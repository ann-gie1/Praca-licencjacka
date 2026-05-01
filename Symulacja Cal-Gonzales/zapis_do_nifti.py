import pandas as pd
import numpy as np
import SimpleITK as sitk
from pathlib import Path
import sys

def main():
    print("Wczytywanie danych symulacyjnych...")
    
    # 1. Wczytanie danych
    df = pd.read_csv("../dane_symulacja_cal_gonzales/Generacja_danych_c-g_1mln-conc.csv")
    df1 = pd.read_csv("../dane_symulacja_cal_gonzales/wyniki_symulacji_C-G_1mln-conc.csv")

    df_all = pd.merge(df, df1, on='Index', suffixes=('', '_wyniki'))

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

        all_xf = []
        all_yf = []
        all_zf = []

        print("Obliczanie położeń i przesunięć sfer...")
        # 4. Aplikowanie przesunięć kołowych TYLKO dla punktów anihilacji
        for i, srednica in enumerate(unikalne_srednice):
            kat = 2 * np.pi * i / n_sfer
            offset_x = r_layout * np.cos(kat)
            offset_y = r_layout * np.sin(kat)
            
            df_sfera = df_izotop[df_izotop['Srednica_mm'] == srednica]
            
            # Zbieramy współrzędne anihilacji i przesuwamy
            all_xf.extend((df_sfera['xf'] + offset_x).tolist())
            all_yf.extend((df_sfera['yf'] + offset_y).tolist())
            all_zf.extend((df_sfera['zf']).tolist())  # Z zostaje bez zmian

        # 5. Wokselizacja (tworzenie macierzy 3D)
        print("Generowanie wolumenu NIfTI...")
        n_voxels = 200            
        spacing = 2.5             
        center_idx = n_voxels // 2 

        volume = np.zeros((n_voxels, n_voxels, n_voxels), dtype=np.float32)

        x_arr = np.array(all_xf)
        y_arr = np.array(all_yf)
        z_arr = np.array(all_zf)

        # Przeliczanie milimetrów na indeksy [0-199]
        idx_x = np.round(x_arr / spacing).astype(int) + center_idx
        idx_y = np.round(y_arr / spacing).astype(int) + center_idx
        idx_z = np.round(z_arr / spacing).astype(int) + center_idx

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