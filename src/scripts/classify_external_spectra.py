"""
classify_external_spectra.py
Using DR as a tool to classify data external to the DESI EDR
"""

import numpy as np
import pandas as pd
from astropy.io import fits

import preprocessing as pp
from reduce_spectra import reduce

sdss_sample_df = pd.read_csv("../data/sdss_spectra/sdss_sample_table.csv")

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]
wlen = fl["wavelengths"]
flux = fl["fluxes"]
ivar = fl["ivars"]


def extract_spectrum_ivar(sdss_nm):
    """Extracts the spectrum and ivar from the SDSS FITS file."""
    filepath = f"../data/sdss_spectra/{sdss_nm}.fits"
    hdul = fits.open(filepath)
    spectrum_rec = hdul[1].data
    wlen_sdss = 10 ** spectrum_rec["loglam"]
    flux_sdss = spectrum_rec["flux"]
    ivar_sdss = spectrum_rec["ivar"]
    # Interpolate to the DESI wavelength grid
    flux_interp = np.interp(wlen, wlen_sdss, flux_sdss)
    ivar_interp = np.interp(wlen, wlen_sdss, ivar_sdss)
    return flux_interp, ivar_interp


def create_augmented_embedding(sdss_nm):
    """
    Creates an embedding of N+1 objects: the DESI EDR and the SDSS spectrum.
    The final object is the SDSS spectrum.
    """
    # Get SDSS spectrum
    sdss_flux, sdss_ivar = extract_spectrum_ivar(sdss_nm)
    # Append the SDSS spectrum to the DESI EDR
    flux_with_sdss = np.vstack([flux, sdss_flux])
    ivar_with_sdss = np.vstack([ivar, sdss_ivar])
    # Preprocess
    pp_flux = pp.meanstd(pp.interp_if_snr_low(wlen, flux_with_sdss, ivar_with_sdss))
    # Reduce dimensionality
    embedding = reduce(pp_flux)
    return embedding


if __name__ == "__main__":
    embeddings = np.zeros((len(sdss_sample_df), len(flux) + 1, 2))
    # Create an augmented embedding for each SDSS spectrum
    for i, sdss_name in enumerate(sdss_sample_df["WD"]):
        print(f"Creating embedding for {sdss_name}...")
        embeddings[i] = create_augmented_embedding(sdss_name)
    # Save the embeddings
    np.savez_compressed(
        "../data/embeddings_with_sdss.npz",
        sdss_names=sdss_sample_df["WD"],
        embeddings=embeddings,
    )
