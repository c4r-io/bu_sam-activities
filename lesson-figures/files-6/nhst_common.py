"""
nhst_common.py — shared geometry and semantics for the C4R power / NHST figures.

Every figure in this set (H0 with rejection regions, Ha with power, and the
future combined overlay) imports this module. Anything that MUST agree between
the panels lives here and nowhere else, so the panels cannot drift apart:

    * the distributions          (SIGMA, MU_NULL, MU_ALT)
    * the decision threshold     (X_CRIT, derived from ALPHA)
    * the axes                   (XLIM, YLIM, XTICKS, YTICKS, labels)
    * the color -> quantity map  (alpha / beta / power)
    * the wording of shared labels

COLOR SEMANTICS
---------------
The set shows three quantities, so it uses the guide's three-category palette,
c4r.THREE_CAT == [PURPLE, ORANGE, BLUE], in its natural reading order:

    alpha (Type I error)   -> PURPLE
    beta  (Type II error)  -> ORANGE
    power (1 - beta)       -> BLUE

This keeps each quantity the same color in the standalone panels AND in the
combined overlay, where all three appear at once. Region fills are OPAQUE tints
of those brand hexes rather than alpha washes: the guide exports transparent
PNGs, so a semi-transparent fill would pick up whatever slide background it
landed on, and overlapping regions in the combined figure would multiply into
colors that are in no palette.

The threshold lines are BLACK ("text / lines / ink" in the guide) and the
distribution outlines are black or dark grey, so the only hues in any panel are
the quantities being compared. The two curves are told apart by weight and by
grey-vs-black rather than by hue -- see CURVE IDENTITY below.
"""

import re

import matplotlib
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

import c4r_style as c4r

# --------------------------------------------------------------------------
# DISTRIBUTIONS AND TEST
# --------------------------------------------------------------------------
SIGMA = 2.0        # standard error of the difference (Hz); peak density 0.199
MU_NULL = 0.0      # H0: no difference between groups
MU_ALT = 3.5       # Ha: true difference of 3.5 Hz

ALPHA = 0.05       # two-tailed
Z_CRIT = 1.959964  # two-tailed z for ALPHA = 0.05
X_CRIT = Z_CRIT * SIGMA   # critical values at +/- 3.92 Hz

# --------------------------------------------------------------------------
# AXES (identical in every panel so the plots stack and overlay exactly)
# --------------------------------------------------------------------------
XLIM = (-10.0, 10.0)
# Headroom above the 0.20 gridline so the H0 / Ha peak labels have somewhere to
# sit without being clipped. Shared, so both peaks land at the same height.
YLIM = (0.0, 0.23)
XTICKS = [-10, -5, 0, 5, 10]
YTICKS = [0.00, 0.05, 0.10, 0.15, 0.20]

XLABEL = "Difference in Firing Rate (Hz)"
YLABEL = "Probability"

# --------------------------------------------------------------------------
# COLORS
# --------------------------------------------------------------------------
TINT = 0.38        # tint strength for large regions (beta, power)
TINT_SMALL = 0.55  # small regions (the alpha tails) need more saturation to read


def tint(color, strength=TINT):
    """Opaque tint of a brand color: blend toward white.

    strength = 1.0 -> the full brand color, 0.0 -> white. Used instead of alpha
    so a region looks the same on any slide background and so overlapping
    regions in the combined figure stay on-palette.
    """
    r, g, b = mcolors.to_rgb(color)
    return tuple(c + (1 - c) * (1 - strength) for c in (r, g, b))


COLOR_ALPHA, COLOR_BETA, COLOR_POWER = c4r.THREE_CAT   # PURPLE, ORANGE, BLUE
FILL_ALPHA = tint(COLOR_ALPHA, TINT_SMALL)
FILL_BETA = tint(COLOR_BETA)
FILL_POWER = tint(COLOR_POWER)

CURVE_LW = 2.6     # distribution outline
CRIT_LW = 2.0      # critical-value line, where it is the active threshold
CENTER_LW = 1.8    # stem from the axis to a distribution's peak

