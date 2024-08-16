"""
create_fig6_augmented.py
Creates Figure 6 in the paper, which demonstrates a `supervised`
application of DR to classify external spectra.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from classify_external_spectra import extract_spectrum_ivar
from create_fig2_embedding import MARKER_DF

# ----------------------------------------------
# Loading data

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]
classes = fl["classifications"]
class_code = np.array([cl[:2] if cl != "WD+MS" else "WM" for cl in classes])

fl = np.load("../data/embeddings_with_sdss.npz", allow_pickle=True)
sdss_names = fl["sdss_names"]
embeddings = fl["embeddings"]

sdss_sample_df = pd.read_csv("../data/sdss_spectra/sdss_sample_table.csv")
assert sdss_sample_df["WD"].to_list() == sdss_names.tolist()  # Ensuring ordering

# ----------------------------------------------

fg, axs = plt.subplots(
    5,
    3,
    figsize=(13, 10),
    gridspec_kw={"hspace": 0, "wspace": 0, "height_ratios": [4, 1, 0.1, 4, 1]},
)

# ----------------------------------------------
# Plotting the projected SDSS spectra onto the DESI EDR embedding

for ax, embedding, sdss_cl, sdss_name in zip(
    axs[::3, :].flatten(),
    embeddings,
    sdss_sample_df["SpClass"],
    sdss_sample_df["WD"],
):
    for cl in np.unique(class_code):
        mask = class_code == cl
        marker = MARKER_DF.loc[cl]
        ax.scatter(
            embedding[:-1, 0][mask],
            embedding[:-1, 1][mask],
            s=4,
            c=marker["c"],
            alpha=0.4,
        )
    sdss_marker = MARKER_DF.loc[sdss_cl[:2]]
    ax.plot(
        embedding[-1, 0],
        embedding[-1, 1],
        marker=sdss_marker["marker"],
        c=sdss_marker["c"],
        markeredgecolor="k",
        markeredgewidth=3,
        markersize=12,
    )
    ax.set_xticks([])
    ax.set_yticks([])

# ----------------------------------------------
# Plotting the SDSS spectra

SPEC_YLIMS = [[1, 26], [2, 42], [5, 31], [-2, 8], [2, 11], [0, 57]]
for ax, sdss_name, sdss_cl, ylims in zip(
    axs[1::3, :].flatten(), sdss_sample_df["WD"], sdss_sample_df["SpClass"], SPEC_YLIMS
):
    sdss_flux, _ = extract_spectrum_ivar(sdss_name)
    ax.plot(wlen, sdss_flux, c=MARKER_DF.loc[sdss_cl[:2]]["c"], lw=0.7)
    ax.set_title(f"{sdss_name[2:]}\n{sdss_cl}", fontsize=11, loc="right", x=0.98, y=0.4)

    ax.set_xlim(3800, 6900)
    ax.tick_params(
        axis="x", which="both", labelsize=11, direction="in", top=True, length=4
    )
    ax.set_yticks([])
    ax.set_ylim(ylims)

# ----------------------------------------------
# Aesthetics

for ax in axs[1::3, 0].flatten():
    ax.set_ylabel("Flux", fontsize=16)

for ax in axs[1, :].flatten():
    ax.set_xticklabels([])

for ax in axs[2, :]:
    ax.axis("off")

axs[4, 1].set_xlabel("Wavelength [Å]", fontsize=16)


fg.savefig("../tex/figures/fig6_augmented.pdf", dpi=300, bbox_inches="tight")
