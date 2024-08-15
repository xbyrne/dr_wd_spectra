"""
create_fig5_CVs.py
Creates Figure 5 in the paper, isolating CVs.
"""

import numpy as np
import matplotlib.pyplot as plt

import preprocessing as pp

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]
classes = fl["classifications"]
isCV = classes == "CV"

fl = np.load("../data/embedding_CV.npz", allow_pickle=True)
embedding = fl["embedding"]

fg, axs = plt.subplots(
    2, 1, figsize=(7, 14), gridspec_kw={"hspace": 0.0, "height_ratios": [7, 7]}
)

# ------------------------------
# Embedding
ax = axs[0]
ax.scatter(
    embedding[isCV, 0],
    embedding[isCV, 1],
    c="#ffaf00",
    marker="x",
    s=150,
    lw=2,
)
ax.scatter(embedding[~isCV, 0], embedding[~isCV, 1], c="k", s=10)
ax.set_xticks([])
ax.set_yticks([])

handles = [
    plt.Line2D(
        [0],
        [0],
        marker="x",
        color="#ffaf00",
        lw=0,
        markersize=12,
        markeredgewidth=3,
        label="CV",
    ),
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="k",
        markersize=7,
        label="Other",
    ),
]
ax.legend(handles=handles, fontsize=18)

# ------------------------------
# Spectra
ax = axs[1]
ax.axvspan(4100, 4300, color="k", alpha=0.2, ec=None)
ax.axvspan(4400, 4800, color="k", alpha=0.2, ec=None)
ax.axvspan(4900, 6500, color="k", alpha=0.2, ec=None)
ax.axvspan(6600, 6800, color="k", alpha=0.2, ec=None)

for i, idx in enumerate(np.where(isCV)[0]):
    ax.plot(
        wlen,
        pp.meanstd(pp.interp_if_snr_low(wlen, flux[idx], ivar[idx])) + 3 * i,
        lw=1,
        c="#ffaf00",
    )

ax.set_xlim(4100, 6800)
ax.set_ylim(-2, 38)
ax.set_xlabel("Wavelength [Å]", fontsize=18)
ax.set_ylabel("Flux [arbitrary]", fontsize=18)
ax.set_yticks([])
ax.tick_params(axis="x", labelsize=14, top=True, direction="in", length=5)

fg.savefig("../tex/figures/fig5_CVs.pdf", dpi=300, bbox_inches="tight")
