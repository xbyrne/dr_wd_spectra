"""
create_fig4_He_line.py
Creates Figure 4 in the paper, demonstrating the isolation of spectra with He lines
"""

import numpy as np
import matplotlib.pyplot as plt
import preprocessing as pp
from create_fig2_embedding import MARKER_DF

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]
classes = fl["classifications"]

fl = np.load("../data/embedding_DB.npz", allow_pickle=True)
embedding = fl["embedding"]

fg, axs = plt.subplots(
    4, 1, figsize=(6, 12), gridspec_kw={"hspace": 0.0, "height_ratios": [2, 1, 1, 1]}
)

# ------------------------------
# Embedding
ax = axs[0]

isDB = np.array(["B" in c for c in classes])
ax.scatter(embedding[~isDB, 0], embedding[~isDB, 1], c="k", s=8)
ax.scatter(embedding[isDB, 0], embedding[isDB, 1], c="b", s=8)

ax.set_xticks([])
ax.set_yticks([])

handles = []
handles.append(
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="b",
        markersize=7,
        label="DB, DAB, ...",
    )
)
handles.append(
    plt.Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        markerfacecolor="k",
        markersize=7,
        label="Non-DB",
    )
)
ax.legend(handles=handles, fontsize=12)

# ------------------------------
# Example DB spectra
ax = axs[1]

wlen_mask = (wlen > 5500) & (wlen < 6100)
eg_DBs = [2503, 536, 1608]

for j, i in enumerate(eg_DBs):
    cl = classes[i]
    pp_spectrum = pp.meanstd(
        pp.interp_if_snr_low(wlen[wlen_mask], flux[i][wlen_mask], ivar[i][wlen_mask])
    )
    ax.plot(
        wlen[wlen_mask],
        pp_spectrum - j * 4,
        lw=0.5,
        c=MARKER_DF.loc[cl[:2]]["c"],
    )
    ax.annotate(
        cl,
        xy=(6095, -j * 4 + 0.7),
        fontsize=12,
        ha="right",
        xytext=(0, 0),
        textcoords="offset points",
    )

ax.set_title("Example DB spectra", fontsize=16, y=0.8)
ax.set_ylim(-12, 6)

# ------------------------------
# False positives?
ax = axs[2]

eg_FPs = [3347, 1170, 2759]

for j, i in enumerate(eg_FPs):
    cl = classes[i]
    pp_spectrum = pp.meanstd(
        pp.interp_if_snr_low(wlen[wlen_mask], flux[i][wlen_mask], ivar[i][wlen_mask])
    )
    ax.plot(
        wlen[wlen_mask],
        pp_spectrum - j * 5,
        lw=0.5,
        c=MARKER_DF.loc[cl[:2]]["c"],
    )
    ax.annotate(
        cl,
        xy=(6095, -j * 6 + 3),
        fontsize=12,
        ha="right",
        xytext=(0, 0),
        textcoords="offset points",
    )

ax.set_title("False positives", fontsize=16, y=0.8)
ax.set_ylim(-15, 7)

# ------------------------------
# False negatives
ax = axs[3]

eg_FNs = [1844, 2013, 3462]

for j, i in enumerate(eg_FNs):
    cl = classes[i]
    pp_spectrum = pp.meanstd(
        pp.interp_if_snr_low(wlen[wlen_mask], flux[i][wlen_mask], ivar[i][wlen_mask])
    )
    ax.plot(
        wlen[wlen_mask],
        pp_spectrum - j * 5,
        lw=0.5,
        c=MARKER_DF.loc[cl[:2]]["c"],
    )
    ax.annotate(
        cl,
        xy=(6095, -j * 5),
        fontsize=12,
        ha="right",
        xytext=(0, 0),
        textcoords="offset points",
    )

ax.set_title("False negatives", fontsize=16, y=0.8)
ax.set_ylim(-15, 6)

# ------------------------------
# Aesthetics
for ax in axs[1:]:
    ax.set_xlim(5500, 6100)
    ax.set_yticks([])
    ax.tick_params(axis="x", top=True, direction="in", labelsize=12, length=5)
    ax.axvline(5875.6, c="k", ls="--", lw=1, alpha=0.5)

for ax in axs[1:3]:
    ax.set_xticklabels([])

axs[3].set_xlabel("Wavelength [Å]", fontsize=16)
axs[2].set_ylabel("Flux [arbitrary]", fontsize=16)

fg.savefig("../tex/figures/fig4_He_line.pdf", bbox_inches="tight")
