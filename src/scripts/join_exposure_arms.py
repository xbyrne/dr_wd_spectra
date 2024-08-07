"""
join_exposure_arms.py
For each exposure of a WD observed by DESI, this script joins the spectra of the three arms (b,r,z).
The output is a single file containing, for each exposure
- Object name (not unique as the same object can be observed multiple times)
- Exposure ID
- Date (why not)
- Wavelength
- Flux (I believe in units of 10^-17 erg/s/cm^2/Angstrom)
- Inverse variance (IVar; 1/sigma^2)
- Classification according to Manser+24
"""

import glob
import numpy as np
from tqdm import tqdm
from astropy.io import fits
from astropy.table import Table

## --------------------
## Load data

# Get list of exposure files
# [ ../data/Exposures/YYYYMMDD/JXXXXXX.XX-YYYYYY.YY_DESI_ID-YYYYMMDD-000EXPID-EXPTIME?-{brz}.dat ]
exposure_file_list = glob.glob("../data/Exposures/*/*.dat")
exposure_file_list.sort()
# len(exposure_file_list) = 95526
# 31842 exposures, each with 3 arms
# 31842 * 3 = 95526

# Get table with Manser+24 visual classifications
hdul = fits.open(
    "../data/DESI_EDR_WD_catalogue_online_data/THE_CATALOGUE/DESI_EDR_WD_catalogue_v1.fits"
)
classifications_table = Table(hdul[1].data)


def exposure_data_from_filename(filename):
    """
    Extracts the object name, exposure ID, and date from a DESI exposure filename.
    """
    basename = filename.split("/")[-1]
    J2000_name = basename.split("_")[0]
    expid = basename.split("-")[-3]
    date_yyyymmdd = basename.split("-")[-4]
    return J2000_name, expid, date_yyyymmdd


## --------------------
## Join arms for an exposure

# Arms have different lengths (different numbers of wavelength bins):
B_BINS = 2751
R_BINS = 2326
Z_BINS = 2881

# They also overlap in wavelength ranges
OVERLAP_BR = 51  # Overlapping wavelength bins between b and r
OVERLAP_RZ = 126  #      "        "         "     "    r and z

# |----------------------|
#                  |----------------------------------|
#                                               |-----------------------|
# |  B_BINS - OBR  | OBR |  R_BINS - OBR - ORZ  | ORZ |  Z_BINS - ORZ   |


def join_arms(b_fl, r_fl, z_fl):
    """
    Join the three arms of a DESI exposure.
    Inputs: paths to the three arms' files
    Outputs: flux and ivar arrays
    """
    b_data = np.loadtxt(b_fl)
    r_data = np.loadtxt(r_fl)
    z_data = np.loadtxt(z_fl)

    flux = np.zeros((B_BINS + R_BINS + Z_BINS - OVERLAP_BR - OVERLAP_RZ,))
    ivar = np.zeros_like(flux)

    # Non-overlapping regions
    # b
    flux[: B_BINS - OVERLAP_BR] = b_data[:-OVERLAP_BR, 1]
    ivar[: B_BINS - OVERLAP_BR] = b_data[:-OVERLAP_BR, 2]
    # r
    flux[B_BINS:-Z_BINS] = r_data[OVERLAP_BR:-OVERLAP_RZ, 1]
    ivar[B_BINS:-Z_BINS] = r_data[OVERLAP_BR:-OVERLAP_RZ, 2]
    # z
    flux[-Z_BINS + OVERLAP_RZ :] = z_data[OVERLAP_RZ:, 1]
    ivar[-Z_BINS + OVERLAP_RZ :] = z_data[OVERLAP_RZ:, 2]

    # Overlapping regions
    # b-r
    (
        flux[B_BINS - OVERLAP_BR : B_BINS],
        ivar[B_BINS - OVERLAP_BR : B_BINS],
    ) = combine_spectral_overlap(b_data[-OVERLAP_BR:, :], r_data[:OVERLAP_BR, :])
    # r-z
    (
        flux[-Z_BINS : -Z_BINS + OVERLAP_RZ],
        ivar[-Z_BINS : -Z_BINS + OVERLAP_RZ],
    ) = combine_spectral_overlap(r_data[-OVERLAP_RZ:, :], z_data[:OVERLAP_RZ, :])

    return flux, ivar


def combine_spectral_overlap(arm1, arm2):
    """
    Statistically combines the fluxes in overlapping spectral regions of two arms.
    arm1[:,1] and arm2[:,1] are the fluxes, and arm1[:,2] and arm2[:,2] are the ivars.
    """
    combined_fluxes = (arm1[:, 1] * arm1[:, 2] + arm2[:, 1] * arm2[:, 2]) / (
        arm1[:, 2] + arm2[:, 2]
    )
    combined_ivars = arm1[:, 2] + arm2[:, 2]
    return combined_fluxes, combined_ivars


## --------------------

if __name__ == "__main__":

    N_exposures = len(exposure_file_list) // 3

    names = np.zeros(N_exposures, dtype=object)
    exposure_ids = np.zeros(N_exposures, dtype=int)
    dates = np.zeros(N_exposures, dtype=object)
    classifications = np.zeros(N_exposures, dtype=object)

    for i in tqdm(range(N_exposures), total=N_exposures):
        b_file = exposure_file_list[i * 3]
        r_file = exposure_file_list[i * 3 + 1]
        z_file = exposure_file_list[i * 3 + 2]

        # Creating wavelength, flux, and ivar arrays on first iteration
        if i == 0:
            b_wlen = np.loadtxt(b_file)[:, 0]
            r_wlen = np.loadtxt(r_file)[OVERLAP_BR:, 0]
            z_wlen = np.loadtxt(z_file)[OVERLAP_RZ:, 0]

            wavelengths = np.concatenate([b_wlen, r_wlen, z_wlen])
            fluxes = np.zeros((N_exposures, len(wavelengths)))
            ivars = np.zeros_like(fluxes)

        name, exposure_id, date = exposure_data_from_filename(b_file)

        classification = classifications_table[
            classifications_table["wdj_name"] == f"WD{name}"
        ]["desi_sp_class"].value[0]
        classifications[i] = classification

        if classification == "NULL":
            # These objects were skipped by Manser+24, as they apparently
            # have no exposures with med[S/N] > 0.5 in any arm.
            # They will be removed from the output arrays file later
            continue

        names[i] = name
        exposure_ids[i] = exposure_id
        dates[i] = date

        fluxes[i], ivars[i] = join_arms(b_file, r_file, z_file)

    # Remove NULL objects
    poor_sn_mask = classifications == "NULL"

    names = names[~poor_sn_mask]
    exposure_ids = exposure_ids[~poor_sn_mask]
    dates = dates[~poor_sn_mask]
    fluxes = fluxes[~poor_sn_mask]
    ivars = ivars[~poor_sn_mask]
    classifications = classifications[~poor_sn_mask]

    np.savez_compressed(
        "../data/exposures.npz",
        names=names,
        exposure_ids=exposure_ids,
        dates=dates,
        wavelengths=wavelengths,
        fluxes=fluxes,
        ivars=ivars,
        classifications=classifications,
    )
