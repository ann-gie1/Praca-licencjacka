import cv2
import numpy as np
from scipy import ndimage
import glob
import os
import csv

def analyze_spheres_subpixel(input_dirs, output_file="wyniki_sfer.csv", angles_step=5, threshold_ratio=0.5, pixel_size_mm=0.332005312085):
    files = []
    for d in input_dirs:
        found = glob.glob(os.path.join(d, "sphere_*.png"))
        files.extend([f for f in found if "_debug" not in f])
    
    if not files:
        print("Brak plików w podanych ścieżkach.")
        return

    # Otwieramy plik CSV do zapisu
    with open(output_file, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        # Dodano nową kolumnę dla średnicy w milimetrach
        writer.writerow(["Nazwa_pliku", "Srednica_px", "Srednica_mm"]) 

        for roi_path in files:
            img = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
                
            _, mask_for_com = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
            center_y, center_x = ndimage.center_of_mass(mask_for_com)
            
            if np.isnan(center_y) or np.isnan(center_x): continue
                
            max_intensity = np.max(img)
            threshold = max_intensity * threshold_ratio
            
            radii = []
            max_radius = min(img.shape[0], img.shape[1]) / 2.0
            r_vals = np.arange(0, max_radius, 0.2)
            
            for angle in range(0, 360, angles_step):
                theta = np.radians(angle)
                
                x_vals = center_x + r_vals * np.cos(theta)
                y_vals = center_y + r_vals * np.sin(theta)
                
                profile = ndimage.map_coordinates(img, [y_vals, x_vals], order=1, mode='nearest')
                
                for i in range(len(profile) - 1):
                    if profile[i] >= threshold and profile[i+1] < threshold:
                        I1, I2 = profile[i], profile[i+1]
                        r1, r2 = r_vals[i], r_vals[i+1]
                        
                        exact_r = r1 + (r2 - r1) * ((threshold - I1) / (I2 - I1))
                        radii.append(exact_r)
                        break
                        
            avg_radius = np.mean(radii) if radii else 0
            
            # --- WYLICZENIA ŚREDNIC ---
            diameter_px = avg_radius * 2
            diameter_mm = diameter_px * pixel_size_mm
            
            file_name = os.path.basename(roi_path)
            
            # Zapis do CSV i wypisanie w konsoli
            writer.writerow([file_name, f"{diameter_px:.3f}", f"{diameter_mm:.3f}"])
            print(f"Zapisano: {file_name:<40} | Środek(X,Y): ({center_x:>6.2f}, {center_y:>6.2f}) | Średnica: {diameter_px:>6.3f} px | {diameter_mm:>6.3f} mm")
            
            # Zapis obrazków poglądowych
            debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            shift = 4
            shifted_center = (int(round(center_x * (1 << shift))), int(round(center_y * (1 << shift))))
            shifted_radius = int(round(avg_radius * (1 << shift)))
            
            cv2.circle(debug_img, shifted_center, shifted_radius, (0, 0, 255), 1, cv2.LINE_AA, shift)
            cv2.circle(debug_img, shifted_center, 1 << shift, (0, 255, 0), -1, cv2.LINE_AA, shift)
            
            debug_path = roi_path.replace(".png", "_debug.png")
            cv2.imwrite(debug_path, debug_img)

# --- KONFIGURACJA ŚCIEŻEK WEJŚCIOWYCH ---
input_directories = [
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/eksperyment",
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/Cal-gonzales",
    "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/CSDA"
]

# Uruchomienie z domyślnym przelicznikiem (1 px = 0.332005312085 mm)
analyze_spheres_subpixel(input_directories)