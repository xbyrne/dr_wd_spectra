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

    print("Applying dimensionality reductions...")
    pp_flux = pp.meanstd(pp.interp_if_snr_low(wlen, flux, ivar))
    embedding_full = reduce(pp_flux)

    He_line_mask = (wlen > 5500) & (wlen < 6100)
    pp_flux = pp.meanstd(
        pp.interp_if_snr_low(
            wlen[He_line_mask], flux[:, He_line_mask], ivar[:, He_line_mask]
        )
    )
    embedding_DB = reduce(pp_flux)

    CV_line_mask = (
        ((wlen > 4300) & (wlen < 4400))
        | ((wlen > 4800) & (wlen < 4900))
        | ((wlen > 6500) & (wlen < 6600))
    )
    pp_flux = pp.meanstd(
        pp.interp_if_snr_low(
            wlen[CV_line_mask], flux[:, CV_line_mask], ivar[:, CV_line_mask]
        )
    )
    embedding_CV = reduce(pp_flux)

    print("Saving...")
    np.savez_compressed(
        "../data/embedding_full.npz", names=names, embedding=embedding_full
    )
    np.savez_compressed("../data/embedding_DB.npz", names=names, embedding=embedding_DB)
    np.savez_compressed("../data/embedding_CV.npz", names=names, embedding=embedding_CV)
