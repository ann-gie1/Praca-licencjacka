import cv2
import numpy as np
import os

def detect_hough_circles_robust(image_path, output_txt_path):
    img_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img_color = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    if img_gray is None:
        print("Błąd wczytywania obrazu.")
        return

    h, w = img_gray.shape
    
    # Współrzędne środka całego obrazu
    center_x, center_y = w // 2, h // 2
    
    # Maksymalna odległość od środka, w jakiej akceptujemy sfery (odcina brzegi z tekstem)
    # 35% krótszego boku obrazu zazwyczaj obejmuje sam fantom
    max_dist_from_center = min(w, h) * 0.35 

    img_blurred = cv2.medianBlur(img_gray, 7)

    # Dynamiczny dystans między środkami (np. 1/12 szerokości obrazu)
    # Zapobiega nakładaniu się okręgów na dużych sferach niezależnie od rozdzielczości
    dynamic_min_dist = max(40, w // 12)

    circles = cv2.HoughCircles(
        img_blurred, 
        cv2.HOUGH_GRADIENT, 
        dp=1, 
        minDist=dynamic_min_dist, 
        param1=20,       
        param2=30,       # Zwiększono próg (mniej fałszywych okręgów na dużej sferze)
        minRadius=max(5, w // 150), 
        maxRadius=w // 15     
    )

    os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)
    
    with open(output_txt_path, "w", encoding="utf-8") as file:
        if circles is not None:
            circles = np.uint16(np.around(circles))
            valid_circles = []
            
            # Filtrowanie okręgów na podstawie odległości od środka (odrzucanie osi)
            for i in circles[0, :]:
                cx, cy, r = int(i[0]), int(i[1]), int(i[2])
                dist = np.sqrt((cx - center_x)**2 + (cy - center_y)**2)
                
                if dist < max_dist_from_center:
                    valid_circles.append((cx, cy, r))

            file.write(f"Znaleziono sfer: {len(valid_circles)}\n\n")
            print(f"Znaleziono sfer po filtracji: {len(valid_circles)}")
            
            for cx, cy, r in valid_circles:
                cv2.circle(img_color, (cx, cy), r, (0, 0, 255), 2)
                cv2.circle(img_color, (cx, cy), 2, (0, 255, 0), 3)
                
                line = f"Środek: ({cx}, {cy}), Promień: {r} px, Średnica: {r*2} px\n"
                file.write(line)
                print(line.strip())
                
            # Rysowanie okręgu pomocniczego (obszar poszukiwań) - niebieska cienka linia
            cv2.circle(img_color, (center_x, center_y), int(max_dist_from_center), (255, 0, 0), 1)
                
            cv2.imwrite("DEBUG_HOUGH_ROBUST.png", img_color)
        else:
            print("Brak wyników.")

# Wywołanie:
detect_hough_circles_robust(
    image_path="./python_code/nema_max_intensity_slice.png", 
    output_txt_path="C:/Users/agieb/OneDrive/Pulpit/uni_materials/rok III/Praca licencjacka/kody_python/diameters/wyniki_experiment_hough.txt"
)