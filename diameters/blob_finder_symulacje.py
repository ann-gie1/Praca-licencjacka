import cv2
import numpy as np
import os
import csv

def detect_spheres_intelligent_batch(image_paths, output_csv_path):
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    with open(output_csv_path, "w", encoding="utf-8", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Folder", "Nazwa pliku", "Liczba sfer", "Środek X", "Środek Y", "Promień (px)", "Średnica (px)"])
        
        for image_path in image_paths:
            folder_name = os.path.basename(os.path.dirname(image_path))
            base_name = os.path.basename(image_path)
            unique_prefix = f"{folder_name}_{base_name}" if folder_name else base_name
            
            img_color = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if img_color is None:
                print(f"Błąd wczytywania: {image_path}")
                continue

            img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
            h, w = img_gray.shape
            
            # Geometria wykresu
            center_x, center_y = w // 2, h // 2
            max_dist = min(w, h) * 0.40 
            
            # KROK 1: Izolacja
            mask = np.zeros_like(img_gray)
            cv2.circle(mask, (center_x, center_y), int(max_dist), 255, -1)
            
            img_blurred = cv2.GaussianBlur(img_gray, (5, 5), 0)
            masked_img = cv2.bitwise_and(img_blurred, img_blurred, mask=mask)
            
            # KROK 2: Inteligentny próg
            max_intensity = np.max(masked_img)
            dynamic_thresh = max(30, max_intensity * 0.4) 
            
            _, binary = cv2.threshold(masked_img, dynamic_thresh, 255, cv2.THRESH_BINARY)
            
            # KROK 3: Wykrywanie konturów
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            valid_circles = []
            for cnt in contours:
                (cx, cy), r = cv2.minEnclosingCircle(cnt)
                if 2.0 < r < w / 10.0:
                    valid_circles.append((float(cx), float(cy), float(r)))
            
            num_spheres = len(valid_circles)
            print(f"[{unique_prefix}] Znaleziono sfer: {num_spheres}")
            
            if num_spheres > 0:
                for cx, cy, r in valid_circles:
                    cv2.circle(img_color, (int(cx), int(cy)), int(r), (0, 0, 255), 2)
                    cv2.circle(img_color, (int(cx), int(cy)), 2, (0, 255, 0), 3)
                    csv_writer.writerow([folder_name, base_name, num_spheres, round(cx, 3), round(cy, 3), round(r, 3), round(r*2, 3)])
            else:
                csv_writer.writerow([folder_name, base_name, 0, "Brak", "Brak", "Brak", "Brak"])
                
            # Zapis zdjęcia wynikowego
            cv2.circle(img_color, (center_x, center_y), int(max_dist), (255, 0, 0), 1)
            cv2.imwrite(f"DEBUG_CONTOURS_{unique_prefix}", img_color)

# --- WYWOŁANIE ---
moje_zdjecia = [
    "./from_server/dane_symulacja_cal_gonzales/symulacja_max_intensity_slice_symulacja_conc_NEMA_18F.png",
    "./from_server/dane_symulacja_cal_gonzales/symulacja_max_intensity_slice_symulacja_conc_NEMA_44Sc.png",
    "./from_server/dane_symulacja_CSDA/symulacja_max_intensity_slice_symulacja_conc_NEMA_18F.png",
    "./from_server/dane_symulacja_CSDA/symulacja_max_intensity_slice_symulacja_conc_NEMA_44Sc.png"
]

plik_wynikowy_csv = "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/wyniki_experiment_contours.csv"

detect_spheres_intelligent_batch(moje_zdjecia, plik_wynikowy_csv)