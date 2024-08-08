"""
create_fig2_embedding.py
Creates Figure 2 in the paper, which shows the t-SNE embedding of the spectra.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MARKER_DF = pd.DataFrame(  # Define the markers and colours for each class
    columns=["class", "c", "marker"],
    data=[
        # WDs
        ["DA", "#ff0000", "o"],
        ["DB", "#0000ff", "o"],
        ["DC", "#1ecc19", "o"],
        ["DO", "#8E369A", "o"],
        ["DQ", "#0e8674", "o"],
        ["DZ", "#de589f", "o"],
        ["DH", "grey", "o"],
        ["WD", "grey", "o"],
        # Others
        ["WM", "#ffaf00", "*"],  # WD+MS
        ["CV", "#ffaf00", "x"],
        ["sd", "k", "+"],  # Subdwarfs
        ["ST", "k", "*"],  # MS stars
        ["EX", "k", "x"],  # Extragalactic (prob QSO)
        ["UN", "k", "."],  # Unclassified
    ],
)
MARKER_DF.set_index("class", inplace=True)


def create_legend_handles():
    """
    Creates a legend for plots of dimensionality-reduced spectra
    """

    def header_handle(label):
        """Blank handle to make a subheading for the legend"""
        return plt.Line2D(
            [0], [0], marker="o", color="w", markerfacecolor="w", label=label
        )

    def class_handle(label, colour, **kwargs):
        """Handle for a class in the legend"""
        return plt.Line2D(
            [0],
            [0],
            label=label,
            markerfacecolor=colour,
            markeredgecolor=colour,
            lw=0,
            **kwargs
        )

    handles = []
    # WDs
    handles.append(header_handle("WDs"))
    for cl_code in ["DA", "DB", "DC", "DZ", "DQ", "DO"]:
        handles.append(
            class_handle(
                cl_code,
                MARKER_DF.loc[cl_code, "c"],
                marker=MARKER_DF.loc[cl_code, "marker"],
                markersize=10,
            )
        )
    # Others
    handles.append(header_handle("Other"))
    for cl_code in ["WM", "CV", "sd", "ST", "EX", "UN"]:
        handles.append(
            class_handle(
                cl_code,
                MARKER_DF.loc[cl_code, "c"],
                marker=MARKER_DF.loc[cl_code, "marker"],
                markersize=9,
            )
        )
    return handles


if __name__ == "__main__":

    fl = np.load("../data/embedding.npz", allow_pickle=True)
    names = fl["names"]
    embedding = fl["embedding"]

    fg, axs = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"wspace": 0.0})

    # Agnostic plot
    ax = axs[0]
    ax.scatter(embedding[:, 0], embedding[:, 1], c="k", s=10)

    # Annotated plot
    fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
    names = fl["names"]
    classes = fl["classifications"]

    # Colouring by primary classification
    class_code = np.array([cl[:2] if cl != "WD+MS" else "WM" for cl in classes])
    # eg. DA, ..., DZ, CV, WD+MS -> WM, WD, sd, EX, ST, UN

    ax = axs[1]
    for cl in np.unique(class_code):
        mask = class_code == cl
        marker = MARKER_DF.loc[cl]
        ax.scatter(
            embedding[mask, 0],
            embedding[mask, 1],
            s=15,
            c=marker["c"],
            marker=marker["marker"],
        )

    leg = ax.legend(
        handles=create_legend_handles(), bbox_to_anchor=(1.02, 1), fontsize=16
    )
    for i in [0, 7]:
        leg.get_texts()[i].set_weight("bold")  # Bold the headers
        leg.get_texts()[i].set_position((-37, 0))  # Move the headers to the left

    # Aesthetic
    for ax in axs:
        ax.set_xlabel("t-SNE 1", fontsize=20)
        ax.set_xticks([])
        ax.set_yticks([])

    axs[0].set_ylabel("t-SNE 2", fontsize=20)

    fg.tight_layout()
    fg.savefig("../tex/figures/fig2_embedding.pdf", dpi=300)
