"""
preprocessing.py
================
Contains functions for preprocessing the data.
"""

import numpy as np


def interp_if_snr_low(wlen, spectra, ivar, snr_threshold=0.2):
    """
    Interpolates over regions of low S/N.
    """
    snr = np.abs(spectra) * np.sqrt(ivar)
    low_snr = snr < snr_threshold
    if spectra.ndim == 1:
        return np.interp(wlen, wlen[~low_snr], spectra[~low_snr])
    return np.array(
        [
            np.interp(wlen, wlen[~mask], spectrum[~mask])
            for mask, spectrum in zip(low_snr, spectra)
        ]
    )


def meanstd(spectra):
    """
    Normalises (each) spectrum to have 0 mean and unit standard deviation.
    """
    if spectra.ndim == 1:
        return (spectra - np.mean(spectra)) / (np.std(spectra) + 1e-20)
    means = np.mean(spectra, axis=1)[..., None]
    stds = np.std(spectra, axis=1)[..., None] + 1e-20
    return (spectra - means) / stds