# CURVE IDENTITY
# --------------
# H0 is drawn in the guide's dark grey at slightly lighter weight, Ha in black.
# The overlay needs the two curves told apart by something other than position,
# and hue is unavailable: all three palette colors are committed to quantities
# (alpha / beta / power), so a colored curve would read as one of those regions.
# Grey-vs-black stays inside the guide's ink vocabulary, collides with nothing,
# and survives greyscale printing -- and unlike adding a fourth hue it doesn't
# make the purple/blue pair harder for colorblind readers.
#
# The convention is applied in EVERY figure, not just the overlay, so a curve
# never changes appearance between figures: grey means H0 throughout, and a
# reader arrives at the overlay already knowing that.
CURVE_STYLE_NULL = dict(color=c4r.DARK_GRAY, linewidth=2.2)
CURVE_STYLE_ALT = dict(color=c4r.BLACK, linewidth=CURVE_LW)


def curve_style(mu):
    """Line style for the distribution centered on mu (see CURVE IDENTITY)."""
    return CURVE_STYLE_NULL if mu == MU_NULL else CURVE_STYLE_ALT

# --------------------------------------------------------------------------
# SHARED WORDING
# --------------------------------------------------------------------------
LABEL_ALPHA = "\u03b1 (Type I error)"
LABEL_BETA = "\u03b2 (Type II error)"
LABEL_POWER = "Power (probability of detection)"
LABEL_CRIT = "Critical value"

# Hypothesis labels are stored PLAIN ("H0", "Ha") and converted to mathtext when
# drawn, by mathify() below. Two reasons:
#   1. The guide's font has the subscript DIGITS (U+2080..) but no subscript
#      letter a (U+2090), so "Ha" cannot be written as a literal glyph -- it
#      renders as a missing-glyph box. mathtext builds the subscript by scaling
#      the ordinary "a", so it needs no special glyph.
#   2. style_axes wraps titles at len(title) > 40. A mathtext title counts 42
#      characters for the same 39 rendered glyphs and would wrap spuriously, so
#      the string handed to style_axes has to be the plain one.
# H0 goes through mathtext too, even though its literal glyph exists: mathtext
# subscripts are larger and sit lower than the font's designed ones, and the two
# labels appear side by side in the stacked and overlay figures.
H0 = "H0"
HA = "Ha"

_MATHTEXT = {"H0": r"$H_0$", "Ha": r"$H_a$"}


def mathify(s):
    """Swap plain hypothesis labels for their mathtext equivalents.

    Word-bounded, so an ordinary word starting "Ha" (e.g. "Half") is untouched.
    """
    if not s:
        return s
    return re.sub(r"\bH([0a])\b", lambda m: _MATHTEXT["H" + m.group(1)], s)


def apply():
    """c4r.apply(), plus pointing mathtext at the guide's font.

    Called instead of c4r.apply() by every script in this set. Without this,
    mathtext would render the hypothesis labels in matplotlib's default DejaVu
    Sans, which does not match. Verified to reproduce the guide's semibold
    weight exactly: a plain "H" renders identically through either path.
    """
    c4r.apply()
    matplotlib.rcParams.update({
        "mathtext.fontset": "custom",
        "mathtext.default": "rm",        # upright, not italic
        "mathtext.rm": c4r.FONT_FAMILY,
        "mathtext.it": c4r.FONT_FAMILY,
        "mathtext.bf": c4r.FONT_FAMILY,
    })

TITLE_NULL_CURVE = f"Null Hypothesis: {H0}"
TITLE_ALT_CURVE = f"Alternative Hypothesis: {HA}"
TITLE_NULL_REJECTION = f"Null Hypothesis: {H0} (rejection regions)"
TITLE_ALT_POWER = f"Alternative Hypothesis: {HA} (with power)"

NOTE_NULL = "No difference\nbetween groups"
NOTE_ALT = f"True difference\n= {MU_ALT:g} Hz"


