# dr_wd_spectra
Using dimensionality reduction to get a quick overview of a spectroscopic dataset


## Downloading data

The exposures of WDs targeted in the DESI EDR are available in a .tar.gz file hosted on Zenodo.
These data are publicly available at https://data.desi.lbl.gov/public/, but it's difficult to query particular objects without downloading the whole EDR.
The exposures for the 3673 WDs targeted by the DESI EDR with usable spectroscopy (median S/R > 0.5 in all three arms) were selected by Christopher J. Manser (see Manser+24), and it is these objects whose exposures are first downloaded.

To download them, `cd` into `src/scripts` and run `bash download_desi_data.sh`, which downloads `Exposures.tar.gz` from Zenodo (https://zenodo.org/records/11548859) and untars them.
`Exposures.tar.gz` is about 8GB in size and takes a few minutes to download.
The untarring takes rather longer, and the resulting src/data/Exposures folder is about 20GB.

To get visual spectral classifications of the WDs in the DESI EDR, we use the catalogue of Manser+24.
This is also downloaded from Zenodo (https://zenodo.org/records/10620344).
This Zenodo record contains lots of extraneous files, e.g. scripts used to make plots in Manser+24; these are removed.


## References
Manser+24:
https://ui.adsabs.harvard.edu/abs/2024arXiv240218641M/abstract