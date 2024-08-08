"""
create_fig1_preprocessing.py
Creates Figure 1 in the paper, which demonstrates the preprocessing steps.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import preprocessing as pp

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]

fg, ax = plt.subplots(figsize=(12, 5))
i = 3330
original_spectrum = flux[i]

LW = 0.8

ax.plot(
    wlen - 40,
    flux[i] + 15,
    c="k",
    lw=LW,
    label="Original spectrum",
)

denoised_spectrum = pp.interp_if_snr_low(wlen, flux[i], ivar[i], snr_threshold=0.1)
arrow_x = 0.5
arrow_length = 0.15
arrow_width = 0.03
arrow = patches.Arrow(
    arrow_x,
    0.57,
    0,
    -arrow_length,
    width=arrow_width,
    color="k",
    transform=ax.transAxes,
)
ax.add_patch(arrow)

ax.plot(
    wlen,
    denoised_spectrum + 4,
    c="r",
    lw=LW,
    label="Denoised",
)

preprocessed_spectrum = pp.meanstd(denoised_spectrum)
arrow = patches.Arrow(
    arrow_x,
    0.25,
    0,
    -arrow_length,
    width=arrow_width,
    color="k",
    transform=ax.transAxes,
)
ax.add_patch(arrow)

ax.plot(
    wlen + 40,
    preprocessed_spectrum,
    c="b",
    lw=LW,
    label="Denoised + rescaled",
)
ax.axhline(0, c="k", ls="--", lw=1)

ax.legend(fontsize=18)
ax.tick_params(axis="both", which="major", labelsize=16)
ax.set_xlabel("Wavelength [Å]", fontsize=20)
ax.set_ylabel("Flux [arbitrary]", fontsize=20)
ax.set_ylim(-2, 29)
ax.margins(-0.02)

fg.tight_layout()
fg.savefig("../tex/figures/fig1_preprocessing.pdf", dpi=300)
