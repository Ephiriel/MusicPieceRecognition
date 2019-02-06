import numpy as np

import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection


# Example code from matplotlib homepage for radar plots
def radar_factory(num_vars, frame='circle'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    def draw_poly_patch(self):
        # rotate theta such that the first axis is at the top
        verts = unit_poly_verts(theta + np.pi / 2)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta + np.pi / 2)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts


def example_data():
    data = [
        ['2: Unchanged', '3: Transposed', '4: Pitch Error 1', '5: Pitch Error 2', '6: Pitch Error 3', '7: Tempo Changed', '8: Note Duration 1', '9: Note Duration 2', '10: Note Duration 3', '11: Added Notes', '12: Removed Notes', '13: Added/Removed', '14: Combined 1', '15: Combined 2'],
        ('Combined', [
            [0.993, 0.993, 0.990, 0.959, 0.896, 0.993, 0.993, 0.993, 0.993, 0.932, 0.984, 0.872, 0.694, 0.680],
            [0.992, 0.992, 0.991, 0.984, 0.975, 0.992, 0.992, 0.992, 0.992, 0.920, 0.988, 0.896, 0.824, 0.826],
            [0.992, 0.014, 0.992, 0.992, 0.991, 0.992, 0.991, 0.991, 0.990, 0.958, 0.979, 0.934, 0.856, 0.009],
            [0.989, 0.989, 0.990, 0.989, 0.989, 0.988, 0.990, 0.987, 0.984, 0.920, 0.966, 0.869, 0.681, 0.668],
            [0.993, 0.993, 0.993, 0.990, 0.984, 0.993, 0.992, 0.992, 0.992, 0.966, 0.984, 0.936, 0.845, 0.843]]),
        ('Smith Waterman', [
            [0.993, 0.993, 0.990, 0.959, 0.896, 0.993, 0.993, 0.993, 0.993, 0.932, 0.984, 0.872, 0.694, 0.680]]),
        ('DTW', [
            [0.992, 0.992, 0.991, 0.984, 0.975, 0.992, 0.992, 0.992, 0.992, 0.920, 0.988, 0.896, 0.824, 0.826]]),
        ('Fingerpint Hash 1', [
            [0.992, 0.014, 0.992, 0.992, 0.991, 0.992, 0.991, 0.991, 0.990, 0.958, 0.979, 0.934, 0.856, 0.009]]),
        ('Fingerpint Hash 2', [
            [0.989, 0.989, 0.990, 0.989, 0.989, 0.988, 0.990, 0.987, 0.984, 0.920, 0.966, 0.869, 0.681, 0.668]]),
        ('Fingerpint Hash 3', [
            [0.993, 0.993, 0.993, 0.990, 0.984, 0.993, 0.992, 0.992, 0.992, 0.966, 0.984, 0.936, 0.845, 0.843]]),
    ]
    return data


if __name__ == '__main__':
    N = 14
    theta = radar_factory(N, frame='polygon')

    data = example_data()
    spoke_labels = data.pop(0)

    fig, axes = plt.subplots(figsize=(9, 9), nrows=3, ncols=2,
                             subplot_kw=dict(projection='radar'))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    colors = ['b', 'r', 'g', 'm', 'y']
    # Plot the four cases from the example data on separate axes
    for idx, (ax, (title, case_data)) in enumerate(zip(axes.flatten(), data)):
        ax.set_rgrids([0.2, 0.4, 0.6, 0.8])
        ax.set_ylim((0, 1))
        ax.set_title(title, weight='bold', size='medium', position=(0.5, 0.5),
                     horizontalalignment='center', verticalalignment='center')
        if len(case_data) == 1:
            ax.plot(theta, case_data[0], color=colors[idx-1])
            ax.fill(theta, case_data[0], facecolor=colors[idx-1], alpha=0.25)
        else:
            for d, color in zip(case_data, colors):
                ax.plot(theta, d, color=color)
                ax.fill(theta, d, facecolor=color, alpha=0.25)
        if idx == 1:
            ax.set_varlabels(spoke_labels)
        else:
            ax.set_varlabels(["2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"])

    # add legend relative to top-left plot
    ax = axes[0, 0]
    labels = ('Smith Waterman', 'DTW', 'Fingerprinting Hash 1', 'Fingerprinting Hash 2', 'Fingerprinting Hash 3')
    legend = ax.legend(labels, loc=(0.9, .95),
                       labelspacing=0.1, fontsize='small')

    fig.text(0.5, 0.92, 'Comparison of the Algorithms on different experiments',
             horizontalalignment='center', color='black', weight='bold',
             size='large')

    plt.show()
