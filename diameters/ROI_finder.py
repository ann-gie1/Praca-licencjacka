import cv2
import numpy as np
import os

def extract_spheres(image_path, output_dir="squares"):
    os.makedirs(output_dir, exist_ok=True)
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Błąd wczytywania pliku: {image_path}")
        return

    # --- ETAP 1: TWORZENIE MASKI ---
    _, inv_img = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY_INV)
    contours_bg, _ = cv2.findContours(inv_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    main_area = max(contours_bg, key=cv2.contourArea)
    
    mask = np.zeros_like(img)
    cv2.drawContours(mask, [main_area], -1, 255, thickness=cv2.FILLED)

    # --- ETAP 2: ZNAJDOWANIE SFER NA MASCE ---
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 40, 255, cv2.THRESH_BINARY)
    masked_thresh = cv2.bitwise_and(thresh, mask)
    
    # Pobranie nazwy pliku bez rozszerzenia, aby nie nadpisywać plików
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Zapis pliku DEBUG z unikalną nazwą w folderze docelowym
    cv2.imwrite(f"{output_dir}/DEBUG_MASKED_{base_name}.png", masked_thresh)

    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    count = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w > 10 and h > 10:
            side = max(w, h) + 10
            cx, cy = x + w//2, y + h//2
            
            x1 = max(0, cx - side//2)
            y1 = max(0, cy - side//2)
            x2 = min(img.shape[1], cx + side//2)
            y2 = min(img.shape[0], cy + side//2)
            
            roi = img[y1:y2, x1:x2]
            # Zapis wyciętych sfer z unikalną nazwą
            cv2.imwrite(f"{output_dir}/sphere_{base_name}_{count}.png", roi)
            count += 1
            
    print(f"Wyodrębniono {count} sfer z pliku {image_path}.")

# --- KONFIGURACJA PLIKÓW I ŚCIEŻEK ZAPISU ---
# Zmień poniższe stringi na właściwe ścieżki do swoich plików PNG
tasks = [
    ("./python_code/nema_max_intensity_slice.png", "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/eksperyment"), # Plik 1 -> Ścieżka 1
    ("./from_server/dane_symulacja_cal_gonzales/symulacja_max_intensity_slice_symulacja_conc_NEMA_44Sc.png", "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/Cal-gonzales"), # Plik 2 -> Ścieżka 2
    ("./from_server/dane_symulacja_cal_gonzales/symulacja_max_intensity_slice_symulacja_conc_NEMA_18F.png", "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/Cal-gonzales"), # Plik 3 -> Ścieżka 2
    ("./from_server/dane_symulacja_CSDA/symulacja_max_intensity_slice_symulacja_conc_NEMA_44Sc.png", "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/CSDA"), # Plik 4 -> Ścieżka 3
    ("./from_server/dane_symulacja_CSDA/symulacja_max_intensity_slice_symulacja_conc_NEMA_18F.png", "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/squares/CSDA")  # Plik 5 -> Ścieżka 3
]

# Przetwarzanie w pętli
for img_path, out_dir in tasks:
    extract_spheres(img_path, output_dir=out_dir)