# --------------------------------------------------------------------------
# DRAWING HELPERS
# --------------------------------------------------------------------------
def normal_pdf(x, mu, sigma=SIGMA):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def x_grid(n=2001):
    """x samples across XLIM that include both critical values EXACTLY, so
    shaded regions meet on a clean edge instead of the nearest sample point."""
    x = np.linspace(XLIM[0], XLIM[1], n)
    return np.unique(np.concatenate([x, [-X_CRIT, X_CRIT]]))


def draw_curve(ax, mu, zorder=5):
    """Outline of the sampling distribution centered on mu.

    Grey for H0, black for Ha -- see CURVE IDENTITY above.
    """
    x = x_grid()
    ax.plot(x, normal_pdf(x, mu), zorder=zorder, solid_capstyle="round",
            **curve_style(mu))


def draw_critical_lines(ax, upper=True, lower=True, faint=(), label=None):
    """Dashed black threshold lines at +/- X_CRIT.

    faint : which of ('upper', 'lower') to de-emphasize. Kept for one-tailed
            variants; the figures in this set draw both lines at full weight,
            since under a two-tailed test both are real boundaries and a
            threshold that changes appearance between panels would undercut the
            shared x-axis.
    label : legend text for the first prominent line drawn.
    """
    todo = ([("upper", X_CRIT)] if upper else []) + \
           ([("lower", -X_CRIT)] if lower else [])
    labelled = False
    for which, xpos in todo:
        is_faint = which in faint
        kw = dict(color=c4r.BLACK, linestyle=c4r.BESTFIT_STYLE)
        if is_faint:
            kw.update(linewidth=1.0, alpha=0.45, zorder=3)
        else:
            kw.update(linewidth=CRIT_LW, zorder=4)
            if label and not labelled:
                kw["label"] = label
                labelled = True
        ax.axvline(xpos, **kw)


def peak_label(ax, mu, text, stem=False, dx=0.0):
    """Label a distribution at its peak, optionally with a stem to the axis.

    The stem marks the value the distribution is centered on. Skip it if that
    value sits so close to the critical value that the solid stem and the
    dashed threshold would visually merge.

    dx : nudge the text sideways, in Hz, to clear a nearby threshold line.
         The label is only ~0.7 Hz wide, so a peak within half a unit of the
         threshold needs a nudge even when the stem itself reads cleanly.
    """
    peak = normal_pdf(np.array([mu]), mu)[0]
    if stem:
        # The mean line is part of its distribution's mark, so it takes that
        # curve's color. The text stays black: all type is black in the guide.
        ax.vlines(mu, 0, peak, colors=curve_style(mu)["color"],
                  linewidth=CENTER_LW, zorder=4)
    ax.text(mu + dx, peak + 0.006, mathify(text), ha="center", va="bottom",
            fontsize=c4r.FONT_SIZES["annotation"], color=c4r.BLACK, zorder=6)


def corner_note(ax, text):
    """Two-line note in the empty top-left of the plot.

    The original figures carried this as a subtitle under the title; the guide's
    locked layout leaves no room between title and axes. Two lines keep the
    block clear of the lower critical-value line, which a single line would run
    straight through at annotation size.
    """
    ax.text(0.015, 0.98, text, transform=ax.transAxes, ha="left", va="top",
            linespacing=1.35, fontsize=c4r.FONT_SIZES["annotation"],
            color=c4r.BLACK, zorder=6)


def _wants_legend(ax, legend):
    """Resolve legend=True/False/"auto"; "auto" means show one iff something
    on the axes carries a label. Bare panels then need no special-casing."""
    if legend == "auto":
        return bool(ax.get_legend_handles_labels()[0])
    return bool(legend)


def finish(ax, title, legend="auto"):
    """Lock the axes to the shared grid, then apply the guide's finishing.

    Figures with no shaded regions or thresholds get no legend. The plot
    rectangle stays locked either way, so the reserved legend strip simply sits
    empty and the x-axis still matches every other figure in the set.
    """
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_xticks(XTICKS)
    ax.set_yticks(YTICKS)
    ax.set_yticklabels([f"{t:.2f}" for t in YTICKS])
    c4r.style_axes(ax, xlabel=XLABEL, ylabel=YLABEL, title=title,
                   grid_axis="both", legend=_wants_legend(ax, legend))
    ax.title.set_text(mathify(ax.title.get_text()))


