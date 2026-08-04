"""
Slide pair: the small-n outlier illusion. C4R-styled remake of two screenshots.

  Figure A : n = 3   -> the three points look linear
  Figure B : n = 20  -> the third point is revealed as an outlier

Both figures share IDENTICAL axis limits, so the three original points land on
exactly the same pixels in each; the pair cross-fades cleanly on a slide.

No titles, no legend, no ticks: the data is abstract, so numbers on the axes
would imply precision the figure doesn't have.

X-NORMALIZATION
---------------
The 17 grey points were traced from the source screenshot, where they had been
placed by eye. Their y values are pedagogically fine but their x values were
too evenly spread to be a normal sample (excess kurtosis about -1.2, no dense
middle, no tails). x_normalized() replaces the x values with normal quantiles
while keeping every y value untouched, and keeps left-right rank order so each
point moves as little as possible. Because the x VALUES are a fixed set, the
assignment of values to points is just a permutation -- so collisions between
markers can be fixed by swapping assignments without disturbing normality at
all.

Pick a variant with X_MODE below.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
from scipy import stats
import c4r_style as c4r

c4r.apply()

# --------------------------------------------------------------------------
# DATA (traced from the originals; abstract units)
# --------------------------------------------------------------------------
# The three points collected first. Index 2 is revealed as the outlier.
ORIGINAL_3 = np.array([
    (1.97, 2.15),
    (4.96, 5.20),   # the "middle" blue point
    (7.75, 7.42),   # <- the outlier
])
OUTLIER_IDX = 2

# The 17 points added when n grows to 20. Y VALUES ARE NEVER MODIFIED.
CLOUD_17 = np.array([
    (4.38, 5.23), (3.47, 4.82), (1.86, 4.22), (5.26, 4.41), (2.75, 3.78),
    (5.83, 3.78), (4.67, 3.48), (3.76, 2.99), (1.17, 2.99), (5.56, 2.77),
    (6.15, 2.39), (2.18, 2.47), (3.17, 2.17), (1.58, 1.76), (4.93, 1.96),
    (4.06, 1.78), (2.56, 1.46),
])

XLIM = (0, 10)
YLIM = (0, 10)

# --------------------------------------------------------------------------
# X-NORMALIZATION VARIANTS  (mean, sd) for the grey points' x values
# --------------------------------------------------------------------------
X_VARIANTS = {
    # Centered on the middle blue point, as originally requested. Note this
    # strands the lower-left blue point 3.2 sd out, so it reads as a second
    # outlier.
    "centered":  (4.96, 0.95),
    # Shifted part-way toward the middle blue point: that point becomes an
    # ordinary member of the cloud (+0.5 sd) while the lower-left one stays
    # inside it (-1.7 sd). RECOMMENDED.
    "compromise": (4.30, 1.35),
    # Shape fixed, center left where it was traced. Smallest possible change.
    "shapeonly": (3.73, 1.55),
    # No change at all: use the traced x values.
    "traced":    None,
}
X_MODE = "traced"

# --------------------------------------------------------------------------
# MARKER SIZES (scaled from the source screenshots to the locked plot area)
# --------------------------------------------------------------------------
# The 17 context points are BLACK and formatted exactly like the blue ones
# (solid fill, no edge). GREY was too close to the slide background to read.
# Black raw points are already the C4R default elsewhere -- see the point_color
# fallback in c4r_style._boxplot -- so this stays inside the guide.
S_CLOUD    = 110    # context points
S_ORIGINAL = 230    # 1.44x the cloud diameter, matching the source
S_OUTLIER  = 300    # a diamond of equal area reads smaller; nudge up

# inches per data unit under the locked C4R layout, used for collision checks
_IPX = (c4r.AXES_RECT[2] * c4r.FIG_W_IN) / (XLIM[1] - XLIM[0])
_IPY = (c4r.AXES_RECT[3] * c4r.FIG_H_IN) / (YLIM[1] - YLIM[0])
_MIN_SEP = 2 * np.sqrt(S_CLOUD / np.pi) / 72 * 1.05   # marker dia + a sliver


def _min_sep(x, y, fixed):
    """Smallest center-to-center distance in inches, incl. the fixed points."""
    pts = np.vstack([np.column_stack([x * _IPX, y * _IPY]),
                     np.column_stack([fixed[:, 0] * _IPX, fixed[:, 1] * _IPY])])
    d = np.hypot(*(pts[:, None, :] - pts[None, :, :]).T)
    np.fill_diagonal(d, np.inf)
    return d.min()


def x_normalized(mode=None, cloud=CLOUD_17):
    """Return the cloud with x replaced by normal quantiles; y untouched."""
    mode = mode or X_MODE
    params = X_VARIANTS[mode]
    if params is None:
        return cloud.copy()
    mean, sd = params
    y = cloud[:, 1]
    n = len(cloud)

    # Normal quantiles -> an essentially exact normal marginal in x.
    xs = mean + sd * stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n)
    order = np.argsort(cloud[:, 0])          # preserve left-right rank order
    x = np.empty(n)
    x[order] = xs

    # Fix marker collisions by SWAPPING x assignments (the x set is preserved,
    # so this cannot change the distribution).
    fixed = ORIGINAL_3[[i for i in range(len(ORIGINAL_3)) if i != OUTLIER_IDX]]
    for _ in range(200):
        if _min_sep(x, y, fixed) >= _MIN_SEP:
            break
        best, swap = _min_sep(x, y, fixed), None
        pts = np.column_stack([x * _IPX, y * _IPY])
        d = np.hypot(*(pts[:, None, :] - pts[None, :, :]).T)
        np.fill_diagonal(d, np.inf)
        i, j = np.unravel_index(np.argmin(d), d.shape)
        for k in range(n):
            for m in (i, j):
                xt = x.copy()
                xt[m], xt[k] = xt[k], xt[m]
                s = _min_sep(xt, y, fixed)
                if s > best:
                    best, swap = s, (m, k)
        if swap is None:
            break
        m, k = swap
        x[m], x[k] = x[k], x[m]

    return np.column_stack([x, y])


# --------------------------------------------------------------------------
# FIGURES
# --------------------------------------------------------------------------
def bare_axes(ax):
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_xticks([])
    ax.set_yticks([])


def figure_a(path, color=c4r.BLUE):
    fig, ax = c4r.new_figure()
    bare_axes(ax)
    ax.scatter(ORIGINAL_3[:, 0], ORIGINAL_3[:, 1], s=S_ORIGINAL,
               color=color, edgecolors="none", zorder=4)
    c4r.style_axes(ax, grid_axis=None)
    c4r.save(fig, path)


def figure_b(path, cloud=None, orig_color=c4r.BLUE, cloud_color=c4r.BLACK,
             cloud_edge=None, cloud_size=None):
    cloud = x_normalized() if cloud is None else cloud
    fig, ax = c4r.new_figure()
    bare_axes(ax)

    ax.scatter(cloud[:, 0], cloud[:, 1], s=(cloud_size or S_CLOUD),
               facecolors=cloud_color,
               edgecolors=(cloud_edge or "none"),
               linewidths=(2.0 if cloud_edge else 0), zorder=3)

    keep = [i for i in range(len(ORIGINAL_3)) if i != OUTLIER_IDX]
    ax.scatter(ORIGINAL_3[keep, 0], ORIGINAL_3[keep, 1], s=S_ORIGINAL,
               color=orig_color, edgecolors="none", zorder=4)

    ox, oy = ORIGINAL_3[OUTLIER_IDX]
    ax.scatter([ox], [oy], s=S_OUTLIER, marker="D", color=c4r.ORANGE,
               edgecolors="none", zorder=5)

    c4r.style_axes(ax, grid_axis=None)
    c4r.save(fig, path)


if __name__ == "__main__":
    figure_a("out/outlier_n3.png")
    figure_b("out/outlier_n20.png")
    # Alternative: hollow black rings (lighter on the page, but they fill with
    # the slide background, so they read fainter when projected).
    figure_b("out/outlier_n20_hollow.png", cloud_color="none",
             cloud_edge=c4r.BLACK)
