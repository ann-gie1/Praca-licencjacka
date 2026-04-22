"""

"""
# Python libraries
from pathlib import Path
import sys
import numpy as np
import SimpleITK as sitk

# For visualization
from vis import vis_3d


def main():
    # From https://arxiv.org/pdf/2506.07230
    n_voxels = (200, 200, 200)
    spacing = (2.5, 2.5, 2.5)  # mm

    # sys.path[0] to folder startowy skryptu
    base_dir = Path(sys.path[0])
    # .parent.parent cofa o dwa foldery w górę
    file_path = base_dir.parent.parent / 'nema_iq_sc_f18_it10' / 'nema_iq_sc_f18_it10.img'

    vol = np.fromfile(file_path, dtype=np.float32)
    vol = np.reshape(vol, n_voxels, order='F')

    img_sitk = sitk.GetImageFromArray(np.transpose(vol, (2, 1, 0)))
    img_sitk.SetSpacing(spacing)
    sitk.WriteImage(img_sitk, "nema_volume.nii.gz")
    print("Plik NIfTI został zapisany jako nema_volume.nii.gz")

    vis_3d(vol, spacing=spacing)

    return 0


if __name__ == "__main__":
    main()
