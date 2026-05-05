import cv2
import numpy as np
import os
import csv

def detect_hough_special_case(image_path, output_csv_path):
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    
    # DODANE: Stała do konwersji
    PIXEL_TO_MM = 0.332005312085
    
    with open(output_csv_path, "w", encoding="utf-8", newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        # ZMIENIONE: Dodano kolumnę "Średnica (mm)"
        csv_writer.writerow(["Nazwa pliku", "Liczba sfer", "Środek X", "Środek Y", "Promień (px)", "Średnica (px)", "Średnica (mm)"])
        
        base_name = os.path.basename(image_path)
        
        img_color = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if img_color is None:
            print(f"Błąd wczytywania obrazu: {image_path}")
            return

        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        h, w = img_gray.shape
        center_x, center_y = w // 2, h // 2
        
        max_dist_from_center = min(w, h) * 0.35 
        
        # Powrót do silnego rozmycia z pierwszego kodu
        img_blurred = cv2.medianBlur(img_gray, 7)
        dynamic_min_dist = max(40, w // 12)

        # Oryginalne ustawienia Hougha z minimalną korektą param2
        circles = cv2.HoughCircles(
            img_blurred, 
            cv2.HOUGH_GRADIENT, 
            dp=1, 
            minDist=dynamic_min_dist, 
            param1=20,       
            param2=20,       # Obniżono z 30 na 24, aby spróbować złapać 6 sferę
            minRadius=max(5, w // 150), 
            maxRadius=w // 15     
        )
        
        if circles is not None:
            # Zachowujemy pełną precyzję float z Hougha do zapisu
            circles_float = circles[0, :]
            valid_circles = []
            
            for i in circles_float:
                cx, cy, r = i[0], i[1], i[2]
                dist = np.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                
                if dist < max_dist_from_center:
                    valid_circles.append((cx, cy, r))

            num_spheres = len(valid_circles)
            print(f"[{base_name}] Znaleziono sfer: {num_spheres}")
            
            if num_spheres > 0:
                for cx, cy, r in valid_circles:
                    cv2.circle(img_color, (int(cx), int(cy)), int(r), (0, 0, 255), 2)
                    cv2.circle(img_color, (int(cx), int(cy)), 2, (0, 255, 0), 3)
                    
                    # DODANE: Liczenie średnicy w mm
                    diameter_mm = (r * 2) * PIXEL_TO_MM
                    
                    # ZMIENIONE: Zapis nowej wartości do CSV
                    csv_writer.writerow([base_name, num_spheres, round(cx, 3), round(cy, 3), round(r, 3), round(r*2, 3), round(diameter_mm, 3)])
            else:
                # ZMIENIONE: Dodano "Brak" dla nowej kolumny
                csv_writer.writerow([base_name, 0, "Brak", "Brak", "Brak", "Brak", "Brak"])
                
            cv2.circle(img_color, (center_x, center_y), int(max_dist_from_center), (255, 0, 0), 1)
            cv2.imwrite(f"DEBUG_HOUGH_SPECIAL_{base_name}", img_color)
            
        else:
            print(f"[{base_name}] Brak wyników.")
            # ZMIENIONE: Dodano "Brak" dla nowej kolumny
            csv_writer.writerow([base_name, 0, "Brak", "Brak", "Brak", "Brak", "Brak"])

# --- WYWOŁANIE ---
zdjecie = "./python_code/nema_max_intensity_slice.png" 
plik_wynikowy_csv = "C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/wyniki_hough_special.csv"

detect_hough_special_case(zdjecie, plik_wynikowy_csv)