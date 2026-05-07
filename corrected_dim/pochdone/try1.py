import cv2
import numpy as np
from scipy import ndimage
import glob
import os
import csv

def analyze_spheres_gradient(input_dirs, output_file="./corrected_dim/pochdone/wyniki_gradient.csv", pixel_size_mm=0.332):

    files = []
    for d in input_dirs:
        found = glob.glob(os.path.join(d, "sphere_*.png"))
        files.extend([f for f in found if "_debug" not in f])
    
    if not files:
        print("Brak plików w podanych ścieżkach.")
        return

    with open(output_file, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Nazwa_pliku", "Srednica_px", "Srednica_mm"]) 

        for roi_path in files:
            img = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
            
            # Wygładzanie - kluczowe dla prawidłowego działania gradientu
            img_smooth = cv2.GaussianBlur(img, (3, 3), 0)
                
            _, mask_for_com = cv2.threshold(img_smooth, np.max(img_smooth)*0.2, 255, cv2.THRESH_BINARY)
            center_y, center_x = ndimage.center_of_mass(mask_for_com)
            
            if np.isnan(center_y) or np.isnan(center_x): continue
            
            max_radius = min(img.shape[0], img.shape[1]) / 2.0
            r_vals = np.arange(0, max_radius, 0.2)
            radii = []
            
            for angle in range(0, 360, 5):
                theta = np.radians(angle)
                x_vals = center_x + r_vals * np.cos(theta)
                y_vals = center_y + r_vals * np.sin(theta)
                
                profile = ndimage.map_coordinates(img_smooth, [y_vals, x_vals], order=1)
                # Obliczenie pochodnej z profilu
                gradient = np.gradient(profile)
                
                # Szukamy najsilniejszego spadku (minimum pochodnej - dyskretne)
                edge_idx = np.argmin(gradient)
                
                # Zabezpieczenie przed błędami na krawędzi wektora
                if 0 < edge_idx < len(r_vals) - 1:
                    # --- DOKŁADNOŚĆ SUBPIKSELOWA (Interpolacja Paraboliczna) ---
                    y1 = gradient[edge_idx - 1]
                    y2 = gradient[edge_idx]
                    y3 = gradient[edge_idx + 1]
                    
                    mianownik = y1 - 2*y2 + y3
                    
                    if mianownik != 0:
                        # p to ułamkowe przesunięcie indeksu (wartość od -0.5 do 0.5)
                        p = 0.5 * (y1 - y3) / mianownik
                        
                        # Pobieramy fizyczny krok wektora promieni (wynosi 0.2)
                        krok = r_vals[1] - r_vals[0] 
                        
                        # Wyliczamy dokładny promień z ułamkowym przesunięciem
                        exact_r = r_vals[edge_idx] + (p * krok)
                    else:
                        exact_r = r_vals[edge_idx]
                        
                    radii.append(exact_r)
                
                        
            avg_radius = np.mean(radii) if radii else 0
            diameter_px = avg_radius * 2
            diameter_mm = diameter_px * pixel_size_mm
            
            file_name = os.path.basename(roi_path)
            writer.writerow([file_name, f"{diameter_px:.3f}", f"{diameter_mm:.3f}"])
            print(f"Zapisano: {file_name} | Średnica: {diameter_px:.3f} px | {diameter_mm:.3f} mm")


input_directories = [
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/eksperyment",
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/Cal-gonzales",
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/CSDA"
]

analyze_spheres_gradient(input_directories)