def area(mu, lo, hi):
    """Numeric area under the N(mu, SIGMA) density between lo and hi."""
    fine = np.linspace(lo, hi, 400001)
    return float(np.trapezoid(normal_pdf(fine, mu), fine))


# --------------------------------------------------------------------------
# SHADED REGIONS
# --------------------------------------------------------------------------
# One definition per quantity, used by the standalone panels, the stacked
# figure and the overlay, so a region can never be drawn one way in one figure
# and another way in the next. zorder is a parameter because the overlay has to
# stack these deliberately: alpha is a thin sliver that sits inside the much
# taller power region and must be drawn last to stay visible.
def fill_rejection(ax, mu=MU_NULL, label=LABEL_ALPHA, zorder=2):
    """Both tails beyond +/- X_CRIT: the rejection regions, alpha."""
    x = x_grid()
    y = normal_pdf(x, mu)
    ax.fill_between(x, 0, y, where=(x >= X_CRIT), facecolor=FILL_ALPHA,
                    edgecolor="none", zorder=zorder, label=label)
    ax.fill_between(x, 0, y, where=(x <= -X_CRIT), facecolor=FILL_ALPHA,
                    edgecolor="none", zorder=zorder)


def fill_power(ax, mu=MU_ALT, label=LABEL_POWER, zorder=2):
    """Area in EITHER rejection region: the effect is detected.

    The test is two-tailed, so a result past the lower threshold rejects H0 as
    well. Under this Ha that lower piece is ~0.002% of the area and invisible,
    but including it is what makes the thresholds mean the same thing in every
    panel: beta stops at both lines rather than running through the lower one.
    """
    x = x_grid()
    ax.fill_between(x, 0, normal_pdf(x, mu),
                    where=(x >= X_CRIT) | (x <= -X_CRIT),
                    facecolor=FILL_POWER, edgecolor="none", zorder=zorder,
                    label=label)


def fill_beta(ax, mu=MU_ALT, label=LABEL_BETA, zorder=2):
    """Area between the two thresholds: the effect is missed."""
    x = x_grid()
    ax.fill_between(x, 0, normal_pdf(x, mu),
                    where=(x >= -X_CRIT) & (x <= X_CRIT),
                    facecolor=FILL_BETA, edgecolor="none", zorder=zorder,
                    label=label)


def power_beta(mu=MU_ALT):
    """(power, beta) under N(mu) for the two-tailed test. They sum to 1."""
    power = area(mu, X_CRIT, 60) + area(mu, -60, -X_CRIT)
    return power, area(mu, -X_CRIT, X_CRIT)


# --------------------------------------------------------------------------
# STACKED TWO-PANEL LAYOUT
# --------------------------------------------------------------------------
# The guide's locked rectangle is for one panel, so the stacked figure defines
# its own. It deliberately keeps the guide's LEFT EDGE and WIDTH (and so the
# legend strip at LEGEND_X), which means a given firing rate lands on the same
# pixel column in the stacked figure, the standalone panels and the overlay.
_STACK_H_IN = 10.2
_PANEL_H_IN = 3.6      # height of each panel
_GAP_IN = 1.00         # room between panels; the lower panel's title sits here,
                       # with more space above it than below so it reads as
                       # belonging to the panel underneath it
_BOT_IN = 1.04         # matches the guide's bottom margin (0.16 * 6.5)

STACK_FIGSIZE = (c4r.FIG_W_IN, _STACK_H_IN)
_L, _W = c4r.AXES_RECT[0], c4r.AXES_RECT[2]
_ph = _PANEL_H_IN / _STACK_H_IN
RECT_LOWER = [_L, _BOT_IN / _STACK_H_IN, _W, _ph]
RECT_UPPER = [_L, (_BOT_IN + _PANEL_H_IN + _GAP_IN) / _STACK_H_IN, _W, _ph]


