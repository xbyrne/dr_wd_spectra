"""
join_desiedr_gf19.py
====================
Obtains a subset of the WD candidate catalogue from Gentile Fusillo+19,
containing only the sources that are in the DESI EDR WD catalogue.
"""

import numpy as np
from pyvo import registry

fl = np.load("../data/coadded_spectra.npz", allow_pickle=True)
names = fl["names"]

GF19_CATALOGUE = "J/MNRAS/482/4570"
GF19_IVO_ID = f"ivo://CDS.Vizier/{GF19_CATALOGUE}"

vo_resource = registry.search(ivoid=GF19_IVO_ID)[0]
tap_service = vo_resource.get_service("tap")

TARGET_LIST_STRING = ", ".join([f"'WD{name}'" for name in names])
query = f"""
SELECT *
FROM "{GF19_CATALOGUE}/gaia2wd"
WHERE WD IN ({TARGET_LIST_STRING})
"""

print("Querying...")
tap_records = tap_service.search(query)  # ~1m30s
desiedr_gf19 = tap_records.to_table().to_pandas()

print("Processing...")
desiedr_gf19.set_index("WD", inplace=True)  # Setting index
desiedr_gf19 = desiedr_gf19.loc[[f"WD{nm}" for nm in names]]  # Reordering

print("Saving...")
desiedr_gf19.to_csv("../data/gf19.csv", index=True, header=True)
