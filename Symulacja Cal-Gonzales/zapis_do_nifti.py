import pandas as pd
import numpy as np
import SimpleITK as sitk
from pathlib import Path
import sys

def main():
    print("Wczytywanie danych symulacyjnych (tylko współrzędnych końcowych z modelu Cal-Gonzales)...")
    
    # 1. OPTYMALIZACJA: Wczytujemy TYLKO plik z wynikami końcowymi (xf, yf, zf)
    # Z poprzedniego kroku wiemy, że izotop i średnica są już w tym pliku.
    df_all = pd.read_csv("../dane_symulacja_cal_gonzales/wyniki_symulacji_C-G_1mln-conc.csv")

    # 2. Pobranie wszystkich dostępnych izotopów
    dostepne_izotopy = df_all['Izotop'].unique()
    print(f"Znaleziono izotopy: {dostepne_izotopy}")
    
    # Główna pętla wykonująca się dla każdego izotopu
    for wybrany_izotop in dostepne_izotopy:
        print(f"\n--- Przetwarzanie izotopu: {wybrany_izotop} ---")
        df_izotop = df_all[df_all['Izotop'] == wybrany_izotop].copy()

        if df_izotop.empty:
            print(f"Błąd: Brak danych dla izotopu {wybrany_izotop}. Pomijam.")
            continue

        # 3. Parametry układu i przygotowanie list
        unikalne_srednice = sorted(df_izotop['Srednica_mm'].unique())
        n_sfer = len(unikalne_srednice)
        r_layout = max(unikalne_srednice) * 1.25 

        # Przygotowanie NumPy arrays zamiast Pythonowych list dla maksymalnej wydajności
        total_points = len(df_izotop)
        all_xf = np.zeros(total_points, dtype=np.float32)
        all_yf = np.zeros(total_points, dtype=np.float32)
        all_zf = np.zeros(total_points, dtype=np.float32)
        
        current_idx = 0

        print("Obliczanie położeń i przesunięć sfer...")
        # 4. Aplikowanie przesunięć kołowych TYLKO dla punktów anihilacji
        for i, srednica in enumerate(unikalne_srednice):
            kat = 2 * np.pi * i / n_sfer
            offset_x = r_layout * np.cos(kat)
            offset_y = r_layout * np.sin(kat)
            
            # Maska przyspiesza dobieranie danych i eliminuje kopiowanie tablic
            mask = df_izotop['Srednica_mm'] == srednica
            n_points = mask.sum()
            
            # Bezpośrednie przepisywanie i wektoryzowane przesunięcie
            all_xf[current_idx:current_idx + n_points] = df_izotop.loc[mask, 'xf'].values + offset_x
            all_yf[current_idx:current_idx + n_points] = df_izotop.loc[mask, 'yf'].values + offset_y
            all_zf[current_idx:current_idx + n_points] = df_izotop.loc[mask, 'zf'].values
            
            current_idx += n_points

        # 5. Wokselizacja (tworzenie macierzy 3D)
        print("Generowanie wolumenu NIfTI...")
        n_voxels = 200            
        spacing = 2.5             
        center_idx = n_voxels // 2 

        volume = np.zeros((n_voxels, n_voxels, n_voxels), dtype=np.float32)

        # Przeliczanie milimetrów na indeksy [0-199]
        idx_x = np.round(all_xf / spacing).astype(int) + center_idx
        idx_y = np.round(all_yf / spacing).astype(int) + center_idx
        idx_z = np.round(all_zf / spacing).astype(int) + center_idx

        # Maska ignorująca punkty uciekające poza wymiary matrycy 200x200x200
        valid_mask = (
            (idx_x >= 0) & (idx_x < n_voxels) & 
            (idx_y >= 0) & (idx_y < n_voxels) & 
            (idx_z >= 0) & (idx_z < n_voxels)
        )

        # Zliczanie anihilacji w konkretnych wokselach
        np.add.at(volume, (idx_x[valid_mask], idx_y[valid_mask], idx_z[valid_mask]), 1)

        # 6. Zapis do NIfTI
        # Konwersja osi z (X, Y, Z) na (Z, Y, X) wymaganą przez SimpleITK
        img_sitk = sitk.GetImageFromArray(np.transpose(volume, (2, 1, 0)))
        img_sitk.SetSpacing((spacing, spacing, spacing))

        plik_wyjsciowy = f"../dane_symulacja_cal_gonzales/symulacja_conc_NEMA_{wybrany_izotop}.nii.gz"
        sitk.WriteImage(img_sitk, plik_wyjsciowy)

        print(f"Zapisano NIfTI dla {wybrany_izotop} -> {plik_wyjsciowy}")

    print("\nZakończono przetwarzanie wszystkich izotopów.")
    return 0

if __name__ == "__main__":
    main()