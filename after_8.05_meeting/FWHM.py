import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops
from scipy.ndimage import binary_erosion # Dodany import

def measure_nema_spheres_3d_adaptive(nifti_path, show_plot=False):
    img = nib.load(nifti_path)
    data = img.get_fdata()
    
    voxel_dims = img.header.get_zooms()[:3]
    voxel_volume = np.prod(voxel_dims)
    
    rough_threshold = np.max(data) * 0.05
    rough_mask = data > rough_threshold
    
    labeled_mask = label(rough_mask)
    regions = regionprops(labeled_mask, intensity_image=data)
    
    results = [] # Zmieniona lista na przechowywanie krotek (srednica, blad)
    final_mask = np.zeros_like(data)
    
    for prop in regions:
        if prop.area > 5:
            local_max = np.max(prop.intensity_image)
            local_threshold = local_max * 0.5
            
            sphere_mask = prop.image & (prop.intensity_image > local_threshold)
            actual_voxels = np.sum(sphere_mask)
            
            if actual_voxels > 0:
                volume_mm3 = actual_voxels * voxel_volume
                diameter_mm = 2 * ((3 * volume_mm3) / (4 * np.pi)) ** (1/3)
                
                if diameter_mm < 60: 
                    # --- WYLICZANIE BŁĘDU (Odchylenie brzegów od kuli) ---
                    eroded_mask = binary_erosion(sphere_mask)
                    boundary_mask = sphere_mask ^ eroded_mask # XOR: tylko brzegi
                    bz, by, bx = np.where(boundary_mask)
                    
                    if len(bz) > 1:
                        # Przeliczenie współrzędnych brzegowych na fizyczne milimetry
                        coords_mm = np.column_stack((bz, by, bx)) * np.array(voxel_dims)
                        centroid_mm = np.mean(coords_mm, axis=0)
                        
                        # Odległość każdego punktu brzegowego od środka
                        distances = np.linalg.norm(coords_mm - centroid_mm, axis=1)
                        # Błąd średnicy to podwojone odchylenie standardowe promienia
                        error_mm = 2 * np.std(distances, ddof=1)
                    else:
                        error_mm = 0.0
                    # ---------------------------------------------------

                    results.append((diameter_mm, error_mm))
                    
                    bbox = prop.bbox
                    sphere_id = len(results)
                    final_mask[bbox[0]:bbox[3], bbox[1]:bbox[4], bbox[2]:bbox[5]][sphere_mask] = sphere_id
            
    # Sortowanie po średnicy (rosnąco)
    results.sort(key=lambda x: x[0])

    if show_plot and len(results) > 0:
        z_slice = np.unravel_index(np.argmax(data), data.shape)[2]
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        
        im0 = axes[0].imshow(data[:, :, z_slice].T, cmap='viridis', origin='lower')
        axes[0].set_title(f"Oryginalny obraz (Warstwa Z: {z_slice})")
        axes[0].axis('off')
        fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label="Intensywność")
        
        axes[1].imshow(data[:, :, z_slice].T, cmap='gray', origin='lower')
        mask_2d = final_mask[:, :, z_slice].T
        masked_data = np.ma.masked_where(mask_2d == 0, mask_2d)
        
        axes[1].imshow(masked_data, cmap='Set1', alpha=0.7, origin='lower')
        axes[1].set_title(f"Wykryte sfery - {os.path.basename(nifti_path)}")
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.show()
                
    return results

# --- Wywołanie dla 5 plików ---
input_files = [
    "./python_code/nema_volume.nii.gz",
    "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_18F_cal_gonzales_smoothed_sigma2.nii.gz",
    "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_44Sc_cal_gonzales_smoothed_sigma2.nii.gz",
    "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_18F_CSDA_smoothed_sigma2.nii.gz",
    "./after_8.05_meeting/nii files/symulacja_conc_correct_NEMA_44Sc_CSDA_smoothed_sigma2.nii.gz"
]

output_file = "./after_8.05_meeting/wyniki_FWHM_with_error.csv"

with open(output_file, 'w', encoding='utf-8') as f:
    # Zmodyfikowany nagłówek CSV
    f.write("Plik,Sfera,Srednica_mm,Blad_mm\n")
    
    for file_path in input_files:
        if not os.path.exists(file_path):
            print(f"Pomijam - plik nie istnieje: {file_path}")
            continue
            
        print(f"Przetwarzanie: {file_path}...")
        
        measured_data = measure_nema_spheres_3d_adaptive(file_path, show_plot=False)
        filename = os.path.basename(file_path)
        
        for i, (d, err) in enumerate(measured_data):
            # Zapis do CSV uwzględniający nową kolumnę błędu
            f.write(f"{filename},{i+1},{d:.2f},{err:.2f}\n")
            print(f"  {filename} - Sfera {i+1}: {d:.2f} ± {err:.2f} mm")

print(f"\nWszystkie wyniki zbiorczo zapisano do: {output_file}")