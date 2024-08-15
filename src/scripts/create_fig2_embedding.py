"""
create_fig2_embedding.py
Creates Figure 2 in the paper, which shows the t-SNE embedding of the spectra.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

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
            [0],
            [0],
            marker="o",
            color="w",
            alpha=0.0,
            markerfacecolor="w",
            label=label,
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
            **kwargs,
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
    handles = handles[:4] + [header_handle("")] + handles[4:]  # Add a blank line
    # Others
    handles.append(header_handle("Other"))
    for cl_code in ["WM", "CV", "sd", "ST", "EX", "UN"]:
        handles.append(
            class_handle(
                {
                    "WM": "WD+MS",
                    "CV": "CV",
                    "sd": "sdX",
                    "ST": "STAR",
                    "EX": "EXGAL",
                    "UN": "UNCLASS",
                }[cl_code],
                MARKER_DF.loc[cl_code, "c"],
                marker=MARKER_DF.loc[cl_code, "marker"],
                markersize=12,
                markeredgewidth=2,
            )
        )
    handles = handles[:12] + [header_handle("")] + handles[12:]  # Add a blank line
    return handles


if __name__ == "__main__":

    fl = np.load("../data/embedding_full.npz", allow_pickle=True)
    names = fl["names"]
    embedding = fl["embedding"]

    # -------------------
    # Agnostic plot
    fg, ax = plt.subplots(1, 1, figsize=(7, 7))
    ax.scatter(embedding[:, 0], embedding[:, 1], c="k", s=8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("t-SNE 1", fontsize=20)
    ax.set_ylabel("t-SNE 2", fontsize=20)

    ax.annotate(
        "(a)",
        xy=(0.02, 0.94),
        xycoords="axes fraction",
        fontsize=20,
    )

    fg.tight_layout()
    fg.savefig("../tex/figures/fig2a_embedding.pdf", dpi=300)

    # -------------------
    # Labelled plot

    fg, axs = plt.subplots(
        2,
        2,
        figsize=(12, 7),
        gridspec_kw={"wspace": 0.0, "hspace": 0.0, "height_ratios": [1, 0.05]},
    )

    ax = axs[0, 0]

    fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
    names = fl["names"]
    classes = fl["classifications"]
    # Colouring by primary classification
    class_code = np.array([cl[:2] if cl != "WD+MS" else "WM" for cl in classes])
    # eg. DA, ..., DZ, CV, WD+MS -> WM, WD, sd, EX, ST, UN

    for cl in np.unique(class_code):
        mask = class_code == cl
        marker = MARKER_DF.loc[cl]
        if cl[0] == "D":
            s = 15
        else:
            s = 20
        ax.scatter(
            embedding[mask, 0],
            embedding[mask, 1],
            s=s,
            c=marker["c"],
            marker=marker["marker"],
        )

    leg = ax.legend(
        handles=create_legend_handles(),
        bbox_to_anchor=(1.0, 0.0),
        fontsize=17,
        ncol=4,
        columnspacing=-0.5,
        frameon=False,
    )
    for i in [0, 8]:
        leg.get_texts()[i].set_weight("bold")  # Bold the headers
        leg.get_texts()[i].set_position((-17, 0))  # Move the headers to the left
    # for t in leg.get_texts():
    #     t.set_position((-15, 0))
    # for t in leg.get_texts()[4:]:
    #     t.set_position((-40, 0))
    for h in leg.legend_handles:
        h.set_data(
            [x + 20 for x in h.get_data()[0]],  # Move the markers to the left
            h.get_data()[1],
        )

    ax.annotate(
        "(b)",
        xy=(0.02, 0.94),
        xycoords="axes fraction",
        fontsize=20,
    )

    # -------------------
    # Temperature coding
    ax = axs[0, 1]

    gf19 = pd.read_csv("../data/gf19.csv", index_col=0)

    teff_cmp = LinearSegmentedColormap.from_list(
        "temp", ["black", "red", "orange", "yellow", "yellow", "white"]
    )
    sc = ax.scatter(
        embedding[:, 0],
        embedding[:, 1],
        s=8,
        c=np.log10(gf19["TeffH"]),
        cmap=teff_cmp,
    )

    ax.annotate("(c)", xy=(0.02, 0.94), xycoords="axes fraction", fontsize=20)

    cbar = fg.colorbar(sc, cax=axs[1, 1], orientation="horizontal")
    cbar.set_label(r"$T_\text{eff}\; [10^3\,\text{K}]$", fontsize=20)
    T_ticks = np.array(
        [
            4000,
            6000,
            8000,
            10000,
            20000,
            40000,
            60000,
            80000,
        ]
    )
    cbar.set_ticks(np.log10(T_ticks))
    cbar.set_ticklabels([f"${int(T/1e3)}$" for T in T_ticks], fontsize=16)

    # -------------------
    # Aesthetic
    for ax in axs[0, :]:
        # ax.set_xlabel("t-SNE 1", fontsize=20)
        ax.set_xticks([])
        ax.set_yticks([])

    axs[1, 0].axis("off")

    # -------------------
    # Saving

    fg.tight_layout()
    fg.savefig("../tex/figures/fig2b_embedding.pdf", dpi=300, bbox_inches="tight")
