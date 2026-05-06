import os
import nibabel as nib
import numpy as np
from skimage.measure import label, regionprops
from scipy.ndimage import binary_dilation

def iterative_nema_thresholding(nifti_path):
    img = nib.load(nifti_path)
    data = img.get_fdata()
    
    voxel_dims = img.header.get_zooms()
    voxel_vol = np.prod(voxel_dims[:3])
    
    # Powrót do 5% global max dla bezpieczniejszej wstępnej maski
    global_max = np.max(data)
    rough_mask = data > (global_max * 0.2)
    labeled_mask = label(rough_mask)
    regions = regionprops(labeled_mask, intensity_image=data)
    
    results = []
    
    for prop in regions:
        if prop.area < 10:
            continue
            
        local_max = np.max(prop.intensity_image)
        bbox = prop.bbox
        roi = data[bbox[0]:bbox[3], bbox[1]:bbox[4], bbox[2]:bbox[5]]
        
        # Iteracyjne szukanie progu
        threshold = local_max * 0.5
        converged = False
        
        for _ in range(20):
            sphere_mask = roi >= threshold
            if np.sum(sphere_mask) == 0:
                break
                
            dilated_mask = binary_dilation(sphere_mask, iterations=2)
            shell_mask = dilated_mask ^ sphere_mask # Tylko otoczka (tło)
            
            if np.sum(shell_mask) == 0:
                break
                
            background_mean = np.mean(roi[shell_mask])
            new_threshold = 0.5 * local_max + 0.5 * background_mean
            
            if abs(new_threshold - threshold) / threshold < 0.01:
                converged = True
                threshold = new_threshold
                break
                
            threshold = new_threshold
            
        if converged:
            final_mask = roi >= threshold
            actual_voxels = np.sum(final_mask)
            volume_mm3 = actual_voxels * voxel_vol
            diameter_mm = 2 * ((3 * volume_mm3) / (4 * np.pi)) ** (1/3)
            
            if diameter_mm < 60:
                results.append(diameter_mm)
                
    results.sort()
    return results

# --- Pętla po plikach i zapis do CSV ---

input_files = [
    "./from_server/dane_symulacja_cal_gonzales/symulacja_conc_correct_NEMA_18F.nii.gz",
    "./from_server/dane_symulacja_cal_gonzales/symulacja_conc_correct_NEMA_44Sc.nii.gz",
    "./from_server/dane_symulacja_CSDA/symulacja_conc_correct_NEMA_18F.nii.gz",
    "./from_server/dane_symulacja_CSDA/symulacja_conc_correct_NEMA_44Sc.nii.gz"
]

output_file = "./corrected_dim/wyniki_innteligent_FWxM-no-exp.csv"

with open(output_file, 'w', encoding='utf-8') as f:
    f.write("Plik,Sfera,Srednica_mm\n")
    
    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"Pomijam - plik nie istnieje: {file_path}")
            continue
            
        print(f"Przetwarzanie: {file_path}...")
        
        measured_diameters = iterative_nema_thresholding(file_path)
        filename = os.path.basename(file_path)
        
        for i, d in enumerate(measured_diameters):
            f.write(f"{filename},{i+1},{d:.2f}\n")
            print(f"  {filename} - Sfera {i+1}: {d:.2f} mm")

print(f"\nWszystkie wyniki zbiorczo zapisano do: {output_file}")