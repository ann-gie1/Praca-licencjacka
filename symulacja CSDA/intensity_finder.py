import SimpleITK as sitk
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Wymusza tryb bezekranowy (kluczowe na serwerze)
import matplotlib.pyplot as plt
import glob
import os

def main():
    # Szukamy wszystkich plików NIfTI wygenerowanych przez poprzedni skrypt
    sciezka_szukania = "../dane_symulacja_CSDA/symulacja_conc_corrects_NEMA_*.nii.gz"
    pliki_nifti = glob.glob(sciezka_szukania)

    if not pliki_nifti:
        print(f"Błąd: Nie znaleziono żadnych plików NIfTI w {sciezka_szukania}")
        return 1

    print(f"Znaleziono {len(pliki_nifti)} plików NIfTI do przetworzenia.")

    # Pętla dla każdego znalezionego pliku
    for input_nifti in pliki_nifti:
        # Wyciągamy nazwę izotopu z nazwy pliku (np. 'symulacja_NEMA_44Sc.nii.gz' -> '44Sc')
        nazwa_pliku = os.path.basename(input_nifti)
        izotop = nazwa_pliku.replace("symulacja_NEMA_", "").replace(".nii.gz", "")
        
        # Ustawiamy ścieżkę wyjściową w tym samym folderze
        output_image = f"../dane_symulacja_CSDA/symulacja_max_intensity_slice_corr_conc_{izotop}.png"

        print(f"\n--- Przetwarzanie izotopu: {izotop} ---")
        
        # Wczytanie wolumenu NIfTI
        img_sitk = sitk.ReadImage(input_nifti)
        vol = sitk.GetArrayFromImage(img_sitk)

        # Znalezienie warstwy o maksymalnej średniej intensywności
        slice_means = np.mean(vol, axis=(1, 2))
        max_intensity_idx = np.argmax(slice_means)
        max_slice = vol[max_intensity_idx, :, :]

        print(f"Indeks warstwy: {max_intensity_idx + 1} / {vol.shape[0]}")

        # Rysowanie
        fig, ax = plt.subplots(figsize=(8, 8))
        im = ax.imshow(max_slice, origin='lower', cmap='viridis')
        ax.set_title(f'Warstwa o maks. intensywności ({izotop}): {max_intensity_idx + 1} / {vol.shape[0]}')
        fig.colorbar(im, ax=ax, label='Intensywność')

        # Zapis i zwolnienie pamięci (konieczne w pętli)
        plt.savefig(output_image, dpi=300, bbox_inches='tight')
        plt.close(fig) 
        
        print(f"Zapisano: {output_image}")

    print("\nGotowe. Przetworzono wszystkie izotopy.")
    return 0

if __name__ == "__main__":
    main()