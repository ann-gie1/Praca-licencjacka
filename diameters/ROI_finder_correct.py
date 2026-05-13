import cv2
import numpy as np
import os

def extract_spheres_robust(image_path, output_dir, box_size=34, exclusion_radius=12):
    os.makedirs(output_dir, exist_ok=True)
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[BŁĄD] Brak pliku: {image_path}")
        return

    # Kopia do szukania maksimów (rozmyta)
    search_img = cv2.GaussianBlur(img, (5, 5), 0).astype(np.float32)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    half_box = box_size // 2
    
    detected_spheres = []
    
    # 1. Znajdź wycinki wszystkich sfer (lokalizacja tak samo jak do tej pory)
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
        
        # 2. Oblicz fizyczny "rozmiar" (masa) sfery wewnątrz wycinka.
        # Bierzemy sumę pikseli powyżej 20% lokalnego maksimum, żeby odciąć ewentualne tło w rogu kwadratu.
        roi_max = np.max(roi)
        size_score = np.sum(roi[roi > (roi_max * 0.2)])
        
        detected_spheres.append({
            'roi': roi,
            'score': size_score
        })
        
        # Wygaszamy
        cv2.circle(search_img, max_loc, exclusion_radius, 0, -1)

    # 3. Posortuj sfery malejąco względem ich masy (największa na początku)
    detected_spheres.sort(key=lambda x: x['score'], reverse=True)

    # 4. Zapisz do plików z narzuconą kolejnością
    for i, sphere in enumerate(detected_spheres):
        out_filename = f"{base_name}_sphere_{i+1}.png"
        cv2.imwrite(os.path.join(output_dir, out_filename), sphere['roi'])

    print(f"Wyodrębniono {len(detected_spheres)} sfer (od największej do najmniejszej) z pliku: {base_name}")

# --- KONFIGURACJA ŚCIEŻEK ---
files_config = [
    {"in": "./diameters/max_intensity_slice_global_cal_gonzales_18F.png", "out": "./diameters/squares_true/sym_C-G/18F/"},
    {"in": "./diameters/max_intensity_slice_global_cal_gonzales_44Sc.png", "out": "./diameters/squares_true/sym_C-G/44Sc/"},
    {"in": "./diameters/max_intensity_slice_global_CSDA_18F.png", "out": "./diameters/squares_true/sym_CSDA/18F/"},
    {"in": "./diameters/max_intensity_slice_global_CSDA_44Sc.png", "out": "./diameters/squares_true/sym_CSDA/44Sc/"}
]

for task in files_config:
    extract_spheres_robust(task["in"], task["out"], box_size=22, exclusion_radius=18)