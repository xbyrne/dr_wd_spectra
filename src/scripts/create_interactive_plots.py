"""
create_interactive_plot.py
Creates an interactive plot where you can mouseover the points in the
tSNE embedding to see which spectra are projected where.
"""

import os
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from bokeh.plotting import figure, output_file
from bokeh.models import ColumnDataSource

import preprocessing as pp
from create_fig2_embedding import MARKER_DF

# ----------------------------------
# Loading data
print("Loading data...")

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
wavelengths = fl["wavelengths"]
fluxes = fl["fluxes"]
ivars = fl["ivars"]
classifications = fl["classifications"]

fl = np.load("../data/embedding_full.npz", allow_pickle=True)
names = fl["names"]
embedding = fl["embedding"]

fl = np.load("../data/embedding_DB.npz", allow_pickle=True)
embedding_DB = fl["embedding"]
fl = np.load("../data/embedding_CV.npz", allow_pickle=True)
embedding_CV = fl["embedding"]


gf19 = pd.read_csv("../data/gf19.csv")

# ----------------------------------
# Creating the spectra for the hover tooltip


def create_spectra_tooltips():
    for name, spectrum, ivar in tqdm(
        zip(names, fluxes, ivars), desc="Creating spectra...", total=len(names)
    ):
        flx = pp.meanstd(
            pp.interp_if_snr_low(wavelengths, spectrum, ivar, snr_threshold=0.2)
        )
        fg, ax = plt.subplots(figsize=(10, 3))
        ax.plot(wavelengths, flx, c="k", lw=0.7)

        ax.set_xlim(3600, 6900)
        ax.set_yticks([])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)

        fg.savefig(f"../interactive_plots/spectra/{name}.png", dpi=100)
        plt.close(fg)


# ----------------------------------
# Creating the interactive plot


def create_bokeh_df(emb):
    # Create a DataFrame for the bokeh plot
    df = pd.DataFrame(emb, columns=["x", "y"])
    df["name"] = names

    df["classification"] = classifications
    short_classes = ["WM" if cl == "WD+MS" else cl[:2] for cl in classifications]
    class_references = [cl[:2] for cl in short_classes]

    df["colour"] = [MARKER_DF.loc[cl]["c"] for cl in class_references]
    df["colour"] = df["colour"].replace("k", "#000000").replace("grey", "#808080")
    df["marker"] = [MARKER_DF.loc[cl]["marker"] for cl in class_references]

    df["Teff"] = gf19["TeffH"].apply(lambda x: f"{x:.3g}")

    return df


def create_interactive_plot(embedding, output_filename):
    # Tooltip for when you hover over a point
    tooltip = """
    <div>
    @name &nbsp; @classification; T=@Teff
    </div>
    <img src="@img_link"></img>
    """

    p = figure(
        width=1000,
        height=1000,
        min_border=150,
        tools="pan, wheel_zoom, box_zoom, reset, hover, save",
        tooltips=tooltip,
    )

    bokeh_df = create_bokeh_df(embedding)

    for marker, marker_name, marker_size, mlw in zip(
        ["o", "*", "x", "+", "."],
        ["circle", "star", "x", "cross", "dot"],
        [7, 8, 9, 8, 16],  # Sizes
        [1, 1, 2, 2, 0],  # Marker line widths
    ):
        marker_df = bokeh_df[bokeh_df["marker"] == marker]
        p.scatter(
            "x",
            "y",
            size=marker_size,
            source=ColumnDataSource(marker_df),
            color="colour",
            marker=marker_name,
            line_width=mlw,
        )

        # Output to a file
        output_file(output_filename)


if __name__ == "__main__":
    # Create the mini spectra tooltips, if they don't exist
    if not os.path.exists("../interactive_plots/spectra/"):
        os.makedirs("../interactive_plots/spectra")
        create_spectra_tooltips()  # ~5min

    create_interactive_plot(embedding, "../interactive_plots/embedding.html")
    create_interactive_plot(embedding_DB, "../interactive_plots/embedding_He.html")
    create_interactive_plot(embedding_CV, "../interactive_plots/embedding_CV.html")
