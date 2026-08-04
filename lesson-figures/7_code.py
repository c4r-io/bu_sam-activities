"""
remake_final.py — the two selected figures, rebuilt in C4R brand style.

  fig1_boxplot.png  : hollow box & whisker, Control vs. Treatment (no points)
  fig2_scatter.png  : scatter + group-colored trend lines, single origin tick

Values were read off the source screenshots; swap in the real arrays where
noted and the figures regenerate unchanged in style.

Run:  python remake_final.py
Out:  output/*.png  (transparent, DPI 200)
"""

import numpy as np
import c4r_style as c4r

c4r.apply()

BOX_XLABEL  = "Group"
BOX_YLABEL  = "Outcome"
SCAT_XLABEL = "Dose"
SCAT_YLABEL = "Response"


def five_number_sample(minimum, q1, median, q3, maximum, n=25):
    """Build an n-point sample whose min/Q1/median/Q3/max are exactly the
    values given. Interpolates the empirical quantile function at p = i/(n-1),
    the same convention numpy.percentile uses, so the summary is recovered
    exactly. Use only to reproduce a figure from a published five-number
    summary — with the raw data, pass it in directly.
    """
    p_known = [0.0, 0.25, 0.50, 0.75, 1.0]
    v_known = [minimum, q1, median, q3, maximum]
    return np.interp(np.linspace(0.0, 1.0, n), p_known, v_known)


def origin_tick(ax, label="0", dx=None, dy=None):
    """Replace the separate x=0 and y=0 tick labels with one shared label at
    the axes corner. Call AFTER set_xticks / set_yticks. Assumes both axes
    start at 0.

    dx/dy default to the same offsets matplotlib uses to place tick labels
    (tick length + pad), so the shared 0 lines up exactly with the x tick row
    and the y tick column instead of floating between them.
    """
    import matplotlib as _mpl
    rc = _mpl.rcParams
    if dx is None:
        dx = -(rc["ytick.major.size"] + rc["ytick.major.pad"])
    if dy is None:
        dy = -(rc["xtick.major.size"] + rc["xtick.major.pad"])
    ax.set_xticks([t for t in ax.get_xticks() if t != 0])
    ax.set_yticks([t for t in ax.get_yticks() if t != 0])
    ax.annotate(label, xy=(0, 0), xycoords="data",
                xytext=(dx, dy), textcoords="offset points",
                ha="right", va="top",
                fontsize=c4r.FONT_SIZES["tick"], color=c4r.BLACK,
                annotation_clip=False)
    return ax


# ==========================================================================
# FIGURE 1 — box & whisker, Control vs. Treatment
# ==========================================================================
# Five-number summaries read off the source screenshot.
control_box   = five_number_sample(0.60, 1.20, 2.40, 3.55, 4.45)
treatment_box = five_number_sample(1.90, 2.60, 4.00, 5.05, 5.80)

fig, ax = c4r.new_figure()                     # locked 13 x 6.5 in plot area
c4r.boxplot(ax, [control_box, treatment_box],
            labels=["Control", "Treatment"],
            colors=c4r.TWO_STATE)              # BLUE = A, ORANGE = B
ax.set_ylim(0, 8)
ax.set_yticks(np.arange(0, 9, 2))
c4r.style_axes(ax, xlabel=BOX_XLABEL, ylabel=BOX_YLABEL, grid_axis="y")
c4r.save(fig, "output/fig1_boxplot.png")


# ==========================================================================
# FIGURE 2 — scatter with group-colored lines of best fit
# ==========================================================================
# Points read off the source screenshot (16 per group).
x_pts = np.array([0.40, 0.75, 1.10, 1.50, 1.85, 2.20, 2.60, 2.95,
                  3.30, 3.70, 4.10, 4.50, 4.90, 5.30, 5.70, 6.20])

# Residuals about each group's trend: Control y = 0.59x + 0.95,
# Treatment y = 0.63x + 2.05.
ctrl_resid = np.array([ 0.02, -0.16,  0.34,  0.08, -0.22,  0.30, -0.10,  0.16,
                        0.28, -0.30,  0.10, -0.14,  0.22, -0.26,  0.14, -0.12])
trt_resid  = np.array([-0.10,  0.28, -0.20,  0.14,  0.32, -0.18,  0.24, -0.28,
                        0.10,  0.20, -0.14,  0.26, -0.22,  0.08, -0.30,  0.18])

y_control   = 0.59 * x_pts + 0.95 + ctrl_resid
y_treatment = 0.63 * x_pts + 2.05 + trt_resid

fig, ax = c4r.new_figure()
ax.scatter(x_pts, y_control,   color=c4r.BLUE,   s=90, zorder=3,
           edgecolors="none", label="Control")
ax.scatter(x_pts, y_treatment, color=c4r.ORANGE, s=90, zorder=3,
           edgecolors="none", label="Treatment")

# Trend lines colored to match their group. This departs from the spec's
# black-annotation rule, which is ambiguous when a scatter has >1 group.
for y, c in ((y_control, c4r.BLUE), (y_treatment, c4r.ORANGE)):
    coeffs = np.polyfit(x_pts, y, 1)
    xs = np.array([x_pts.min(), x_pts.max()])
    ax.plot(xs, np.polyval(coeffs, xs), c4r.BESTFIT_STYLE, color=c,
            lw=c4r.BESTFIT_LW + 0.5, zorder=2)

ax.set_xlim(0, 8)
ax.set_ylim(0, 8)
ax.set_xticks(np.arange(0, 9, 2))
ax.set_yticks(np.arange(0, 9, 2))
c4r.style_axes(ax, xlabel=SCAT_XLABEL, ylabel=SCAT_YLABEL,
               grid_axis="both", legend=True)
origin_tick(ax)                                # one shared 0 at the corner
c4r.save(fig, "output/fig2_scatter.png")

print("done")
