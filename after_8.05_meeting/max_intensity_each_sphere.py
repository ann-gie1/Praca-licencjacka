import SimpleITK as sitk
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def main():
    # --- KONFIGURACJA ŚCIEŻEK ---
    # Plik maski NEMA (musi mieć te same wymiary co pliki badane, np. 200x200x200)
    # Zakładamy, że sfery mają wartości od 1 do 6.
    sciezka_maski = "./after_8.05_meeting/maski_NEMA.nii.gz"
    
    # 5 plików wejściowych
    pliki_wejsciowe = [
        "./python_code/nema_volume.nii.gz", # Indeks 0
        "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_18F_cal_gonzales_smoothed_sigma2.nii.gz", # Indeks 1
        "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_44Sc_cal_gonzales_smoothed_sigma2.nii.gz", #index2
        "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_18F_CSDA_smoothed_sigma2.nii.gz", # Indeks 3
        "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_44Sc_CSDA_smoothed_sigma2.nii.gz"  # Indeks 4
    ]

    # Mapowanie indeksu pliku wejściowego na ścieżkę wyjściową
    katalogi_wyjsciowe = {
        0: "./after_8.05_meeting/max_intensity_per_sphere_experiment", # Dla pliku 1
        1: "./after_8.05_meeting/Max_intensity_per_sphere_cal-gonzales", # Dla pliku 2
        2: "./after_8.05_meeting/Max_intensity_per_sphere_cal-gonzales", # Dla pliku 3
        3: "./after_8.05_meeting/max_intensity_per_sphere_CSDA", # Dla pliku 4
        4: "./after_8.05_meeting/max_intensity_per_sphere_CSDA"  # Dla pliku 5
    }

    # --- WERYFIKACJA MASKI ---
    if not os.path.exists(sciezka_maski):
        print(f"Błąd: Nie znaleziono pliku maski: {sciezka_maski}")
        return 1

    mask_sitk = sitk.ReadImage(sciezka_maski)
    mask_vol = sitk.GetArrayFromImage(mask_sitk)
    
    # Rozpoznanie unikalnych wartości w masce (z pominięciem zera - tła)
    id_sfer = np.unique(mask_vol)[1:] 
    if len(id_sfer) != 6:
        print(f"Ostrzeżenie: Znaleziono {len(id_sfer)} etykiet w masce, a spodziewano się 6.")

    # --- PRZETWARZANIE ---
    for idx, input_nifti in enumerate(pliki_wejsciowe):
        if not os.path.exists(input_nifti):
            print(f"Pominięto (brak pliku): {input_nifti}")
            continue

        katalog_out = katalogi_wyjsciowe[idx]
        os.makedirs(katalog_out, exist_ok=True) # Tworzy katalog, jeśli nie istnieje

        nazwa_pliku = os.path.basename(input_nifti)
        izotop = nazwa_pliku.replace("symulacja_conc_correct_NEMA_", "").replace(".nii.gz", "")
        
        # Wyciąganie tagu symulacji z nazwy pliku lub katalogu (do dostosowania)
        parent_dir = os.path.basename(os.path.dirname(input_nifti))
        symulacja = parent_dir.replace("dane_symulacja_", "")

        print(f"\n--- Przetwarzanie pliku {idx+1}/5: {izotop} ---")
        
        img_sitk = sitk.ReadImage(input_nifti)
        vol = sitk.GetArrayFromImage(img_sitk)

        # Weryfikacja zgodności wymiarów
        if vol.shape != mask_vol.shape:
            print(f"Błąd krytyczny: Rozmiar {input_nifti} {vol.shape} nie pasuje do maski {mask_vol.shape}")
            continue

        # Szukanie max intensywności dla każdej ze sfer
        for sphere_id in id_sfer:
            # Tworzymy binarną maskę tylko dla obecnej sfery
            pojedyncza_sfera_maska = (mask_vol == sphere_id)
            
            # Zerujemy wszystko poza sferą i liczymy sumę na każdej warstwie (oś Z)
            wartosci_w_sferze = vol * pojedyncza_sfera_maska
            slice_sums = np.sum(wartosci_w_sferze, axis=(1, 2))
            
            # Znalezienie warstwy z maksymalną aktywnością dla TEJ sfery
            max_intensity_idx = np.argmax(slice_sums)
            
            # Pobranie czystej warstwy z oryginalnego wolumenu (nie wyzerowanej!)
            max_slice = vol[max_intensity_idx, :, :]
            
            output_image = os.path.join(katalog_out, f"max_intensity_slice_sphere_{int(sphere_id)}_{symulacja}_{izotop}.png")
            
            # Zapis obrazu w formacie 1 piksel = 1 voxel
            plt.imsave(output_image, max_slice, cmap='viridis', origin='lower')
            print(f"Sfera {int(sphere_id)} | Warstwa: {max_intensity_idx + 1} -> Zapisano w {katalog_out}")

    print("\nGotowe. Przetworzono wszystkie zdefiniowane pliki.")
    return 0

if __name__ == "__main__":
    main()