import cv2
import numpy as np
import os

def extract_spheres_robust(image_path, output_dir, box_size=34, exclusion_radius=12):
    os.makedirs(output_dir, exist_ok=True)
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[BŁĄD] Brak pliku: {image_path}")
        return

    search_img = cv2.GaussianBlur(img, (5, 5), 0).astype(np.float32)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    half_box = box_size // 2
    
    extracted_spheres = []
    
    # Szukamy do 6 maksimów i zapisujemy je do listy tymczasowej
    for _ in range(6):
        _, max_val, _, max_loc = cv2.minMaxLoc(search_img)
        
        if max_val < 5:
            break
            
        cx, cy = max_loc
        
        x1 = max(0, cx - half_box)
        y1 = max(0, cy - half_box)
        x2 = min(img.shape[1], cx + half_box)
        y2 = min(img.shape[0], cy + half_box)
        
        roi = img[y1:y2, x1:x2]
        
        # Obliczamy "masę" sfery jako sumę wartości wszystkich jej pikseli
        sphere_mass = np.sum(roi)
        extracted_spheres.append((sphere_mass, roi))
        
        cv2.circle(search_img, max_loc, exclusion_radius, 0, -1)

    # Sortowanie sfer malejąco na podstawie obliczonej sumy intensywności (od największej do najmniejszej)
    extracted_spheres.sort(key=lambda x: x[0], reverse=True)

    # Zapis już posortowanych wyników
    for i, (_, roi) in enumerate(extracted_spheres):
        out_filename = f"{base_name}_sphere_{i+1}.png"
        cv2.imwrite(os.path.join(output_dir, out_filename), roi)

    print(f"Wyodrębniono {len(extracted_spheres)} sfer z pliku: {base_name} (posortowane po rozmiarze)")

# --- KONFIGURACJA ŚCIEŻEK ---
files_config = [
    {"in": "after_8.05_meeting/max_intensity_global/nema_max_intensity_slice.png", "out": "./after_8.05_meeting/squares_correct_smoothing/eksperyment/"},
    {"in": "./after_8.05_meeting/max_intensity_slice_global_nii files_18F_cal_gonzales_smoothed_fwhm2.png", "out": "./after_8.05_meeting/squares_correct_smoothing/cal-gonzales/18F/"},
    {"in": "./after_8.05_meeting/max_intensity_slice_global_nii files_44Sc_cal_gonzales_smoothed_fwhm2.png", "out": "./after_8.05_meeting/squares_correct_smoothing/cal-gonzales/44Sc/"},
    {"in": "./after_8.05_meeting/max_intensity_slice_global_nii files_18F_CSDA_smoothed_fwhm2.png", "out": "./after_8.05_meeting/squares_correct_smoothing/CSDA/18F/"},
    {"in": "./after_8.05_meeting/max_intensity_slice_global_nii files_44Sc_CSDA_smoothed_fwhm2.png", "out": "./after_8.05_meeting/squares_correct_smoothing/CSDA/44Sc/"}
]

for task in files_config:
    extract_spheres_robust(task["in"], task["out"], box_size=20, exclusion_radius=12)