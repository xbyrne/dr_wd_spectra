"""
create_fig3_DZisland.py
Creates Figure 3 in the paper, which shows an island of polluted WDs.
"""

import numpy as np
import matplotlib.pyplot as plt

from create_fig2_embedding import MARKER_DF
from preprocessing import interp_if_snr_low, meanstd

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]
classes = fl["classifications"]

fl = np.load("../data/embedding_full.npz", allow_pickle=True)
embedding = fl["embedding"]

fg, axs = plt.subplots(
    3, 1, figsize=(5, 7), gridspec_kw={"hspace": 0.0, "height_ratios": [4, 2, 1]}
)

knowns = [1150, 2992]
DBZ = 2202

# ------------------------------
# Zoom in on the DZ island
ax = axs[0]

for spectral_class in [
    "DZ",
    "DB",
    "DC",
]:
    mask = np.array([cl[:2] == spectral_class for cl in classes])
    ax.scatter(
        embedding[mask, 0],
        embedding[mask, 1],
        s=40,
        c=MARKER_DF.loc[spectral_class]["c"],
        marker=MARKER_DF.loc[spectral_class]["marker"],
        label=spectral_class,
    )
for i in knowns:
    ax.scatter(
        embedding[i, 0],
        embedding[i, 1],
        s=60,
        c=MARKER_DF.loc[classes[i][:2]]["c"],
        marker=MARKER_DF.loc[classes[i][:2]]["marker"],
        lw=2,
        ec="k",
    )
ax.set_xlim(-1, 5)
ax.set_ylim(23, 26)
ax.set_xticks([])
ax.set_yticks([])
leg = ax.legend(loc="lower right", fontsize=12)
leg.get_texts()[0].set_text("DZ, DZA, ...")
leg.get_texts()[1].set_text("DBZ")

# ------------------------------
# Known Polluted WDs
ax = axs[1]

for j, (i, cl) in enumerate(zip(knowns + [DBZ], ["DZ", "DZ", "DB"])):
    normalised_spectrum = meanstd(interp_if_snr_low(wlen, flux[i], ivar[i]))
    ax.plot(wlen, normalised_spectrum - 3 * j, c=MARKER_DF.loc[cl]["c"], lw=1)
ax.set_ylim(-7, 3)

# ------------------------------
# The `DC`
ax = axs[2]

i = 3085
normalised_spectrum = meanstd(interp_if_snr_low(wlen, flux[i], ivar[i]))
ax.plot(wlen, normalised_spectrum, c=MARKER_DF.loc["DC"]["c"], lw=1)
ax.annotate(
    names[i], xy=(0.985, 0.1), xycoords="axes fraction", ha="right", fontsize=10
)
ax.set_ylim(-6, 6)

ax.set_xlabel("Wavelength [Å]", fontsize=16)

# ------------------------------
# Aesthetics

for ax in axs[1:]:
    ax.set_xlim(3875, 4125)
    ax.set_yticks([])
    ax.axvline(3933.66, c="k", ls="--", lw=1, alpha=0.5)
    ax.axvline(3968.47, c="k", ls="--", lw=1, alpha=0.5)
    ax.tick_params(axis="x", labelsize=12, top=True, direction="in")

axs[2].set_ylabel("Flux [arbitrary]", fontsize=16, y=1.5)

# ------------------------------
# Save
fg.savefig("../tex/figures/fig3_DZisland.pdf", bbox_inches="tight")
