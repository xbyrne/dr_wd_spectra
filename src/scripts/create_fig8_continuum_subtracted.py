"""
create_fig8_continuum_subtracted.py
Creates Figure 8 in the paper, showing
the tSNE embedding of the continuum-subtracted spectra
Code mostly borrowed from create_fig2_embedding.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from create_fig2_embedding import MARKER_DF, create_legend_handles

fl = np.load("../data/continuum_subtracted_spectra_embedding.npz", allow_pickle=True)
names = fl["names"]
embedding = fl["embedding"]


fg, axs = plt.subplots(
    2,
    2,
    figsize=(12, 7),
    gridspec_kw={"wspace": 0.0, "hspace": 0.0, "height_ratios": [1, 0.05]},
)

# -----------------------------------------------------------------------------
# Colouring by primary classification
ax = axs[0, 0]

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
classes = fl["classifications"]
class_code = np.array([cl[:2] if cl != "WD+MS" else "WM" for cl in classes])
# eg. DA, ..., DZ, CV, WD+MS -> WM, WD, sd, EX, ST, UN

for cl in np.unique(class_code):
    mask = class_code == cl
    marker = MARKER_DF.loc[cl]
    if cl[0] == "D":
        s = 15
    else:
        s = 20
    ax.scatter(
        embedding[mask, 0],
        embedding[mask, 1],
        s=s,
        c=marker["c"],
        marker=marker["marker"],
    )

leg = ax.legend(
    handles=create_legend_handles(),
    bbox_to_anchor=(1.0, 0.0),
    fontsize=17,
    ncol=4,
    columnspacing=-0.5,
    frameon=False,
)
for i in [0, 8]:
    leg.get_texts()[i].set_weight("bold")  # Bold the headers
    leg.get_texts()[i].set_position((-17, 0))  # Move the headers to the left

for h in leg.legend_handles:
    h.set_data(
        [x + 20 for x in h.get_data()[0]],  # Move the markers to the left
        h.get_data()[1],
    )

ax.annotate(
    "(a)",
    xy=(0.02, 0.94),
    xycoords="axes fraction",
    fontsize=20,
)

# -------------------
# Temperature coding
ax = axs[0, 1]

gf19 = pd.read_csv("../data/gf19.csv", index_col=0)

teff_cmp = LinearSegmentedColormap.from_list(
    "temp", ["black", "red", "orange", "yellow", "yellow", "white"]
)
sc = ax.scatter(
    embedding[:, 0],
    embedding[:, 1],
    s=8,
    c=np.log10(gf19["TeffH"]),
    cmap=teff_cmp,
)

ax.annotate("(b)", xy=(0.02, 0.94), xycoords="axes fraction", fontsize=20)

cbar = fg.colorbar(sc, cax=axs[1, 1], orientation="horizontal")
cbar.set_label(r"$T_\text{eff}\; [10^3\,\text{K}]$", fontsize=20)
T_ticks = np.array(
    [
        4000,
        6000,
        8000,
        10000,
        20000,
        40000,
        60000,
        80000,
    ]
)
cbar.set_ticks(np.log10(T_ticks))
cbar.set_ticklabels([f"${int(T/1e3)}$" for T in T_ticks], fontsize=16)

# -------------------
# Aesthetic
for ax in axs[0, :]:
    # ax.set_xlabel("t-SNE 1", fontsize=20)
    ax.set_xticks([])
    ax.set_yticks([])

axs[1, 0].axis("off")

# -------------------
# Saving

fg.tight_layout()
fg.savefig("../tex/figures/fig8_continuum_subtracted.pdf", dpi=300, bbox_inches="tight")
