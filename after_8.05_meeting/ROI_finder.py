import cv2
import numpy as np
import os

def extract_spheres_robust(image_path, output_dir, box_size=34, exclusion_radius=12):
    os.makedirs(output_dir, exist_ok=True)
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"[BŁĄD] Brak pliku: {image_path}")
        return

    # Kopia do szukania maksimów (lekko rozmyta, by zniwelować pojedyncze zaszumione piksele)
    search_img = cv2.GaussianBlur(img, (5, 5), 0).astype(np.float32)
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    half_box = box_size // 2
    count = 0
    
    # Szukamy dokładnie 6 maksimów
    for i in range(6):
        # minMaxLoc zwraca najjaśniejszy punkt (max_loc) w obrazie
        _, max_val, _, max_loc = cv2.minMaxLoc(search_img)
        
        # Zabezpieczenie na wypadek szukania w pustym tle
        if max_val < 5:
            break
            
        cx, cy = max_loc
        
        # Wycinamy kwadrat z ORYGINALNEGO obrazu
        x1 = max(0, cx - half_box)
        y1 = max(0, cy - half_box)
        x2 = min(img.shape[1], cx + half_box)
        y2 = min(img.shape[0], cy + half_box)
        
        roi = img[y1:y2, x1:x2]
        
        out_filename = f"{base_name}_sphere_{i+1}.png"
        cv2.imwrite(os.path.join(output_dir, out_filename), roi)
        count += 1
        
        # KLUCZOWE: Wygaszamy znalezioną sferę na czarno w obrazie pomocniczym,
        # aby w następnej pętli algorytm szukał KOLEJNEJ najjaśniejszej sfery.
        cv2.circle(search_img, max_loc, exclusion_radius, 0, -1)

    print(f"Wyodrębniono {count} sfer z pliku: {base_name}")

# --- KONFIGURACJA ŚCIEŻEK ---
# Parametry progów tła (bg_thresh/sphere_thresh) nie są już potrzebne.
files_config = [
    {"in": "after_8.05_meeting/max_intensity_global/nema_max_intensity_slice.png", "out": "./after_8.05_meeting/squares/eksperyment/"},
    {"in": "./after_8.05_meeting/max_intensity_global/max_intensity_slice_global_after_8.05_meeting_18F_cal_gonzales_smoothed_sigma2.png", "out": "./after_8.05_meeting/squares/sym_C-G/18F/"},
    {"in": "./after_8.05_meeting/max_intensity_global/max_intensity_slice_global_after_8.05_meeting_44Sc_cal_gonzales_smoothed_sigma2.png", "out": "./after_8.05_meeting/squares/sym_C-G/44Sc/"},
    {"in": "./after_8.05_meeting/max_intensity_global/max_intensity_slice_global_after_8.05_meeting_18F_CSDA_smoothed_sigma2.png", "out": "./after_8.05_meeting/squares/sym_CSDA/18F/"},
    {"in": "./after_8.05_meeting/max_intensity_global/max_intensity_slice_global_after_8.05_meeting_44Sc_CSDA_smoothed_sigma2.png", "out": "./after_8.05_meeting/squares/sym_CSDA/44Sc/"}
]

# box_size = rozmiar wyciętego kwadratu. exclusion_radius = jak szeroko "gasimy" sferę po znalezieniu (12 pixeli powinno skutecznie oddzielić te dwie zlewające się).
for task in files_config:
    extract_spheres_robust(task["in"], task["out"], box_size=20, exclusion_radius=12)