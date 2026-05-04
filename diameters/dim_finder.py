import cv2
import numpy as np
from scipy import ndimage
import glob
import os

def analyze_spheres(input_dir="squares", angles_step=5, threshold_ratio=0.5):
    # Pobieramy wszystkie wygenerowane pliki sfer
    files = glob.glob(os.path.join(input_dir, "sphere_blackbox_*.png"))
    
    # Filtrujemy pliki debugujące, jeśli jakieś zostały z poprzednich uruchomień
    files = [f for f in files if "debug" not in f]
    
    if not files:
        print(f"Brak plików sfer w folderze '{input_dir}'.")
        return

    for roi_path in files:
        img = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
            
        # 1. POPRAWA: Środek masy liczymy na masce, żeby szum z tła go nie przesunął
        _, mask_for_com = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
        center_y, center_x = ndimage.center_of_mass(mask_for_com)
        
        # Zabezpieczenie przed pustym obrazem
        if np.isnan(center_y) or np.isnan(center_x):
            print(f"Pomijam {os.path.basename(roi_path)} - pusta maska.")
            continue
            
        center = (int(center_x), int(center_y))
        
        # 2. POPRAWA: Bierzemy absolutne maksimum z obrazu zamiast z konkretnego piksela
        max_intensity = np.max(img)
        threshold = max_intensity * threshold_ratio
        
        radii = []
        # Upewniamy się, że promień może wyjść poza połowę boku, 
        # jeśli sfera nie jest idealnie wyśrodkowana w ROI
        max_radius = max(img.shape[0], img.shape[1]) 
        
        # Rzutowanie promieni
        for angle in range(0, 360, angles_step):
            theta = np.radians(angle)
            
            # Przeszukiwanie wzdłuż promienia aż do napotkania wartości poniżej progu
            for r in range(1, max_radius):
                x = int(center[0] + r * np.cos(theta))
                y = int(center[1] + r * np.sin(theta))
                
                # Zapobieganie wyjściu poza tablicę obrazu
                if x < 0 or x >= img.shape[1] or y < 0 or y >= img.shape[0]:
                    break
                    
                # Warunek krawędzi sfery (np. spadek poniżej FWHM)
                if img[y, x] < threshold:
                    radii.append(r)
                    break
                    
        if not radii:
            avg_radius = 0
        else:
            avg_radius = np.mean(radii)
            
        diameter = avg_radius * 2
        
        # --- ZAPIS DEBUG ---
        # Tworzymy kolorową kopię, żeby narysować środek i znaleziony okrąg
        debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # Rysowanie krawędzi (czerwona linia)
        cv2.circle(debug_img, center, int(avg_radius), (0, 0, 255), 1)
        # Rysowanie środka (zielona kropka)
        cv2.circle(debug_img, center, 1, (0, 255, 0), -1)
        
        debug_path = roi_path.replace(".png", "_debug.png")
        cv2.imwrite(debug_path, debug_img)
        
        print(f"Plik: {os.path.basename(roi_path):<25} | Środek (X,Y): {center} | Średnica: {diameter:.2f} px")

# Uruchomienie analizy na folderze, do którego wcześniej wycięto kwadraty
analyze_spheres("diameters/squares")