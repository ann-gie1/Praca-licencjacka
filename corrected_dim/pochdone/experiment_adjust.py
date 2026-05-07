import cv2
import numpy as np
from scipy import ndimage
import os
import glob
import csv

def analyze_experimental_spheres(input_dirs, output_file="wyniki_eksperyment.csv", pixel_size_mm=0.332):
    # ==========================================
    # PARAMETRY DO KALIBRACJI
    # ==========================================
    BLUR_2D_KERNEL = (7, 7)    # Rozmycie całego obrazu (usuwa gruboziarnisty szum)
    COM_THRESHOLD = 0.4        # Próg znalezienia środka (40% maksimum obrazu)
    
    STEP_PX = 0.2              # Krok próbkowania w pikselach
    BLUR_1D_SIGMA = 10         # Sigma 10 = rozmycie profilu o 2.0 piksele fizyczne (10 * 0.2)
    
    IGNORE_CENTER_PX = 3.0     # Omiń pierwsze 3 piksele od środka (często zawierają piki szumu)
    IGNORE_EDGE_PX = 2.0       # Omiń 2 piksele na samym brzegu obrazka
    # ==========================================

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

        for image_path in files:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
                
            img_smooth = cv2.GaussianBlur(img, BLUR_2D_KERNEL, 0)
            _, mask_for_com = cv2.threshold(img_smooth, np.max(img_smooth) * COM_THRESHOLD, 255, cv2.THRESH_BINARY)
            center_y, center_x = ndimage.center_of_mass(mask_for_com)
            
            if np.isnan(center_y) or np.isnan(center_x): continue
            
            max_radius = min(img.shape[0], img.shape[1]) / 2.0
            r_vals = np.arange(0, max_radius, STEP_PX)
            radii = []
            
            # Przeliczenie fizycznych odległości na indeksy wektora
            ignore_start_idx = int(IGNORE_CENTER_PX / STEP_PX)
            ignore_end_idx = int(IGNORE_EDGE_PX / STEP_PX)
            
            for angle in range(0, 360, 5):
                theta = np.radians(angle)
                x_vals = center_x + r_vals * np.cos(theta)
                y_vals = center_y + r_vals * np.sin(theta)
                
                profile = ndimage.map_coordinates(img_smooth, [y_vals, x_vals], order=1)
                
                # Uspokojenie profilu - klucz do działania gradientu na zaszumionych danych
                profile_smooth = ndimage.gaussian_filter1d(profile, sigma=BLUR_1D_SIGMA)
                gradient = np.gradient(profile_smooth)
                
                # Zawężamy obszar poszukiwań (bez centrum i bez brzegów ROI)
                if len(gradient) > ignore_start_idx + ignore_end_idx:
                    local_gradient = gradient[ignore_start_idx : -ignore_end_idx if ignore_end_idx > 0 else None]
                    
                    if len(local_gradient) == 0: continue
                        
                    local_edge_idx = np.argmin(local_gradient)
                    edge_idx = ignore_start_idx + local_edge_idx
                    
                    # Interpolacja paraboliczna dla wyniku subpikselowego
                    if 0 < edge_idx < len(r_vals) - 1:
                        y1 = gradient[edge_idx - 1]
                        y2 = gradient[edge_idx]
                        y3 = gradient[edge_idx + 1]
                        
                        mianownik = y1 - 2*y2 + y3
                        if mianownik != 0:
                            p = 0.5 * (y1 - y3) / mianownik
                            exact_r = r_vals[edge_idx] + (p * STEP_PX)
                        else:
                            exact_r = r_vals[edge_idx]
                            
                        radii.append(exact_r)
                        
            avg_radius = np.mean(radii) if radii else 0
            diameter_px = avg_radius * 2
            diameter_mm = diameter_px * pixel_size_mm
            
            file_name = os.path.basename(image_path)
            writer.writerow([file_name, f"{diameter_px:.3f}", f"{diameter_mm:.3f}"])
            print(f"Zapisano: {file_name} | Średnica: {diameter_px:.3f} px | {diameter_mm:.3f} mm")

            # Obrazy kontrolne
            debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            shift = 4
            shifted_center = (int(round(center_x * (1 << shift))), int(round(center_y * (1 << shift))))
            shifted_radius = int(round(avg_radius * (1 << shift)))
            cv2.circle(debug_img, shifted_center, shifted_radius, (0, 0, 255), 1, cv2.LINE_AA, shift)
            cv2.circle(debug_img, shifted_center, 1 << shift, (0, 255, 0), -1, cv2.LINE_AA, shift)
            cv2.imwrite(image_path.replace(".png", "_debug.png"), debug_img)

# Użycie
input_directories = [
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/eksperyment"
]
analyze_experimental_spheres(input_directories)