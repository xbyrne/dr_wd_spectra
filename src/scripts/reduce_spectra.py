"""
reduce_spectra.py
Contains functionality to apply dimensionality reduction to the spectra.
"""

import numpy as np
from sklearn.manifold import TSNE
import preprocessing as pp


def reduce(spectra, random_state=0):
    """
    Applies dimensionality reduction to the spectra.
    """
    tsne = TSNE(n_components=2, random_state=random_state)
    return tsne.fit_transform(spectra)


if __name__ == "__main__":
    print("Loading data...")
    fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
    names = fl["names"]
    wlen = fl["wavelengths"]
    flux = fl["fluxes"]
    ivar = fl["ivars"]

    print("Preprocessing...")
    flux = pp.interp_if_snr_low(wlen, flux, ivar)
    flux = pp.meanstd(flux)

    print("Applying dimensionality reduction...")
    embedding = reduce(flux)

    print("Saving...")
    np.savez_compressed("../data/embedding.npz", names=names, embedding=embedding)
