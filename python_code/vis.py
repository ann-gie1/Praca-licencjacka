"""
Data visualization

@author: Martin Rädler
"""
# Python libraries
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm


def vis_3d(img, spacing=None, transpose=False, axis=-1):
    # Move the slice axis to the last dimension
    img = np.moveaxis(img, axis, -1)
    if transpose:
        img = np.moveaxis(img, 0, 1)
    idx_max = img.shape[-1]
    idx_initial = int(idx_max / 2)

    # Interactive figure
    fig, ax = plt.subplots()
    ax.set_label('main')
    fig_text = fig.text(0.02, 0.02, 'Scroll step: 1')
    im = ax.imshow(img[:, :, idx_initial].T, origin='lower')
    # im = ax.imshow(img[:, :, idx_initial].T, origin='lower', vmin=0)
    # im = ax.imshow(img[:, :, idx_initial].T, origin='lower', norm=LogNorm(vmin=1e-8, vmax=1e-4))

    if spacing is None:
        ax.set_aspect('auto')
    else:
        # Spacing of the 2D slices
        spacing_slice = np.delete(spacing, axis)
        if transpose:
            ax.set_aspect(spacing_slice[0] / spacing_slice[1])
        else:
            ax.set_aspect(spacing_slice[1] / spacing_slice[0])

    cax = make_axes_locatable(ax).append_axes('right', size='5%', pad=0.1)
    cax.set_label('colorbar')
    fig.colorbar(im, cax=cax, orientation='vertical')
    # cax.set_aspect(20 * np.diff(cax.get_xlim()) / np.diff(cax.get_ylim()) * ax.get_aspect())

    ax_title = ax.set_title('%i / %i' % (idx_initial + 1, idx_max))
    [spine[1].set_linewidth(1.6) for spine in cax.spines.items()]

    def update_scroll(event):
        # Update the index
        if event.button == 'up':
            diff = idx_max - 1 - update_scroll.idx
            if diff >= update_click.scroll_step:
                update_scroll.idx += update_click.scroll_step
            elif diff > 0:
                update_scroll.idx = idx_max - 1
            else:
                return

        if event.button == 'down':
            if update_scroll.idx - update_click.scroll_step >= 0:
                update_scroll.idx -= update_click.scroll_step
            elif update_scroll.idx > 0:
                update_scroll.idx = 0
            else:
                return

        # Update image, colorbar (if desired) and title
        new_img = img[:, :, update_scroll.idx].T
        im.set_data(new_img)
        if update_click.update_colorbar:
            im.set_clim(np.min(new_img), np.max(new_img))
        ax_title.set_text('%i / %i' % (update_scroll.idx + 1, idx_max))
        fig.canvas.draw()

        return 0

    def update_click(event):
        # Only act if inside axis
        if event.inaxes is None:
            return

        # If inside main axis
        if event.inaxes.get_label() == 'main':
            if event.button == 1:
                update_click.scroll_step += 1
            elif event.button == 3:
                if update_click.scroll_step > 1:
                    update_click.scroll_step -= 1

            fig_text.set_text('Scroll step: %d' % update_click.scroll_step)

        # If inside colorbar
        if event.inaxes.get_label() == 'colorbar':
            update_click.update_colorbar = ~ update_click.update_colorbar
            if update_click.update_colorbar:
                [spine[1].set_linewidth(0.8) for spine in cax.spines.items()]
            else:
                [spine[1].set_linewidth(1.6) for spine in cax.spines.items()]

        fig.canvas.draw()
        return 0

    update_scroll.idx = idx_initial
    update_click.scroll_step = 1
    update_click.update_colorbar = False
    fig.canvas.mpl_connect('scroll_event', update_scroll)
    fig.canvas.mpl_connect('button_press_event', update_click)

    plt.show()
    return 0
