#!/bin/bash

# --------------------------------------------------
# Prepare the exposure data from Zenodo

## Download the exposures into the data folder
echo "Downloading exposures from Zenodo..."
wget -O ../data/Exposures.tar.gz https://zenodo.org/records/11548859/files/Exposures.tar.gz?download=1

## Untar the exposures
echo "Unpacking exposures..."
tar -xzf ../data/Exposures.tar.gz -C ../data/

# --------------------------------------------------
# Prepare Manser+24's labelled catalogue

## Download from Zenodo
echo "Downloading Manser+24's labelled DESI EDR WD catalogue..."
wget -O ../data/manser_24_wd_catalogue.zip https://zenodo.org/records/10620344/files/DESI_EDR_WD_catalogue_online_data.zip?download=1

## Unzip
echo "Unpacking Manser+24's catalogue..."
unzip -qo ../data/manser_24_wd_catalogue.zip -d ../data/

# --------------------------------------------------
# Cleaning up
echo "Cleaning up..."

## Remove the tarballs
echo "Removing tarballs..."
rm ../data/Exposures.tar.gz
rm ../data/manser_24_wd_catalogue.zip

## Removing extraneous files
echo "Removing extraneous files..."
rm -rf ../data/__MACOSX
rm -rf ../data/DESI_EDR_WD_catalogue_online_data/!(THE_CATALOGUE)