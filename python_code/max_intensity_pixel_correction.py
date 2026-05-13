import SimpleITK as sitk
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import os

def main():
    sciezka_szukania = "./python_code/nema_volume.nii.gz"
    pliki_nifti = glob.glob(sciezka_szukania)

    if not pliki_nifti:
        print(f"Błąd: Nie znaleziono żadnych plików NIfTI w {sciezka_szukania}")
        return 1

    print(f"Znaleziono {len(pliki_nifti)} plików NIfTI do przetworzenia.")

    for input_nifti in pliki_nifti:
        
        output_image = f"./after_8.05_meeting/max_intensity_global/nema_max_intensity_slice.png"
        
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