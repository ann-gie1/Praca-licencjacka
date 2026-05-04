import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from skimage.measure import label, regionprops

def measure_nema_spheres_3d_adaptive(nifti_path, save_path=None, show_plot=True):
    img = nib.load(nifti_path)
    data = img.get_fdata()
    
    voxel_dims = img.header.get_zooms()
    voxel_volume = np.prod(voxel_dims[:3])
    
    # 1. Zgrubna maska (np. 5% maksimum globalnego)
    rough_threshold = np.max(data) * 0.05
    rough_mask = data > rough_threshold
    
    labeled_mask = label(rough_mask)
    regions = regionprops(labeled_mask, intensity_image=data)
    
    diameters_mm = []
    
    # Pusta maska do wizualizacji - wymiary takie same jak oryginalny obraz
    final_mask = np.zeros_like(data)
    
    for prop in regions:
        if prop.area > 10:
            local_max = np.max(prop.intensity_image)
            local_threshold = local_max * 0.5
            
            # Woksele należące do tej sfery ORAZ przekraczające 50% jej LOKALNEGO maksimum
            sphere_mask = prop.image & (prop.intensity_image > local_threshold)
            actual_voxels = np.sum(sphere_mask)
            
            if actual_voxels > 0:
                volume_mm3 = actual_voxels * voxel_volume
                diameter_mm = 2 * ((3 * volume_mm3) / (4 * np.pi)) ** (1/3)
                
                # Odrzucamy tło/główną komorę (np. obiekty większe niż 60mm)
                if diameter_mm < 60: 
                    diameters_mm.append(diameter_mm)
                    
                    # Nakładamy sferę na końcową maskę wizualizacyjną
                    # bbox: (min_x, min_y, min_z, max_x, max_y, max_z)
                    bbox = prop.bbox
                    # Zapisujemy ID sfery na masce (aby każda miała ewentualnie inny kolor)
                    sphere_id = len(diameters_mm)
                    final_mask[bbox[0]:bbox[3], bbox[1]:bbox[4], bbox[2]:bbox[5]][sphere_mask] = sphere_id
            
    diameters_mm.sort()
    
    if save_path:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write("Sfera,Srednica_mm\n")
            for i, d in enumerate(diameters_mm):
                f.write(f"{i+1},{d:.2f}\n")
        print(f"Wyniki zapisano do: {save_path}")

    # --- WIZUALIZACJA ---
    if show_plot and len(diameters_mm) > 0:
        # Znajdujemy indeks warstwy Z, na której znajduje się najjaśniejszy piksel (globalne maksimum)
        # Sfery NEMA są zazwyczaj ułożone w jednej płaszczyźnie, więc ta warstwa pokaże je najlepiej.
        z_slice = np.unravel_index(np.argmax(data), data.shape)[2]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 7))
        
        # 1. Oryginalny obraz
        # Używamy .T (transpozycji), aby dopasować standardowy widok NIfTI
        im0 = axes[0].imshow(data[:, :, z_slice].T, cmap='viridis', origin='lower')
        axes[0].set_title(f"Oryginalny obraz (Warstwa Z: {z_slice})")
        axes[0].axis('off')
        fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label="Intensywność")
        
        # 2. Obraz z nałożoną maską
        axes[1].imshow(data[:, :, z_slice].T, cmap='gray', origin='lower')
        
        # Przygotowanie maski (ukrywamy zera, żeby były przezroczyste)
        mask_2d = final_mask[:, :, z_slice].T
        masked_data = np.ma.masked_where(mask_2d == 0, mask_2d)
        
        # Rysujemy maskę (cmap='Set1' da ładne, wyraźne kolory dla różnych sfer)
        axes[1].imshow(masked_data, cmap='Set1', alpha=0.7, origin='lower')
        axes[1].set_title("Wykryte sfery (Nakładka)")
        axes[1].axis('off')
        
        plt.tight_layout()
        plt.show()
                
    return diameters_mm

# --- Wywołanie ---
input_file = "./python_code/nema_volume.nii.gz"
output_file = "./python_code/wyniki_eksperyment_sfery.csv"

# Funkcja teraz po zakończeniu obliczeń wyświetli okienko z wykresem
measured_diameters = measure_nema_spheres_3d_adaptive(input_file, save_path=output_file)

for i, d in enumerate(measured_diameters):
    print(f"Sfera {i+1}: {d:.2f} mm")