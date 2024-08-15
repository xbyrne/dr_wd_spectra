"""
download_sdss_spectra.py
Downloads a random SDSS spectrum for each spectral class in the Gentile Fusillo+19 catalogue.
Used for demonstrating the application of DR to classify external spectra.
"""

import os
from urllib.error import HTTPError

import numpy as np
import pandas as pd
from astropy.io import fits
import pyvo as vo


# ------------------------------
# Select a random spectrum for each spectral class
def get_random_spectra_data():
    """
    Downloads a table containing a random spectrum in each of the following spectral classes:
    DA, DB, DC, DZ, DQ, DAO.
    If the table has already been downloaded, it is loaded from disk.
    Returns the table as a pandas DataFrame.
    """
    if os.path.exists("../data/sdss_spectra/sdss_sample_table.csv"):
        return pd.read_csv("../data/sdss_spectra/sdss_sample_table.csv")

    if not os.path.exists("../data/sdss_spectra"):
        print("Creating directory ../data/sdss_spectra to store SDSS spectra.")
        os.makedirs("../data/sdss_spectra")

    # Query the Gentile Fusillo+19 catalogue for a random spectrum of each spectral class
    spectral_classes = ["DA", "DB", "DC", "DZ", "DQ", "DAO"]
    tap_service = vo.dal.TAPService("http://tapvizier.u-strasbg.fr/TAPVizieR/tap")
    catalogue = "J/MNRAS/482/4570/gaiasdss"  # Gentile Fusillo+19 with spectral classes

    np.random.seed(0)
    sdss_table = pd.DataFrame()
    for spectral_class in spectral_classes:
        query = f"""
        SELECT WD, Plate, MJD, Fiber, \"S/N\", SpClass
        FROM \"{catalogue}\"
        WHERE SpClass = '{spectral_class}'
        """
        result = tap_service.search(query)
        # Choose a random row from the result
        random_selection = result.to_table().to_pandas().sample(1)
        sdss_table = pd.concat([sdss_table, random_selection])

    sdss_table.to_csv("../data/sdss_spectra/sdss_sample_table.csv", index=False)
    return sdss_table


def download_sdss_spectrum(sdss_table_row):
    """
    Downloads an SDSS spectrum given the plate, MJD, and fiber number.
    Saves the spectrum to disk in the data/sdss_spectra directory.
    If the spectrum has already been downloaded, it is not re-downloaded.
    """
    plate = sdss_table_row["Plate"]
    mjd = sdss_table_row["MJD"]
    fiber = sdss_table_row["Fiber"]
    # Check if the spectrum has already been downloaded
    filename = f"../data/sdss_spectra/{sdss_table_row['WD']}.fits"
    if os.path.exists(filename):
        print(f"{sdss_table_row['WD']} already downloaded.")
        return
    print("Trying DR18...")
    url = f"https://sas.sdss.org/sas/dr18/spectro/sdss/redux/v5_13_2/spectra/lite/{plate}/spec-{plate}-{mjd}-{fiber:04d}.fits"
    try:
        with fits.open(url) as hdul:
            hdul.writeto(filename)
        print("Success!")
        return
    except HTTPError:
        print("Failed. Trying DR17...")
    url = f"https://dr17.sdss.org/sas/dr17/sdss/spectro/redux/26/spectra/{plate}/spec-{plate}-{mjd}-{fiber:04d}.fits"
    try:
        with fits.open(url) as hdul:
            hdul.writeto(filename)
        print("Success!")
    except HTTPError:
        print("DR17 failed too :/")


if __name__ == "__main__":
    random_sdss_table = get_random_spectra_data()

    for j, (i, row) in enumerate(random_sdss_table.iterrows()):
        print(f"Downloading spectrum {j + 1} of {len(random_sdss_table)}...")
        download_sdss_spectrum(row)
