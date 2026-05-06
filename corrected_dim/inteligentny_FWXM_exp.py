import os
import nibabel as nib
import numpy as np
from skimage.measure import label, regionprops
from scipy.ndimage import binary_dilation

def iterative_nema_thresholding_real(nifti_path):
    img = nib.load(nifti_path)
    data = img.get_fdata()
    
    voxel_dims = img.header.get_zooms()
    voxel_vol = np.prod(voxel_dims[:3])
    
    # 1. Próg maski wstępnej dopasowany do danych rzeczywistych
    global_max = np.max(data)
    rough_mask = data > (global_max * 0.28)
    labeled_mask = label(rough_mask)
    regions = regionprops(labeled_mask, intensity_image=data)
    
    results = []
    
    for prop in regions:
        if prop.area < 10:
            continue
            
        local_max = np.max(prop.intensity_image)
        
        # Ograniczenie roi ze zmniejszonym marginesem zapobiegającym wyjściu w tło poza fantomem
        bbox = prop.bbox
        margin = 5 
        rmin, cmin, zmin = max(0, bbox[0]-margin), max(0, bbox[1]-margin), max(0, bbox[2]-margin)
        rmax, cmax, zmax = min(data.shape[0], bbox[3]+margin), min(data.shape[1], bbox[4]+margin), min(data.shape[2], bbox[5]+margin)
        roi = data[rmin:rmax, cmin:cmax, zmin:zmax]
        
        threshold = local_max * 0.5
        converged = False
        
        for _ in range(20):
            sphere_mask = roi >= threshold
            if np.sum(sphere_mask) == 0:
                break
                
            # 2. Zwężona martwa strefa (1 woksel) i otoczka pomiarowa (2 woksele)
            gap_mask = binary_dilation(sphere_mask, iterations=1) 
            outer_mask = binary_dilation(gap_mask, iterations=2)
            shell_mask = outer_mask ^ gap_mask
            
            if np.sum(shell_mask) == 0:
                break
                
            # 3. Zabezpieczenie: Mierzymy tylko ciepłe tło, ignorując zera i powietrze/plastik
            bg_values = roi[shell_mask]
            warm_bg_values = bg_values[bg_values > (global_max * 0.05)]
            
            if len(warm_bg_values) == 0:
                break
                
            background_mean = np.mean(warm_bg_values)
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
            
            if diameter_mm < 60: # Odsiewamy ewentualne artefakty
                results.append(diameter_mm)
                
    results.sort()
    return results

# Użycie i zapis do CSV
plik_nifti = "./python_code/nema_volume.nii.gz"
output_csv = "./corrected_dim/wyniki_eksperyment_nema.csv"

if os.path.exists(plik_nifti):
    srednice = iterative_nema_thresholding_real(plik_nifti)
    
    print(f"Wyniki dla: {plik_nifti}")
    
    with open(output_csv, 'w', encoding='utf-8') as f:
        f.write("Plik,Sfera,Srednica_mm\n")
        filename = os.path.basename(plik_nifti)
        
        for i, d in enumerate(srednice):
            print(f"  Sfera {i+1}: Średnica = {d:.2f} mm")
            f.write(f"{filename},{i+1},{d:.2f}\n")
            
    print(f"\nZapisano wyniki do: {output_csv}")
else:
    print(f"Błąd: Nie znaleziono pliku {plik_nifti}")