def stacked_figure():
    """Figure with two x-aligned panels: (fig, ax_upper, ax_lower).

    The panels share the x-axis: only the lower one carries tick labels and the
    axis label, so a vertical read at any firing rate crosses both
    distributions at the same screen position.
    """
    fig = plt.figure(figsize=STACK_FIGSIZE)
    ax_up = fig.add_axes(RECT_UPPER)
    ax_lo = fig.add_axes(RECT_LOWER, sharex=ax_up)
    # This layout is deliberate, so tell c4r.save() not to re-tighten it. That
    # is exactly what the guide's marker means; the rectangle simply isn't the
    # single-panel one.
    ax_up._c4r_standard = True
    return fig, ax_up, ax_lo


def panel_legend(ax, rect):
    """The guide's legend, anchored to one panel's top instead of the figure's.

    style_axes(legend=True) hardcodes the anchor to the single-panel top edge,
    which would stack both panels' legends on top of each other. Everything
    else -- wrapping, single column, spacing -- is the guide's.
    """
    handles, labels = c4r._wrap_legend_labels(ax)
    ax.legend(handles, labels, loc="upper left",
              bbox_to_anchor=(c4r.LEGEND_X, rect[1] + rect[3]),
              bbox_transform=ax.figure.transFigure,
              ncol=1, borderaxespad=0.0, handlelength=1.4, labelspacing=0.8)


def finish_panel(ax, title, rect, xlabel=None, legend="auto"):
    """finish() for one panel of a stacked figure.

    Pass xlabel=None for an upper panel: it inherits the shared axis and its
    tick labels are hidden. The legend, if any, is anchored to this panel.
    """
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_xticks(XTICKS)
    ax.set_yticks(YTICKS)
    ax.set_yticklabels([f"{t:.2f}" for t in YTICKS])
    c4r.style_axes(ax, xlabel=xlabel, ylabel=YLABEL, title=title,
                   grid_axis="both", legend=False)
    ax.title.set_text(mathify(ax.title.get_text()))
    if xlabel is None:
        ax.tick_params(labelbottom=False)
    if _wants_legend(ax, legend):
        panel_legend(ax, rect)


# --------------------------------------------------------------------------
# PANEL COMPOSITIONS
# --------------------------------------------------------------------------
# Each function draws the CONTENT of one panel and nothing else; the caller
# supplies the axes and does the finishing, because a panel is laid out
# differently on its own than stacked. Defining each panel once means the H0
# rejection panel is identical whether it appears alone, above the bare Ha
# curve, or above the Ha power panel -- and the same for every other panel.
def panel_null_curve(ax):
    """H0 alone: curve and mean line, no shading and no thresholds."""
    draw_curve(ax, MU_NULL)
    peak_label(ax, MU_NULL, H0, stem=True)
    corner_note(ax, NOTE_NULL)


def panel_alt_curve(ax):
    """Ha alone: curve and mean line, no shading and no thresholds.

    The mean line is centered under the label here, matching H0. It has to be
    left out once a threshold is drawn, because mu sits 0.42 Hz from the
    critical value and the two lines merge at display size.
    """
    draw_curve(ax, MU_ALT)
    peak_label(ax, MU_ALT, HA, stem=True)
    corner_note(ax, NOTE_ALT)


def panel_null_rejection(ax):
    """H0 with both rejection regions shaded and the thresholds drawn."""
    fill_rejection(ax, MU_NULL)
    draw_critical_lines(ax, label=LABEL_CRIT)
    draw_curve(ax, MU_NULL)
    peak_label(ax, MU_NULL, H0)   # no mean line: that belongs to the bare panel
    corner_note(ax, NOTE_NULL)
    ax.text(0.98, 0.98, f"\u03b1 = {ALPHA:.2f}", transform=ax.transAxes,
            ha="right", va="top", fontsize=c4r.FONT_SIZES["annotation"],
            color=c4r.BLACK, zorder=6)


def panel_alt_power(ax):
    """Ha split by the thresholds into beta and power."""
    fill_power(ax, MU_ALT)
    fill_beta(ax, MU_ALT)
    draw_critical_lines(ax, label=LABEL_CRIT)
    draw_curve(ax, MU_ALT)
    peak_label(ax, MU_ALT, HA, dx=-0.45)
    corner_note(ax, NOTE_ALT)
