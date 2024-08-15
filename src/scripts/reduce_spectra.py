"""
reduce_spectra.py
Contains functionality to apply dimensionality reduction to the spectra.
"""

import numpy as np
from sklearn.manifold import TSNE
import preprocessing as pp


def reduce(spectra, random_state=0, wlen_mask=None):
    """
    Applies dimensionality reduction to the spectra.
    """
    tsne = TSNE(n_components=2, random_state=random_state)

    if wlen_mask is None:
        return tsne.fit_transform(spectra)
    return tsne.fit_transform(spectra[:, wlen_mask])


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

    print("Applying dimensionality reductions...")
    embedding_full = reduce(flux)

    He_line_mask = (wlen > 5800) & (wlen < 6200)
    embedding_DB = reduce(flux, wlen_mask=He_line_mask)

    CV_line_mask = (
        ((wlen > 4300) & (wlen < 4400))
        | ((wlen > 4800) & (wlen < 4900))
        | ((wlen > 6500) & (wlen < 6600))
    )
    embedding_CV = reduce(flux, wlen_mask=CV_line_mask)

    print("Saving...")
    np.savez_compressed(
        "../data/embedding_full.npz", names=names, embedding=embedding_full
    )
    np.savez_compressed("../data/embedding_DB.npz", names=names, embedding=embedding_DB)
    np.savez_compressed("../data/embedding_CV.npz", names=names, embedding=embedding_CV)
