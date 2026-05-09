import cv2
import numpy as np
from scipy import ndimage
import glob
import os
import csv

def analyze_spheres_subpixel(input_dirs, output_file="./after_8.05_meeting/wyniki_sfer_dim.csv", angles_step=5, threshold_ratio=0.5, pixel_spacing=2.5):
    files = []
    for d in input_dirs:
        # Zintegrowane szukanie plików z nema_ i bez
        found = glob.glob(os.path.join(d, "*max_intensity_slice_*.png"))
        files.extend([f for f in found if "_debug" not in f])
    
    if not files:
        print("Brak plików w podanych ścieżkach.")
        return

    with open(output_file, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Nazwa_pliku", "Srednica_px", "Blad_px", "Srednica_mm", "Blad_mm"]) 

        for roi_path in files:
            img = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
                
            # Powrót do sprawdzonego progu dla środka ciężkości (COM)
            _, mask_for_com = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
            center_y, center_x = ndimage.center_of_mass(mask_for_com)
            
            if np.isnan(center_y) or np.isnan(center_x): continue
                
            # Zabezpieczenie przed pojedynczymi hot-pixelami (zamiast np.max)
            max_intensity = np.percentile(img, 99)
            
            # Powrót do klasycznego wyliczania FWHM, które działało przed rozmyciem
            threshold = max_intensity * threshold_ratio
            
            radii = []
            max_radius = min(img.shape[0], img.shape[1]) / 2.0
            r_vals = np.arange(0, max_radius, 0.2)
            
            for angle in range(0, 360, angles_step):
                theta = np.radians(angle)
                
                x_vals = center_x + r_vals * np.cos(theta)
                y_vals = center_y + r_vals * np.sin(theta)
                
                # astype(float) krytyczne dla ominięcia błędu 'overflow encountered in scalar subtract'
                profile = ndimage.map_coordinates(img, [y_vals, x_vals], order=1, mode='nearest').astype(float)
                
                for i in range(len(profile) - 1):
                    # Usunięto Zabezpieczenie 1, które załamywało się na rozmytych gradientach
                    if profile[i] >= threshold and profile[i+1] < threshold:
                        I1, I2 = profile[i], profile[i+1]
                        r1, r2 = r_vals[i], r_vals[i+1]
                        
                        if I1 != I2:
                            exact_r = r1 + (r2 - r1) * ((threshold - I1) / (I2 - I1))
                            radii.append(exact_r)
                        break
                        
            # Usunięto Zabezpieczenie 2 (odrzucanie za pomocą mediany)
            # --- OBLICZANIE BŁĘDU ---
            if radii and len(radii) > 1:
                std_radius = np.std(radii, ddof=1) # ddof=1 dla odchylenia standardowego próby
            else:
                std_radius = 0
                
            avg_radius = np.mean(radii) if radii else 0
            
            diameter_px = avg_radius * 2
            error_px = std_radius * 2
            
            diameter_mm = diameter_px * pixel_spacing 
            error_mm = error_px * pixel_spacing
            
            file_name = os.path.basename(roi_path)
            
            writer.writerow([file_name, f"{diameter_px:.3f}", f"{error_px:.3f}", f"{diameter_mm:.3f}", f"{error_mm:.3f}"])
            print(f"Zapisano: {file_name} | mm: {diameter_mm:.3f} ± {error_mm:.3f}")
            
            if avg_radius > 0:
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
    "./after_8.05_meeting/squares/eksperyment",
    "./after_8.05_meeting/squares/sym_C-G/18F",
    "./after_8.05_meeting/squares/sym_C-G/44Sc",
    "./after_8.05_meeting/squares/sym_CSDA/18F",
    "./after_8.05_meeting/squares/sym_CSDA/44Sc",
]

analyze_spheres_subpixel(input_directories, pixel_spacing=2.5)