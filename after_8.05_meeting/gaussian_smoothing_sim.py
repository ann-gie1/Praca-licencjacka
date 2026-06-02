import nibabel as nib
from scipy.ndimage import gaussian_filter
import os
import numpy as np

# Lista ścieżek do plików
file_paths = [
    "./from_server/dane_symulacja_cal_gonzales/symulacja_conc_correct_NEMA_18F_20626.nii.gz",
    "./from_server/dane_symulacja_cal_gonzales/symulacja_conc_correct_NEMA_44Sc_20626.nii.gz",
    "./from_server/dane_symulacja_CSDA/symulacja_conc_correct_NEMA_18F_20626.nii.gz",
    "./from_server/dane_symulacja_CSDA/symulacja_conc_correct_NEMA_44Sc_20626.nii.gz"
]

fwhm_value = 2
# Poprawne przejście z FWHM na sigmę
sigma_value = fwhm_value / (2 * np.sqrt(2 * np.log(2)))

for file_path in file_paths:
    # Weryfikacja: sprawdzenie czy plik istnieje
    if not os.path.exists(file_path):
        print(f"Brak pliku: {file_path}. Pomijam.")
        continue
        
    print(f"Przetwarzanie: {file_path}")
    
    # Automatyczne pobranie nazwy folderu (np. 'dane_symulacja_CSDA')
    parent_dir = os.path.basename(os.path.dirname(file_path))
    
    # Skrócenie nazwy dla czytelności (usunięcie wspólnego przedrostka)
    tag = parent_dir.replace("dane_symulacja_", "")

    # Wczytaj plik
    img = nib.load(file_path)
    data = img.get_fdata()

    # Nałóż Gaussian smoothing z przeliczoną sigmą
    smoothed_data = gaussian_filter(data, sigma=sigma_value)

    # Wygeneruj nazwę wyjściową z unikalnym tagiem (zmieniono suffix na FWHM)
    base_name = os.path.basename(file_path)
    name, ext = base_name.split('.nii', 1)
    output_path = f"./after_8.05_meeting/nii files/{name}_{tag}_smoothed_fwhm{fwhm_value}_20626.nii{ext}"

    # Zapisz wynik
    new_img = nib.Nifti1Image(smoothed_data, img.affine, img.header)
    nib.save(new_img, output_path)
    print(f"Zapisano jako: {output_path}\n")