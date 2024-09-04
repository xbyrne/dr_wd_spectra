"""
subtract_continuum_reduce.py
Subtracts the continuum from the spectra, partially removing temperature information.
Also generates a t-SNE embedding of the continuum-subtracted spectra.
"""

from tqdm import tqdm

import numpy as np
from specutils.spectra import Spectrum1D
from specutils.fitting import fit_generic_continuum
from astropy import units as u

import preprocessing as pp
from reduce_spectra import reduce

# -----------------------------------------------------------------------------
print("Loading data...")

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
wavelengths = fl["wavelengths"]
fluxes = fl["fluxes"]
ivars = fl["ivars"]

# -----------------------------------------------------------------------------
print("Subtracting continuum...")

su_spectra = [
    Spectrum1D(
        spectral_axis=wavelengths * u.AA, flux=flux * u.Unit("erg cm-2 s-1 AA-1")
    )
    for flux in fluxes
]

continuum_subtracted = np.zeros_like(fluxes)
for i, spectrum in enumerate(tqdm(su_spectra)):
    continuum = fit_generic_continuum(spectrum)(spectrum.spectral_axis)
    continuum_subtracted[i] = spectrum.flux - continuum

# -----------------------------------------------------------------------------
print("Applying dimensionality reduction...")

preprocessed_spectra = pp.meanstd(
    pp.interp_if_snr_low(wavelengths, continuum_subtracted, ivars)
)
embedding = reduce(preprocessed_spectra)

# -----------------------------------------------------------------------------
print("Saving...")
np.savez_compressed(
    "../data/continuum_subtracted_spectra_embedding.npz",
    names=names,
    wavelengths=wavelengths,
    fluxes=continuum_subtracted,
    embedding=embedding,
)
