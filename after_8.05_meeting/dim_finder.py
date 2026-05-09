import cv2
import numpy as np
from scipy import ndimage
import glob
import os
import csv

def analyze_spheres_subpixel(input_dirs, output_file="./after_8.05_meeting/wyniki_sfer_dim.csv", angles_step=5, threshold_ratio=0.5, pixel_spacing=2.5):

    #Kalkulator średnic sfer z zabezpieczeniem przed wpływem sąsiadujących sfer (spill-over).
    #pixel_spacing: rozmiar piksela w milimetrach (domyślnie 2.5 mm).
    files = []
    for d in input_dirs:
        found = glob.glob(os.path.join(d, "max_intensity_slice_*.png")) + \
        glob.glob(os.path.join(d, "nema_max_intensity_slice_*.png"))
        files.extend([f for f in found if "_debug" not in f])
    
    if not files:
        print("Brak plików w podanych ścieżkach.")
        return

    # Otwieramy plik CSV do zapisu z nową kolumną dla milimetrów
    with open(output_file, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Nazwa_pliku", "Srednica_px", "Srednica_mm"]) 

        for roi_path in files:
            img = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
                
            # Zabezpieczenie przed niezerowym tłem z obrazów z nałożoną kolorówką
            bg_val = np.min(img)
            _, mask_for_com = cv2.threshold(img, bg_val + 10, 255, cv2.THRESH_BINARY)
            center_y, center_x = ndimage.center_of_mass(mask_for_com)
            
            if np.isnan(center_y) or np.isnan(center_x): continue
                
            max_intensity = np.percentile(img, 99)
            # Rzeczywisty próg wyliczany od najniższej wartości tła, a nie od sztywnego zera
            threshold = bg_val + (max_intensity - bg_val) * threshold_ratio
            
            radii = []
            max_radius = min(img.shape[0], img.shape[1]) / 2.0
            r_vals = np.arange(0, max_radius, 0.2)
            
            for angle in range(0, 360, angles_step):
                theta = np.radians(angle)
                
                x_vals = center_x + r_vals * np.cos(theta)
                y_vals = center_y + r_vals * np.sin(theta)
                
                profile = ndimage.map_coordinates(img, [y_vals, x_vals], order=1, mode='nearest').astype(float)
                
                for i in range(len(profile) - 1):
                    # ZABEZPIECZENIE 1: Odrzucanie promienia celującego w sąsiada
                    # Zmiana: Tolerancja na szum to 10% max_intensity, a nie 3 poziomy szarości
                    noise_margin = max_intensity * 0.1 
                    if profile[i] < max_intensity * 0.8 and profile[i+1] > profile[i] + noise_margin:
                        break # Porzucamy ten kąt
                        
                    # Klasyczne szukanie momentu przecięcia progu (FWHM)
                    if profile[i] >= threshold and profile[i+1] < threshold:
                        I1, I2 = profile[i], profile[i+1]
                        r1, r2 = r_vals[i], r_vals[i+1]
                        
                        if I1 != I2:
                            exact_r = r1 + (r2 - r1) * ((threshold - I1) / (I2 - I1))
                            radii.append(exact_r)
                        break
                        
            # ZABEZPIECZENIE 2: Odrzucanie anomalii (Outlier Rejection)
            # Kąty, które uciekły w "ogon" będą znacznie różnić się długością
            if radii:
                median_r = np.median(radii)
                # Odrzucamy wszystko, co różni się o ponad 30% od mediany
                valid_radii = [r for r in radii if abs(r - median_r) < 0.3 * median_r]
            else:
                valid_radii = []

            avg_radius = np.mean(valid_radii) if valid_radii else 0
            diameter_px = avg_radius * 2
            diameter_mm = diameter_px * pixel_spacing # Zamiana na milimetry
            
            file_name = os.path.basename(roi_path)
            
            writer.writerow([file_name, f"{diameter_px:.3f}", f"{diameter_mm:.3f}"])
            print(f"Zapisano: {file_name} | px: {diameter_px:.3f} | mm: {diameter_mm:.3f}")
            
            # Generowanie pliku debug z wizualizacją
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
# Edytuj te foldery, aby wskazywały miejsca z wyciętymi ROI
input_directories = [
    "./after_8.05_meeting/squares/eksperyment",
    "./after_8.05_meeting/squares/sym_C-G/18F",
    "./after_8.05_meeting/squares/sym_C-G/44Sc",
    "./after_8.05_meeting/squares/sym_CSDA/18F",
    "./after_8.05_meeting/squares/sym_CSDA/44Sc",
]

# Uruchomienie kalkulatora z przelicznikiem 2.5 mm na piksel
analyze_spheres_subpixel(input_directories, pixel_spacing=2.5)