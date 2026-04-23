"""
Znajdowanie i zapisywanie warstwy o maksymalnej intensywności z pliku NIfTI.

Ten skrypt wczytuje wolumen NIfTI, automatycznie znajduje warstwę
z największą średnią intensywnością (gdzie znajdują się sfery fantomu),
wyświetla ją jako statyczny obraz 2D z paskiem kolorów i zapisuje do pliku graficznego.
"""

# 1. Import niezbędnych bibliotek
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from pathlib import Path
import sys
import os

def main():
    
    input_nifti = f"./dane_symulacja_CSDA/symulacja_NEMA_44Sc.nii.gz"
    output_image =f"symulacja_max_intensity_slice_44Sc.png"

    # Sprawdzenie, czy plik wejściowy istnieje
    if not os.path.exists(input_nifti):
        print(f"Błąd: Nie znaleziono pliku wejściowego {input_nifti}")
        return 1

    print(f"Wczytywanie pliku NIfTI: {input_nifti}...")

    # 3. Wczytanie wolumenu NIfTI
    img_sitk = sitk.ReadImage(str(input_nifti))
    
    # Pobranie danych jako macierzy NumPy i zamiana osi na (z, y, x)
    vol = sitk.GetArrayFromImage(img_sitk)
    # Oryginalny układ z `vis_3d` to był (x, y, z).
    # SimpleITK wczytuje jako (z, y, x). To nam odpowiada do szukania warstw wzdłuż Z.
    # Jeśli jednak chcesz zachować orientację z `vis_3d`, gdzie `imshow`
    # wyświetlało `vol[:, :, idx].T` z `origin='lower'`, musimy to odtworzyć.
    # vol[:, :, idx] w `vis_3d` to jest wolumen (x, y, z).
    # vol[:, :, idx].T w `vis_3d` to jest warstwa (y, x).
    # Nasz obecny `vol` jest (z, y, x).

    # 4. Automatyczne znalezienie warstwy o maksymalnej średniej intensywności sfer
    # Obliczamy średnią intensywność dla każdej warstwy wzdłuż osi Z (osi 0).
    # Zakładamy, że sfery są najjaśniejszymi obiektami i ich obecność
    # znacznie podniesie średnią warstwy.
    slice_means = np.mean(vol, axis=(1, 2))
    
    # Znalezienie indeksu warstwy o maksymalnej średniej
    max_intensity_idx = np.argmax(slice_means)
    max_intensity_value = slice_means[max_intensity_idx]
    
    print(f"Znaleziono warstwę o maksymalnej średniej intensywności.")
    print(f"Indeks warstwy: {max_intensity_idx + 1} / {vol.shape[0]}")
    print(f"Średnia intensywność tej warstwy: {max_intensity_value:.6f}")

    # Wyciągnięcie tej jednej, płaskiej warstwy 2D (macierz y, x)
    max_slice = vol[max_intensity_idx, :, :]

    # 5. Wyświetlenie i zapisanie statycznego obrazu 2D
    # Tworzymy figurę
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Wyświetlamy obraz. 
    # Aby zachować tę samą orientację co w `vis_3d` (sfery w tych samych miejscach),
    # używamy `imshow(max_slice, origin='lower')`.
    # `max_slice` to macierz (y, x). `imshow` interpretuje to jako (wiersze, kolumny),
    # co odpowiada (y, x). `origin='lower'` sprawia, że y=0 jest na dole.
    # Nie musimy tu robić .T, bo nasza macierz ma już układ (y, x).
    im = ax.imshow(max_slice, origin='lower', cmap='viridis')
    
    # Dodanie tytułu z informacją o warstwie
    ax.set_title(f'Warstwa o maks. intensywności: {max_intensity_idx + 1} / {vol.shape[0]}')
    
    # Dodanie pasku kolorów
    fig.colorbar(im, ax=ax, label='Intensywność')

    # Zapisanie figury do pliku PNG
    print(f"Zapisywanie statycznego obrazu do: {output_image}...")
    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    
    # Wyświetlenie obrazu na ekranie (opcjonalne, skrypt się nie zablokuje)
    plt.show()

    print("Gotowe.")
    return 0

if __name__ == "__main__":
    main()