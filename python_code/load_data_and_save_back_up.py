# Python libraries
from pathlib import Path
import sys
import numpy as np
import plotly.graph_objects as go # DODANE

# For visualization
from vis import vis_3d

# DODANA FUNKCJA
def save_html_slider(vol, output_path="nema_interactive.html"):
    fig = go.Figure()
    n_slices = vol.shape[2]
    idx_initial = n_slices // 2

    # Dodajemy każdą warstwę, ale tylko środkowa jest domyślnie widoczna
    for i in range(n_slices):
        fig.add_trace(go.Heatmap(
            z=vol[:, :, i].T,
            visible=(i == idx_initial),
            colorscale='Viridis', # Domyslny schemat kolorów dla medycznych danych
            showscale=False
        ))

    # Tworzymy kroki dla suwaka
    steps = []
    for i in range(n_slices):
        step = dict(
            method="update",
            args=[{"visible": [False] * n_slices},
                  {"title": f"Warstwa: {i + 1} / {n_slices}"}],
        )
        step["args"][0]["visible"][i] = True
        steps.append(step)

    # Dodajemy suwak do układu
    fig.update_layout(
        sliders=[dict(active=idx_initial, currentvalue={"prefix": "Skok: "}, pad={"t": 50}, steps=steps)],
        title=f"Warstwa: {idx_initial + 1} / {n_slices}",
        width=700, height=700
    )
    
    # Zapis do samodzielnego pliku HTML
    fig.write_html(output_path)
    print(f"Zapisano interaktywny plik HTML do: {output_path}")


def main():
    # From https://arxiv.org/pdf/2506.07230
    n_voxels = (200, 200, 200)
    spacing = (2.5, 2.5, 2.5)  # mm

    base_dir = Path(sys.path[0])
    file_path = base_dir.parent.parent / 'nema_iq_sc_f18_it10' / 'nema_iq_sc_f18_it10.img'

    vol = np.fromfile(file_path, dtype=np.float32)
    vol = np.reshape(vol, n_voxels, order='F')

    # Wywołanie Twojej wizualizacji (zostaje jak było)
    vis_3d(vol, spacing=spacing)

    # DODANE: Wywołanie funkcji zapisującej do HTML
    save_html_slider(vol)

    return 0


if __name__ == "__main__":
    main()