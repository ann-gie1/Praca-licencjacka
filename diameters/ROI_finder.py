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
    # Odwracamy obraz: czarne tło staje się białe (>15), a jasne osie i sfery stają się czarne
    _, inv_img = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY_INV)
    
    # Znajdujemy największą "plamę", którą będzie nasz centralny czarny kwadrat
    contours_bg, _ = cv2.findContours(inv_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    main_area = max(contours_bg, key=cv2.contourArea)
    
    # Tworzymy czarną maskę i wypełniamy na biało tylko obszar głównego kwadratu
    mask = np.zeros_like(img)
    cv2.drawContours(mask, [main_area], -1, 255, thickness=cv2.FILLED)

    # --- ETAP 2: ZNAJDOWANIE SFER NA MASCE ---
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 40, 255, cv2.THRESH_BINARY)
    
    # Nakładamy maskę (wszystko poza głównym kwadratem staje się czarne)
    masked_thresh = cv2.bitwise_and(thresh, mask)
    
    # ZAPIS DEBUG - sprawdź ten plik, by upewnić się, że widać tylko 6 białych sfer
    cv2.imwrite("DEBUG_MASKED.png", masked_thresh)

    # Szukamy sfer wyłącznie wewnątrz zamaskowanego, czystego obszaru
    contours, _ = cv2.findContours(masked_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    count = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Wystarczy prostsze filtrowanie, ponieważ pozbyliśmy się zewnętrznych szumów
        if w > 10 and h > 10:
            side = max(w, h) + 10
            cx, cy = x + w//2, y + h//2
            
            x1 = max(0, cx - side//2)
            y1 = max(0, cy - side//2)
            x2 = min(img.shape[1], cx + side//2)
            y2 = min(img.shape[0], cy + side//2)
            
            roi = img[y1:y2, x1:x2]
            cv2.imwrite(f"{output_dir}/sphere_blackbox_{count}.png", roi)
            count += 1
            
    print(f"Wyodrębniono {count} sfer.")

extract_spheres("./python_code/nema_max_intensity_slice.png")