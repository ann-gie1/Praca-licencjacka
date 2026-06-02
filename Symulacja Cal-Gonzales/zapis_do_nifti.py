import pandas as pd
import numpy as np
import SimpleITK as sitk

def main():
    print("Wczytywanie wyników symulacyjnych...")
    df_all = pd.read_csv("../dane_symulacja_cal_gonzales/wyniki_symulacji_c-g_1mln-conc_20626.csv")

    # Słownik precyzyjnych frakcji do pobrania na podstawie ekstrapolacji
    # oraz uwzględnienia całki rozpadu dla t = 217 min.
    frakcje = {
        "18F": {
            10: 1.000,
            13: 0.984,
            17: 0.951,
            22: 0.917,
            28: 0.875,
            37: 0.813
        },
        "44Sc": {
            10: 0.570,
            13: 0.570,
            17: 0.570,
            22: 0.570,
            28: 0.570,
            37: 0.570
        }
    }

    dostepne_izotopy = df_all['Izotop'].unique()
    
    for wybrany_izotop in dostepne_izotopy:
        print(f"\n--- Przetwarzanie izotopu: {wybrany_izotop} ---")
        df_izotop = df_all[df_all['Izotop'] == wybrany_izotop].copy()

        if df_izotop.empty or wybrany_izotop not in frakcje:
            print(f"Brak danych lub współczynników dla {wybrany_izotop}. Pomijam.")
            continue

        unikalne_srednice = sorted(df_izotop['Srednica_mm'].unique())
        n_sfer = len(unikalne_srednice)
        r_layout = max(unikalne_srednice) * 1.25 

        total_points = len(df_izotop)
        all_xf = np.zeros(total_points, dtype=np.float32)
        all_yf = np.zeros(total_points, dtype=np.float32)
        all_zf = np.zeros(total_points, dtype=np.float32)
        
        current_idx = 0
        
        for i, srednica in enumerate(unikalne_srednice):
            if srednica not in frakcje[wybrany_izotop]:
                continue
                
            kat = 2 * np.pi * i / n_sfer
            offset_x = r_layout * np.cos(kat)
            offset_y = r_layout * np.sin(kat)
            
            mask = df_izotop['Srednica_mm'] == srednica
            ułamek = frakcje[wybrany_izotop][srednica]
            
            # Pobieranie właściwej proporcji (zawsze inne zdarzenia - brak ziarna)
            df_sfera = df_izotop[mask].sample(frac=ułamek)
            n_points = len(df_sfera)
            
            print(f"Sfera {srednica}mm: Pobrane {ułamek*100:.1f}% dostępnych zdarzeń -> {n_points}")
            
            all_xf[current_idx:current_idx + n_points] = df_sfera['xf'].values + offset_x
            all_yf[current_idx:current_idx + n_points] = df_sfera['yf'].values + offset_y
            all_zf[current_idx:current_idx + n_points] = df_sfera['zf'].values
            
            current_idx += n_points

        all_xf = all_xf[:current_idx]
        all_yf = all_yf[:current_idx]
        all_zf = all_zf[:current_idx]

        print(f"Generowanie wolumenu NIfTI z łącznej liczby {current_idx} punktów...")
        n_voxels = 200            
        spacing = 2.5             
        center_idx = n_voxels // 2 

        volume = np.zeros((n_voxels, n_voxels, n_voxels), dtype=np.float32)

        idx_x = np.round(all_xf / spacing).astype(int) + center_idx
        idx_y = np.round(all_yf / spacing).astype(int) + center_idx
        idx_z = np.round(all_zf / spacing).astype(int) + center_idx

        valid_mask = (
            (idx_x >= 0) & (idx_x < n_voxels) & 
            (idx_y >= 0) & (idx_y < n_voxels) & 
            (idx_z >= 0) & (idx_z < n_voxels)
        )

        np.add.at(volume, (idx_x[valid_mask], idx_y[valid_mask], idx_z[valid_mask]), 1)

        img_sitk = sitk.GetImageFromArray(np.transpose(volume, (2, 1, 0)))
        img_sitk.SetSpacing((spacing, spacing, spacing))

        plik_wyjsciowy = f"../dane_symulacja_cal_gonzales/symulacja_conc_correct_NEMA_{wybrany_izotop}_20626.nii.gz"
        sitk.WriteImage(img_sitk, plik_wyjsciowy)

        print(f"Zapisano NIfTI dla {wybrany_izotop} -> {plik_wyjsciowy}")

    print("\nZakończono generowanie obu plików NIfTI.")
    return 0

if __name__ == "__main__":
    main()