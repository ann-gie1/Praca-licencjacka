import cv2
import numpy as np
from scipy import ndimage
import glob
import os
import csv

def analyze_spheres_subpixel(input_dirs, output_dir="./after_8.05_meeting", angles_step=5, pixel_spacing=2.5):
    files = []
    for d in input_dirs:
        found = glob.glob(os.path.join(d, "*max_intensity_slice_*.png"))
        files.extend([f for f in found if "_debug" not in f])
    
    if not files:
        print("Brak plików w podanych ścieżkach.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    # Konfiguracja progów procentowych i tworzenie dla nich plików CSV
    percentages = range(10, 100, 10) # 10, 20, 30, 40, 50, 60, 70, 80, 90
    csv_files = {}
    writers = {}
    
    for pct in percentages:
        out_path = os.path.join(output_dir, f"wyniki_sfer_dim_{pct}.csv")
        f = open(out_path, mode="w", newline='', encoding="utf-8")
        w = csv.writer(f, delimiter=';')
        w.writerow(["Nazwa_pliku", "Srednica_px", "Blad_px", "Srednica_mm", "Blad_mm"]) 
        csv_files[pct] = f
        writers[pct] = w

    dr = 0.2 # Krok na promieniu r_vals
    # Systematyczny błąd interpolacji (szerokość przedziału dr, przyjęto rozkład jednorodny dr / sqrt(12))
    interp_error_px = dr / np.sqrt(12)

    # Parametry do rysowania (subpixel precision)
    shift = 4
    multiplier = (1 << shift)

    try:
        for roi_path in files:
            img = cv2.imread(roi_path, cv2.IMREAD_GRAYSCALE)
            if img is None: continue
                
            _, mask_for_com = cv2.threshold(img, 20, 255, cv2.THRESH_BINARY)
            center_y, center_x = ndimage.center_of_mass(mask_for_com)
            
            if np.isnan(center_y) or np.isnan(center_x): continue
                
            max_intensity = np.percentile(img, 99)
            max_radius_limit = min(img.shape[0], img.shape[1]) / 2.0
            r_vals = np.arange(0, max_radius_limit, dr)
            
            shifted_center = (int(round(center_x * multiplier)), int(round(center_y * multiplier)))

            for pct in percentages:
                threshold_ratio = pct / 100.0
                threshold = max_intensity * threshold_ratio
                
                radii = []
                # Lista punktów krawędzi do narysowania szprych
                edge_points_shifted = []
                
                for angle in range(0, 360, angles_step):
                    theta = np.radians(angle)
                    cos_theta = np.cos(theta)
                    sin_theta = np.sin(theta)
                    
                    x_vals = center_x + r_vals * cos_theta
                    y_vals = center_y + r_vals * sin_theta
                    
                    profile = ndimage.map_coordinates(img, [y_vals, x_vals], order=1, mode='nearest').astype(float)
                    
                    for i in range(len(profile) - 1):
                        if profile[i] >= threshold and profile[i+1] < threshold:
                            I1, I2 = profile[i], profile[i+1]
                            r1, r2 = r_vals[i], r_vals[i+1]
                            
                            if I1 != I2:
                                exact_r = r1 + (r2 - r1) * ((threshold - I1) / (I2 - I1))
                                radii.append(exact_r)
                                
                                # Oblicz punkt krawędzi do rysowania
                                edge_x = center_x + exact_r * cos_theta
                                edge_y = center_y + exact_r * sin_theta
                                edge_points_shifted.append((int(round(edge_x * multiplier)), int(round(edge_y * multiplier))))
                            break
                            
                # --- OBLICZANIE BŁĘDU I ŚREDNICY ---
                if radii and len(radii) > 1:
                    std_radius = np.std(radii, ddof=1)
                    avg_radius = np.mean(radii)
                else:
                    std_radius = 0
                    avg_radius = 0
                    
                total_radius_error = np.sqrt(std_radius**2 + interp_error_px**2) if radii else 0
                    
                diameter_px = avg_radius * 2
                error_px = total_radius_error * 2 
                
                diameter_mm = diameter_px * pixel_spacing 
                error_mm = error_px * pixel_spacing
                
                file_name = os.path.basename(roi_path)
                writers[pct].writerow([file_name, f"{diameter_px:.3f}", f"{error_px:.3f}", f"{diameter_mm:.3f}", f"{error_mm:.3f}"])
                
                # --- RYSOWANIE DEBUG ---
                if avg_radius > 0:
                    debug_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    
                    # 1. Rysuj "szprychy" (promienie) - na niebiesko
                    for pt in edge_points_shifted:
                        cv2.line(debug_img, shifted_center, pt, (255, 0, 0), 1, cv2.LINE_AA, shift)
                    
                    # 2. Rysuj dopasowany okrąg średni - na czerwono
                    shifted_radius = int(round(avg_radius * multiplier))
                    cv2.circle(debug_img, shifted_center, shifted_radius, (0, 0, 255), 1, cv2.LINE_AA, shift)
                    
                    # 3. Rysuj środek - na zielono
                    cv2.circle(debug_img, shifted_center, 1 << shift, (0, 255, 0), -1, cv2.LINE_AA, shift)
                    
                    debug_path = roi_path.replace(".png", f"_debug_{pct}.png")
                    cv2.imwrite(debug_path, debug_img)
                    
            print(f"Zakończono analizę pliku (10-80% + szprychy): {file_name}")

    finally:
        for f in csv_files.values():
            f.close()

# --- KONFIGURACJA ŚCIEŻEK WEJŚCIOWYCH ---
input_directories = [
    "./after_8.05_meeting/squares/eksperyment",
    "./after_8.05_meeting/squares/sym_C-G/18F",
    "./after_8.05_meeting/squares/sym_C-G/44Sc",
    "./after_8.05_meeting/squares/sym_CSDA/18F",
    "./after_8.05_meeting/squares/sym_CSDA/44Sc",
]

analyze_spheres_subpixel(input_directories, pixel_spacing=2.5)