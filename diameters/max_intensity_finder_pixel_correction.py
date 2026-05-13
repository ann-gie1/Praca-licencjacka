import SimpleITK as sitk
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import os

def main():
    sciezka_szukania = "./from_server/dane_symulacja_*/symulacja_conc_correct_NEMA_*.nii.gz"
    pliki_nifti = glob.glob(sciezka_szukania)

    if not pliki_nifti:
        print(f"Błąd: Nie znaleziono żadnych plików NIfTI w {sciezka_szukania}")
        return 1

    print(f"Znaleziono {len(pliki_nifti)} plików NIfTI do przetworzenia.")

    for input_nifti in pliki_nifti:
        nazwa_pliku = os.path.basename(input_nifti)
        
        izotop = nazwa_pliku.replace("symulacja_conc_correct_NEMA_", "").replace(".nii.gz", "")
        
        parent_dir = os.path.basename(os.path.dirname(input_nifti))
        symulacja = parent_dir.replace("dane_symulacja_", "")
        
        output_image = f"./diameters/max_intensity_slice_global_{symulacja}_{izotop}.png"

        print(f"\n--- Przetwarzanie izotopu: {izotop} ---")
        
        img_sitk = sitk.ReadImage(input_nifti)
        vol = sitk.GetArrayFromImage(img_sitk)

        slice_means = np.mean(vol, axis=(1, 2))
        max_intensity_idx = np.argmax(slice_means)
        max_slice = vol[max_intensity_idx, :, :]

        print(f"Indeks warstwy: {max_intensity_idx + 1} / {vol.shape[0]}")
        print(f"Zapisywanie obrazu o wymiarach: {max_slice.shape[1]}x{max_slice.shape[0]} pikseli")

        # Zapis czystej macierzy 1:1 bez osi, tytułów i marginesów
        plt.imsave(output_image, max_slice, cmap='viridis', origin='lower')
        
        print(f"Zapisano: {output_image}")

    print("\nGotowe. Przetworzono wszystkie izotopy.")
    return 0

if __name__ == "__main__":
    main()