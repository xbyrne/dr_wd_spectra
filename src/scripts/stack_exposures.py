"""
stack_exposures.py
Stacks the exposures for each source
"""

import numpy as np
from tqdm import tqdm


def stack_fluxes_ivars(fluxes, ivars):
    """
    Stacks the fluxes and ivars for a single source
    """
    stacked_fluxes = np.sum(fluxes * ivars, axis=0) / np.sum(ivars, axis=0)
    stacked_ivars = np.sum(ivars, axis=0)
    return stacked_fluxes, stacked_ivars


if __name__ == "__main__":
    print("Loading exposures...")
    fl = np.load("../data/exposures.npz", allow_pickle=True)

    names = fl["names"]
    wavelengths = fl["wavelengths"]
    exposure_fluxes = fl["fluxes"]
    exposure_ivars = fl["ivars"]
    classifications = fl["classifications"]

    UNIQUE_NAMES = np.unique(names)
    n_sources = len(UNIQUE_NAMES)

    combined_fluxes = np.zeros((n_sources, len(wavelengths)))
    combined_ivars = np.zeros_like(combined_fluxes)

    print("Stacking exposures...")
    for i, name in tqdm(enumerate(UNIQUE_NAMES), total=n_sources):
        combined_fluxes[i], combined_ivars[i] = stack_fluxes_ivars(
            exposure_fluxes[names == name], exposure_ivars[names == name]
        )

    unique_classifications = np.array(
        [classifications[names == name][0] for name in UNIQUE_NAMES]
    )

    print("Saving coadded spectra...")
    np.savez_compressed(
        "../data/coadded_spectra.npz",
        names=UNIQUE_NAMES,
        wavelengths=wavelengths,
        fluxes=combined_fluxes,
        ivars=combined_ivars,
        classifications=unique_classifications,
    )
