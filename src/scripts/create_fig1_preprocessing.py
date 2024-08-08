"""
create_fig1_preprocessing.py
Creates Figure 1 in the paper, which demonstrates the preprocessing steps.
"""

import numpy as np
import matplotlib.pyplot as plt
import preprocessing as pp

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]

i = 3399
original_spectrum = flux[i]

LW = 0.5
title_loc = [0.975, 0.75]
ypad = 100
snr_cut = 0.2
snr = np.abs(flux[i]) * np.sqrt(ivar[i])

fg, axs = plt.subplots(
    3, 1, figsize=(12, 6), gridspec_kw={"hspace": 0.0, "height_ratios": [2, 1, 2]}
)

ax = axs[0]
ax.plot(wlen, original_spectrum, c="k", lw=LW)
ax.set_ylim(-7, 29)
# ax.set_ylabel("Flux [$10^{-17}$ erg s$^{-1}$ cm$^{-2}$ Å$^{-1}$]", fontsize=20)
ax.set_ylabel("Flux [arb.]", fontsize=20)
ax.set_title(
    "Original",
    fontsize=20,
    x=title_loc[0],
    y=title_loc[1],
    loc="right",
)

ax = axs[1]
ax.plot(wlen, np.log10(snr), c="k", lw=LW)
ax.annotate(
    "S/N = 0.2",
    xy=(4700, np.log10(snr_cut) + 0.15),
    fontsize=14,
)
ax.axhspan(-1.1, np.log10(snr_cut), color="r", alpha=0.4, lw=0)
ax.axhline(np.log10(snr_cut), c="r", ls="-.", lw=1)
ax.set_ylabel(r"$\log(\text{S/N})$", fontsize=20)
ax.set_ylim(-1.1, 1.7)

ax = axs[2]
denoised_spectrum = pp.interp_if_snr_low(
    wlen, original_spectrum, ivar[i], snr_threshold=snr_cut
)
preprocessed_spectrum = pp.meanstd(denoised_spectrum)
ax.plot(wlen, preprocessed_spectrum, lw=LW, c="k")
ax.set_ylim(-1.7, 3.5)
ax.set_ylabel("Flux [arb.]", fontsize=20)
ax.set_title(
    "Denoised + Rescaled",
    fontsize=20,
    x=title_loc[0],
    y=title_loc[1],
    loc="right",
)
ax.set_xlabel("Wavelength [Å]", fontsize=20)
ax.axhline(0, c="k", ls="--", lw=1)

for ax in axs:
    ax.margins(-0.02)
    ax.tick_params(
        axis="both", which="major", top=True, right=True, direction="in", labelsize=16
    )

fg.align_ylabels(axs)

fg.tight_layout()
fg.savefig("../tex/figures/fig1_preprocessing.pdf", dpi=300)
