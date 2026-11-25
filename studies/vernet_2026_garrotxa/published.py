"""Values transcribed from Vernet et al. (2026) and its appendix, and the choices made in
the conversion, as named constants. Nothing is calculated here. The comment above each
block gives its source, and README.md gives the reasons for the choices.

    Vernet, E., Calvo-Rathert, M., Beamud, E., Bógalo, M.-F., Carrancho, Á., Planagumà, L.,
    & Martí, J. (2026). Laschamp and Greenland-Norwegian Sea excursions recorded in NE Iberia
    lava flows: Late Quaternary geomagnetic data from La Garrotxa Volcanic Field. Geologica
    Acta, 24.15, 1-18, I-VII. https://doi.org/10.1344/GeologicaActa2026.24.15
"""

from collections import OrderedDict

import pandas as pd

PAPER_DOI = "10.1344/GeologicaActa2026.24.15"
DATA_DOI = "10.5281/zenodo.20326424"

# ------------------------------------------------------------------ text of the paper
# "Sites GTX01 to GTX10 were treated thermally (TH) or by Alternating Fields (AF) at the
# University of Burgos (UBU, Spain), while in sites OL01 to OL04 a TH demagnetization was
# performed at the CCiTUB-Geo3BCN Laboratory of Paleomagnetism." The names are the MagIC
# vocabulary items; Geo3BCN is the former ICTJA, whose laboratory is shared with the
# Universitat de Barcelona (CCiTUB).
LAB_BURGOS = "Paleomagnetic and Rock Magnetic Laboratory (Universidad de Burgos, Spain)"
LAB_BARCELONA = "Laboratory of Paleomagnetism (CSIC-ICTJA and Universitat de Barcelona, Spain)"
LABORATORIES = f"{LAB_BURGOS}:{LAB_BARCELONA}"
# Shown with the contribution in MagIC.
CONTRIBUTION_DESCRIPTION = (
    "Converted from the laboratory files archived by the authors (https://doi.org/10.5281/zenodo.20326424) "
    "and from the paper and its appendix. Sources, choices and checks are documented at "
    "<permalink>.")
LOCATION = "La Garrotxa Volcanic Field"
# Abstract: "Late Pleistocene basaltic lava flows (~134-16 ka)"
GEOLOGIC_CLASSES, GEOLOGIC_TYPES, LITHOLOGIES = "Extrusive:Igneous", "Lava Flow", "Basalt"
# Sampling section: drilled cores "oriented using magnetic compass and sun compass when possible"
# (GTX01 to GTX07, GTX09; OL01 to OL04 "drilled and collected similarly"); GTX08 and GTX10 "oriented
# blocks ... oriented in situ before their extraction using a magnetic compass and applying a local
# declination correction of 2°"; GTX11 "only unoriented hand-blocks".
ORIENTATION_CORES = "FS-FD:SO-MAG:SO-SUN"
ORIENTATION_BLOCKS = "FS-H:SO-MAG"
BLOCK_SITES = ("GTX08", "GTX10")
UNORIENTED_SITES = ("GTX11",)
# Paleomagnetic directions section: OL01 to OL04 were demagnetized thermally. Their .rs3 files mark
# the steps with ID M and no unit (README.md, "Files").
OL_STEP_TYPE = "T"

# ------------------------------------------------------------------ Table 1
# site, locality name, age (ka BP), ± as printed, dating method, latitude, longitude (degrees)
# Dating: "40Ar/39Ar (1)" = Martí et al. (2025); "TH in Pl (2)" = thermoluminescence in
# plagioclase, Guerin et al. (1985). The table does not say what the ± is.
TABLE1 = pd.DataFrame([
    ("GTX03", "Triai", 15.86, 4.21, "Ar", 42.1661838, 2.4997058),
    ("OL03", "Pomareda en el Croscat", 15.86, 4.21, "Ar", 42.1582200, 2.5302390),
    ("OL04", "Pomareda s.s. (spater)", 15.86, 4.21, "Ar", 42.1584870, 2.5304360),
    ("GTX08", "Volcanic cone paleolake", 17.35, 4.17, "Ar", 42.1597402, 2.4668109),
    ("GTX09", "Fonts de Sant Roc", 17.35, 4.17, "Ar", 42.1735223, 2.4742503),
    ("OL01", "Puig Jordà", 17.35, 4.17, "Ar", 42.1736530, 2.4656450),
    ("GTX02", "La Moixina", 26.76, 5.82, "Ar", 42.1671597, 2.4857701),
    ("GTX05", "Sant Feliu (Traiter)", 46.3, 4.0, "TL", 42.0771804, 2.5096877),
    ("GTX01", "Montolivet (Pla de Dalt)", 61.80, 6.34, "Ar", 42.1893203, 2.4687525),
    ("GTX04", "Santa Pau (Sant Marc volcano)", 69.63, 12.73, "Ar", 42.0728693, 2.5164106),
    ("OL02", "Roca Negra (Sta. Pau)", 69.63, 12.73, "Ar", 42.1444470, 2.5682010),
    ("GTX06", "Sant Iscle (Fontpobra Collfort)", 73.5, 4.6, "TL", 42.1145247, 2.5198911),
    ("GTX07", "Pla de les Tries", 110, 10, "TL", 42.1574034, 2.5661000),
    ("GTX11", "Batet de la Serra", 129.20, 4.38, "Ar", 42.1706500, 2.5001159),
    ("GTX10", "Can Pixola", 133, 12, "TL", 42.1955990, 2.5024540),
], columns=["site", "locality", "age", "age_pm", "dating", "lat", "lon"])
DATING = {
    "Ar": ("GM-ARAR", "Martí et al. (2025), 40Ar/39Ar"),
    "TL": ("GM-LUM-TH", "Guerin et al. (1985), thermoluminescence in plagioclase"),
}

# ------------------------------------------------------------------ Table 2: site directions
# site, Dec, ΔD, Inc, ΔI (degrees; ΔD and ΔI "at 97.5% (Demarest, 1983)"), α95, n/N ("number of
# accepted specimens vs. number of studied specimens"). No direction for GTX06 (text: "no mean
# direction was calculated") or GTX11 (unoriented). The text: "mean directions per lava flow were
# calculated hierarchically at sample level (Table 2) using PMagTools".
TABLE2_DIRECTIONS = pd.DataFrame([
    ("GTX03", 10.8, 3.1, 42.8, 2.3, 2.9, 9, 9),
    ("OL03", 356.8, 9.8, 55.7, 5.5, 7.1, 6, 8),
    ("OL04", 2.8, 5.9, 53.8, 3.5, 4.4, 9, 10),
    ("GTX08", 19.2, 8.5, 18.3, 8.1, 10.8, 3, 3),
    ("GTX09", 36.0, 21.2, 46.2, 14.7, 18.8, 6, 7),
    ("OL01", 18.9, 17.9, 53.4, 13.7, 13.7, 7, 7),
    ("GTX02", 7.4, 5.2, 51.2, 3.3, 4.2, 6, 8),
    ("GTX05", 9.5, 6.6, 65.8, 2.7, 3.4, 9, 9),
    ("GTX01", 155.7, 21.2, 78.2, 4.3, 5.5, 10, 10),
    ("GTX04", 31.0, 8.6, 57.7, 4.6, 5.9, 7, 8),
    ("OL02", 1.8, 4.0, 65.6, 1.7, 2.1, 10, 10),
    ("GTX07", 1.8, 6.8, 52.0, 4.2, 5.3, 9, 9),
    ("GTX10", 29.1, 12.4, 58.6, 6.5, 8.6, 3, 3),
], columns=["site", "dec", "dD", "inc", "dI", "a95", "n", "N"])
# Table 2, GTX06: "0/9"
GTX06_N = 9

# ------------------------------------------------------------------ Table 2: site paleointensities
# site, B, ΔB (microtesla), n/N; "-" (no result) is left out
TABLE2_INTENSITIES = pd.DataFrame([
    ("GTX03", 37.9, 4.7, 4, 10),
    ("OL04", 39.7, 5.4, 6, 8),
    ("GTX08", 32.0, 3.2, 4, 8),
    ("GTX02", 27.6, 4.5, 6, 10),
    ("GTX05", 10.8, 2.6, 8, 9),
    ("OL02", 16.1, 4.7, 8, 9),
    ("GTX06", 3.5, 0.9, 3, 10),
    ("GTX07", 9.4, 2.4, 2, 8),
    ("GTX11", 28.7, 3.2, 7, 8),
    ("GTX10", 30.8, 1.3, 3, 10),
], columns=["site", "B", "dB", "n", "N"])

# ------------------------------------------------------------------ Table 3: VGPs and VADMs
# site, VGP lat, lon (degrees), dp, dm, VADM, ΔVADM (10^22 Am2). The header prints the error
# columns as "Dm dp", but the first of the two is dp (the smaller; README.md, "Directions").
TABLE3 = pd.DataFrame([
    ("GTX03", 70.5, 151.8, 2.22, 3.59, 6.39, 0.79),
    ("OL03", 83.6, 206.3, 7.27, 10.16, None, None),
    ("OL04", 81.9, 165.9, 4.30, 6.15, 6.69, 0.91),
    ("GTX08", 53.1, 149.7, 5.83, 11.22, 5.40, 0.54),
    ("GTX09", 57.4, 107.4, 15.43, 24.08, None, None),
    ("OL01", 73.1, 115.3, 13.25, 19.06, None, None),
    ("GTX02", 78.1, 150.3, 3.86, 5.69, 4.65, 0.76),
    ("GTX05", 81.0, 47.5, 4.52, 5.54, 1.82, 0.44),
    ("GTX01", 21.1, 12.3, 9.77, 10.36, None, None),
    ("GTX04", 66.2, 91.1, 6.36, 8.66, None, None),
    ("OL02", 84.2, 14.7, 2.78, 3.42, 2.72, 0.79),
    ("GTX06", None, None, None, None, 0.59, 0.15),
    ("GTX07", 80.4, 173.5, 4.96, 7.25, 1.59, 0.40),
    ("GTX11", None, None, None, None, 4.84, 0.54),
    ("GTX10", 67.9, 90.2, 9.48, 12.77, 5.19, 0.22),
], columns=["site", "vgp_lat", "vgp_lon", "dp", "dm", "vadm", "vadm_sigma"])
# Table 3, "Mean poles" of sites with the same isotopic age (text: P1, P2, P3), and the mean VADMs
# of P1 (6.54 ± 0.21) and P2 printed in the same rows. The text: "only VGPs calculated per lava flow
# were considered for the discussion."
MEAN_POLES = pd.DataFrame([
    ("P1", "GTX03:OL03:OL04", 79.4, 165.0, 13.1),
    ("P2", "GTX08:GTX09:OL01", 62.6, 126.7, 24.0),
    ("P3", "GTX04:OL02", 77.1, 78.2, 52.6),
], columns=["group", "sites", "pole_lat", "pole_lon", "A95"])

# ------------------------------------------------------------------ Table I (appendix)
# specimen, discarded ("*"), treatment, Min., Max. (°C or mT), line ("OA": "anchored to the origin";
# "O": "including the origin"; blank: free), N, Dec, Inc, MAD (degrees). Directions are geographic.
TABLE_I = pd.DataFrame([
    ('GTX0101B', False, 'TH', '360', '580', 'OA', 10, 141.6, 76.8, 17.6),
    ('GTX0102A', False, 'TH', '420', '560', 'OA', 7, 118.6, 77.6, 15.0),
    ('GTX0103A', False, 'AF', '35', '100', 'OA', 9, 91.1, 81.3, 9.8),
    ('GTX0104A', False, 'TH', '420', '580', 'OA', 8, 139.8, 75.6, 7.1),
    ('GTX0105A', False, 'TH', '390', '560', 'O', 8, 181.5, 79.1, 9.2),
    ('GTX0106A', False, 'AF', '20', '100', 'O', 12, 159.8, 74.6, 1.0),
    ('GTX0107B', False, 'TH', '330', '560', 'OA', 10, 171.0, 69.1, 14.6),
    ('GTX0108A', False, 'TH', '330', '540', 'OA', 9, 339.5, 83.9, 14.7),
    ('GTX0109A', False, 'TH', '420', '580', 'OA', 8, 169.6, 72.9, 19.8),
    ('GTX0110A', False, 'TH', '420', '560', 'OA', 7, 165.4, 69.3, 15.7),
    ('GTX0201A', False, 'TH', '420', '560', 'OA', 7, 18.9, 51.8, 4.6),
    ('GTX0202A', False, 'AF', '25', '100', 'OA', 11, 7.4, 50.1, 2.1),
    ('GTX0202B', False, 'TH', '330', '560', 'OA', 10, 3.7, 57.2, 5.7),
    ('GTX0203B', False, 'TH', '360', '560', 'OA', 9, 6.2, 53.3, 3.7),
    ('GTX0204B', True, 'TH', '150', '540', 'OA', 13, 30.9, 68.4, 7.6),
    ('GTX0205A', True, 'TH', '330', '540', 'OA', 9, 104.3, 71.1, 2.9),
    ('GTX0206A', False, 'TH', '420', '540', 'OA', 6, 7.3, 54.1, 0.9),
    ('GTX0207A', False, 'AF', '5', '100', 'OA', 15, 2.8, 46.4, 0.4),
    ('GTX0207B', False, 'TH', '360', '580', 'OA', 10, 1.8, 44.1, 0.7),
    ('GTX0208A', False, 'TH', '390', '580', 'OA', 9, 4.8, 48.4, 1.4),
    ('GTX0301A', False, 'TH', '360', '580', 'OA', 10, 5.1, 37.8, 3.6),
    ('GTX0302A', False, 'TH', '300', '450', 'OA', 6, 17.7, 45.7, 7.6),
    ('GTX0302B', False, 'AF', '35', '100', 'OA', 9, 356.6, 49.7, 1.0),
    ('GTX0303A', False, 'TH', '300', '540', 'OA', 10, 12.4, 38.9, 5.0),
    ('GTX0304A', False, 'TH', '300', '560', 'OA', 11, 9.1, 41.3, 3.3),
    ('GTX0305A', False, 'TH', '330', '580', 'OA', 11, 12.8, 39.9, 2.7),
    ('GTX0306A', False, 'TH', '330', '580', 'OA', 11, 12.2, 41.5, 2.3),
    ('GTX0307A', False, 'TH', '360', '580', 'OA', 10, 9.3, 42.8, 2.7),
    ('GTX0308A', False, 'TH', '500', '580', 'OA', 5, 14.9, 45.5, 2.2),
    ('GTX0309A', False, 'AF', '20', '100', 'OA', 12, 14.6, 48.5, 1.0),
    ('GTX0401A', True, 'TH', '100', '480', 'OA', 11, 83.7, -56.8, 4.4),
    ('GTX0401B', True, 'AF', '10', '90', 'OA', 16, 42.8, 26.4, 9.7),
    ('GTX0402A', False, 'TH', '300', '560', 'OA', 11, 46.0, 47.1, 10.3),
    ('GTX0403A', False, 'TH', '250', '520', 'OA', 10, 22.5, 54.6, 10.3),
    ('GTX0404A', True, 'AF', '10', '75', 'OA', 12, 332.4, 81.6, 1.8),
    ('GTX0404B', False, 'TH', '100', '420', 'OA', 9, 32.4, 53.7, 6.7),
    ('GTX0405A', False, 'TH', '360', '520', 'OA', 7, 20.9, 63.0, 4.0),
    ('GTX0406A', False, 'TH', '330', '540', 'OA', 8, 25.1, 58.8, 8.6),
    ('GTX0407A', False, 'TH', '330', '540', 'OA', 8, 25.8, 62.6, 6.9),
    ('GTX0408A', False, 'TH', '200', '540', 'OA', 11, 39.9, 62.0, 8.0),
    ('GTX0501A', False, 'TH', '200', '580', 'OA', 13, 12.6, 61.7, 0.8),
    ('GTX0502A', False, 'AF', '6', '100', 'OA', 14, 10.1, 72.4, 0.6),
    ('GTX0502B', False, 'TH', '330', '580', 'OA', 10, 10.5, 67.2, 1.3),
    ('GTX0503A', False, 'TH', '330', '580', 'OA', 10, 358.2, 65.5, 2.1),
    ('GTX0504A', False, 'TH', '420', '560', 'OA', 7, 1.2, 65.2, 4.4),
    ('GTX0505A', False, 'TH', '250', '580', 'OA', 12, 3.2, 62.6, 2.3),
    ('GTX0506A', False, 'AF', '15', '100', 'OA', 12, 8.3, 66.0, 0.6),
    ('GTX0507A', False, 'TH', '420', '540', 'OA', 6, 37.0, 71.3, 3.8),
    ('GTX0508A', False, 'TH', '200', '450', 'OA', 8, 10.8, 63.1, 2.2),
    ('GTX0509B', False, 'TH', '250', '480', 'OA', 8, 10.8, 64.0, 2.0),
    ('GTX0601B', True, 'TH', '360', '540', 'O', 8, 273.7, -50.7, 1.1),
    ('GTX0602B', True, 'TH', '360', '500', 'O', 6, 231.9, 20.0, 9.8),
    ('GTX0603A', True, 'AF', '40', '100', 'O', 12, 134.9, 74.6, 3.3),
    ('GTX0604A', True, 'TH', '360', '560', 'O', 9, 142.7, 76.7, 7.9),
    ('GTX0605B', True, 'TH', '390', '560', 'O', 8, 127.0, 64.8, 4.3),
    ('GTX0606A', True, 'TH', '200', '420', 'O', 7, 192.6, -19.8, 5.9),
    ('GTX0607A', True, 'AF', '15', '90', 'O', 12, 199.5, -15.3, 0.5),
    ('GTX0607B', True, 'TH', '200', '420', 'O', 7, 191.4, -14.5, 8.0),
    ('GTX0608A', True, 'TH', '100', '420', 'O', 9, 131.0, 4.7, 5.8),
    ('GTX0609A', True, 'TH', '150', '520', 'O', 12, 132.3, 18.1, 3.6),
    ('GTX0701B', False, 'TH', '300', '540', 'OA', 10, 4.4, 49.8, 10.7),
    ('GTX0702A', False, 'TH', '100', '390', 'OA', 8, 347.5, 33.7, 17.0),
    ('GTX0702B', False, 'AF', 'NRM', '100', 'OA', 15, 343.6, 53.1, 1.5),
    ('GTX0703A', False, 'TH', '100', '390', 'OA', 8, 1.3, 43.9, 15.7),
    ('GTX0704A', False, 'TH', '330', '390', 'OA', 3, 11.5, 54.1, 2.3),
    ('GTX0705A', False, 'TH', '200', '390', 'OA', 6, 6.6, 62.1, 4.9),
    ('GTX0706A', False, 'TH', '200', '390', 'OA', 6, 2.3, 61.3, 1.4),
    ('GTX0707A', False, 'TH', '250', '420', 'OA', 6, 4.3, 48.3, 4.2),
    ('GTX0708A', False, 'TH', '330', '520', 'OA', 8, 8.1, 49.6, 9.2),
    ('GTX0710A', False, 'AF', '10', '90', 'OA', 13, 355.7, 53.2, 0.4),
    ('GTX080101A', False, 'TH', '360', '540', 'OA', 8, 3.4, 8.4, 10.4),
    ('GTX080102A', False, 'TH', '390', '540', 'OA', 7, 38.2, 25.1, 1.1),
    ('GTX080102B', False, 'AF', '35', '100', 'O', 9, 37.1, 18.4, 0.8),
    ('GTX080103A', False, 'TH', '330', '420', 'OA', 4, 1.5, 8.4, 4.0),
    ('GTX080201A', False, 'TH', '100', '360', 'O', 7, 28.4, 17.6, 2.8),
    ('GTX080202A', False, 'TH', '150', '360', 'O', 6, 26.5, 19.1, 2.2),
    ('GTX080203A', False, 'TH', '150', '420', 'O', 8, 23.1, 19.0, 3.4),
    ('GTX080301A', False, 'TH', '300', '540', 'O', 10, 11.6, 20.5, 1.7),
    ('GTX080301B', False, 'AF', '15', '90', 'O', 12, 16.1, 21.4, 1.5),
    ('GTX080303A', False, 'TH', '330', '520', 'OA', 8, 8.1, 18.9, 4.0),
    ('GTX0901A', False, 'TH', '300', '520', 'O', 9, 58.3, 35.2, 1.7),
    ('GTX0901B', False, 'AF', '20', '100', 'O', 11, 57.2, 38.7, 1.1),
    ('GTX0902A', False, 'TH', '300', '520', 'O', 9, 47.8, 34.1, 1.4),
    ('GTX0903A', False, 'TH', '250', '520', 'O', 10, 55.3, 33.0, 2.6),
    ('GTX0904A', True, 'TH', '300', '520', 'O', 9, 137.6, 38.3, 1.6),
    ('GTX0904B', True, 'TH', '330', '520', 'O', 8, 138.1, 36.9, 1.1),
    ('GTX0905A', False, 'AF', '10', '100', 'O', 17, 13.5, 59.4, 0.7),
    ('GTX0905B', False, 'TH', '360', '560', 'O', 9, 2.5, 59.9, 4.6),
    ('GTX0906B', False, 'TH', '330', '560', 'O', 10, 15.8, 54.6, 2.8),
    ('GTX0907A', False, 'TH', '150', '540', 'O', 13, 1.5, 52.1, 3.4),
    ('GTX100101A', False, 'AF', '5', '100', 'O', 18, 22.1, 53.7, 1.0),
    ('GTX100101B', False, 'TH', '200', '540', 'O', 12, 21.3, 56.2, 9.0),
    ('GTX100102A', True, 'TH', '300', '540', 'O', 10, 22.7, 17.9, 4.8),
    ('GTX100103A', True, 'TH', '250', '540', 'O', 11, 16.1, 11.3, 2.4),
    ('GTX100201A', False, 'TH', '200', '540', 'O', 12, 21.2, 61.3, 4.2),
    ('GTX100202A', False, 'TH', '330', '540', 'O', 9, 54.4, 59.6, 3.5),
    ('GTX100203A', False, 'TH', '200', '540', 'O', 12, 42.1, 57.7, 4.3),
    ('GTX100301A', False, 'TH', '360', '560', 'O', 11, 27.2, 59.9, 4.5),
    ('GTX100302A', True, 'TH', '360', '560', 'O', 11, 78.6, 12.4, 4.9),
    ('OL0110B', False, 'TH', '250', '560', 'OA', 8, 24.8, 51.3, 4.5),
    ('OL0102B', False, 'TH', '250', '560', 'OA', 8, 47.7, 59.9, 2.8),
    ('OL0104B', False, 'TH', '400', '530', 'OA', 4, 19.7, 34.8, 5.7),
    ('OL0106A', False, 'TH', '300', '560', 'OA', 7, 328.8, 54.0, 2.6),
    ('OL0107B', False, 'TH', '200', '560', 'OA', 9, 357.6, 50.6, 1.4),
    ('OL0108B', False, 'TH', '200', '530', 'OA', 8, 33.3, 47.4, 5.3),
    ('OL0109B', False, 'TH', '350', '530', 'OA', 5, 40.6, 58.3, 8.4),
    ('OL0210A', False, 'TH', '300', '530', 'OA', 6, 359.9, 65.8, 2.0),
    ('OL0201B', False, 'TH', '300', '560', 'OA', 7, 7.6, 65.3, 1.1),
    ('OL0202A', False, 'TH', '300', '560', 'OA', 7, 350.9, 66.5, 1.2),
    ('OL0203A', False, 'TH', '400', '560', 'OA', 5, 358.2, 65.4, 1.0),
    ('OL0204A', False, 'TH', '400', '600', 'OA', 7, 357.9, 68.2, 0.8),
    ('OL0205B', False, 'TH', '400', '600', 'OA', 7, 356.4, 64.9, 1.0),
    ('OL0206A', False, 'TH', '400', '600', 'OA', 7, 6.5, 65.2, 1.3),
    ('OL0207A', False, 'TH', '400', '580', 'OA', 6, 358.1, 60.4, 1.1),
    ('OL0208A', False, 'TH', '300', '490', '', 5, 12.4, 65.4, 2.6),
    ('OL0209A', False, 'TH', '400', '530', 'OA', 4, 10.7, 67.0, 1.2),
    ('OL0310B', True, 'TH', '250', '490', 'OA', 6, 213.0, -23.5, 1.9),
    ('OL0301A', False, 'TH', '300', '530', 'OA', 6, 8.9, 45.4, 9.6),
    ('OL0302A', False, 'TH', '350', '560', 'OA', 6, 341.1, 54.6, 1.7),
    ('OL0303A', False, 'TH', '250', '530', 'OA', 7, 359.8, 56.9, 2.9),
    ('OL0304B', False, 'TH', '350', '530', 'OA', 5, 9.0, 60.3, 1.2),
    ('OL0305A', False, 'TH', '250', '450', 'OA', 5, 345.6, 54.9, 3.9),
    ('OL0306A', False, 'TH', '250', '530', 'OA', 7, 355.4, 59.0, 2.1),
    ('OL0309A', True, 'TH', '200', '560', 'OA', 9, 10.4, -13.0, 1.1),
    ('OL0410A', False, 'TH', '450', '580', 'OA', 5, 5.8, 47.9, 0.9),
    ('OL0401A', False, 'TH', '450', '580', 'OA', 5, 5.1, 61.0, 1.1),
    ('OL0402B', True, 'TH', '490', '580', 'OA', 4, 277.6, 63.8, 2.7),
    ('OL0403A', False, 'TH', '530', '580', 'OA', 3, 348.1, 64.5, 1.7),
    ('OL0404B', False, 'TH', '300', '560', 'OA', 7, 6.7, 54.5, 1.8),
    ('OL0405A', False, 'TH', '450', '580', 'OA', 5, 354.3, 55.6, 1.3),
    ('OL0406A', False, 'TH', '450', '580', 'OA', 5, 5.7, 49.0, 1.4),
    ('OL0407C', False, 'TH', '400', '580', 'OA', 6, 7.3, 53.3, 0.8),
    ('OL0408A', False, 'TH', '350', '560', 'OA', 6, 3.5, 48.5, 1.0),
    ('OL0409B', False, 'TH', '400', '580', 'OA', 6, 3.7, 48.7, 0.6),
], columns=["specimen", "discarded", "treatment", "min", "max", "line", "n", "dec", "inc", "mad"])

# ------------------------------------------------------------------ decisions (see README.md)
# Samples: the piece oriented in the field. A core (the specimen name without its final letter: GTX0202A ->
# GTX0202, OL01-2B -> OL01-2), and for GTX08 and GTX10 the hand block (GTX080102A -> GTX0801), from which cores
# were drilled in the laboratory, each with its own orientation (in the .rs3 files), entered on its specimens.
# The samples are the level at which the site means of Table 2 recalculate.
# Measurements: the 2G files for the sites measured at Burgos (GTX), the .rs3 files for the OL
# sites (no 2G files); orientations and the authors' fits from the .rs3 files.
# Table I against the files (README.md, "Directions"):
# GTX0108A: the site mean of GTX01 recalculates with the direction in the file, not with Table I.
TABLE_I_FILE_DIRECTION = {"GTX0108A": (298.7, 84.0)}
# GTX0702A: the file holds a fit over 390-520 °C; Table I and the site mean use one over 100-390 °C.
TABLE_I_REFIT = {"GTX0702A": ("100", "390")}
# GTX0103A: the 2G file and the .rs3 file list a step at 420 °C first and then one labelled NRM, before the
# alternating-field steps. The 2G file gives the time of each measurement: 420 °C on 15 Dec 2023 at 10:59,
# "NRM" at 12:25, 2 mT at 12:28. The "NRM" is therefore a second measurement after heating to 420 °C, with
# no treatment in between, and is entered as such (temperature in °C, description).
NRM_AFTER_HEATING = {"GTX0103A": (420, "Labelled NRM in the files, but measured after the 420 °C step (the 2G "
                                       "file gives 15 Dec 2023, 10:59 for 420 °C and 12:25 for this measurement) "
                                       "and before the alternating-field steps: a second measurement after heating "
                                       "to 420 °C.")}

# ------------------------------------------------------------------ paleointensity: text of the paper
# "The laboratory field applied for the in-field steps was 40 µT"; pTRM checks "starting from 300 ˚C";
# "All results were processed with the ThellierTool 4.2 software (Leonhardt et al., 2004)"; LTD:
# "including a LTD after each heating step and before each measurement ... submerging the specimens in a
# dewar filled with liquid nitrogen (-196 °C)". The experiments were made at Burgos ("UBU Laboratory of
# Paleomagnetism"), on "~8 mm diameter microcores".
THELLIER_LAB_FIELD = 40e-6
THELLIER_SOFTWARE = "ThellierTool 4.2"
# The in-field steps point to -Z in specimen coordinates (convert.py checks this on the files).
THELLIER_LAB_DEC, THELLIER_LAB_INC = 0, -90
# Suffix of every Thellier specimen: the microcores are distinct from the demagnetized specimens, and the
# file GTX0204B.TDT has the name of a demagnetized specimen (README.md, "Paleointensity").
THELLIER_SUFFIX = "t"
# Table III (table_iii.csv) gives the specimens of GTX10 as GTX1011, GTX1012 and LTD GTX1011 to GTX1014;
# the files are GTX10011.TDT, GTX10012.TDT and LTD_GTX10011.TDT to LTD_GTX10014.TDT (block GTX1001).
TABLE_III_FILE_NAMES = {("", "GTX1011"): "GTX10011", ("", "GTX1012"): "GTX10012",
                        ("yes", "GTX1011"): "LTD_GTX10011", ("yes", "GTX1012"): "LTD_GTX10012",
                        ("yes", "GTX1013"): "LTD_GTX10013", ("yes", "GTX1014"): "LTD_GTX10014"}
# Inferred (README.md, "Paleointensity"): two ranges of Table III hold a different number of steps from
# its N, and one other range gives N, B, beta, f and q of the table. LTD GTX08022 is printed 390-540 °C
# (7 steps, N = 8): 390-560 °C. GTX1011 is printed 20-500 °C (12 steps, N = 10): 200-500 °C.
TABLE_III_RANGE = {("yes", "GTX08022"): (390, 560), ("", "GTX1011"): (200, 500)}

# ------------------------------------------------------------------ Table II (appendix): selection criteria
# class: N, f, q, beta, dCK (percent), MAD' (degrees), alpha (degrees). Classes A and B are those of
# Paterson et al. (2014); C is added by the authors ("δ(CK) values ≤ 15").
TABLE_II = pd.DataFrame([
    ("A", 5, 0.35, 5, 0.10, 7, 6, 15),
    ("B", 5, 0.35, 0, 0.15, 9, 15, 15),
    ("C", 5, 0.35, 0, 0.15, 15, 15, 15),
], columns=["class", "n", "f", "q", "beta", "dck", "mad", "alpha"])
# column of the specimens table and operation for each criterion
TABLE_II_COLUMNS = OrderedDict([("n", ("int_n_measurements", ">=")), ("f", ("int_f", ">=")),
                                ("q", ("int_q", ">=")), ("beta", ("int_b_beta", "<=")),
                                ("dck", ("int_dck", "<=")), ("mad", ("int_mad_anc", "<=")),
                                ("alpha", ("int_alpha", "<="))])

# ------------------------------------------------------------------ Table 4: site paleointensities
# site; non-LTD B, ΔB, n, N; LTD B, ΔB, n, N; Diff.; mean B, ΔB; number of class A, B, C; n, N.
# None for "-". The caption defines the classes by δ(CK) differently from Table II (A ≤ 9, B ≤ 15).
TABLE4 = pd.DataFrame([
    ("GTX01", None, None, 0, 5, None, None, 0, 2, None, None, None, 0, 0, 0, 0, 7),
    ("GTX02", 27.8, 2.8, 3, 6, 27.4, 6.5, 3, 4, 0.3, 27.6, 4.5, 1, 2, 3, 6, 10),
    ("GTX03", 41.4, 4.0, 2, 6, 34.3, 1.1, 2, 4, 7.0, 37.9, 4.7, 1, 1, 2, 4, 10),
    ("GTX04", None, None, 0, 4, None, None, 0, 2, None, None, None, 0, 0, 0, 0, 6),
    ("GTX05", 11.6, 2.3, 5, 5, 9.4, 3.1, 3, 4, 2.2, 10.8, 2.6, 1, 2, 5, 8, 9),
    ("GTX06", 4.6, None, 1, 6, 3.0, 0.3, 2, 4, 1.6, 3.5, 0.9, 0, 3, 0, 3, 10),
    ("GTX07", 11.1, None, 1, 5, 7.7, None, 1, 3, 3.4, 9.4, 2.4, 0, 1, 1, 2, 8),
    ("GTX08", 31.2, None, 1, 4, 32.3, 3.9, 3, 4, -1.1, 32.0, 3.2, 1, 2, 1, 4, 8),
    ("GTX09", None, None, 0, 5, None, None, 0, 3, None, None, None, 0, 0, 0, 0, 8),
    ("GTX10", None, None, 0, 6, 30.8, 1.3, 3, 4, None, 30.8, 1.3, 0, 2, 1, 3, 10),
    ("GTX11", 28.3, 3.1, 5, 6, 29.9, 4.4, 2, 2, -1.7, 28.7, 3.2, 2, 3, 2, 7, 8),
    ("OL01", None, None, 0, 6, 38.8, None, 1, 3, None, 38.8, None, 0, 0, 1, 1, 9),
    ("OL02", 18.0, 4.7, 5, 6, 13.1, 3.5, 3, 3, 4.9, 16.1, 4.7, 5, 3, 0, 8, 9),
    ("OL03", None, None, 0, 7, None, None, 0, 2, None, None, None, 0, 0, 0, 0, 9),
    ("OL04", 42.0, 2.2, 4, 6, 35.1, 8.1, 2, 2, 6.9, 39.7, 5.4, 1, 4, 1, 6, 8),
], columns=["site", "b_std", "db_std", "n_std", "N_std", "b_ltd", "db_ltd", "n_ltd", "N_ltd", "diff", "b", "db",
            "class_a", "class_b", "class_c", "n", "N"])
# Table 4, last rows: accepted 27/83 (32.5%) without LTD, 25/46 (54.3%) with, 52/129 (40.3%) in all;
# classes A 12, B 23, C 17; mean difference 2.6 µT. The text gives "52.2%" for the LTD specimens.
TABLE4_TOTALS = dict(n_std=27, N_std=83, n_ltd=25, N_ltd=46, n=52, N=129, class_a=12, class_b=23, class_c=17,
                     mean_diff=2.6)

# ------------------------------------------------------------------ rock magnetism (text)
# "rock magnetic experiments were performed with a Variable Field Translation Balance (VFTB) at the
# University of Burgos ... on one grinded representative sample per lava flow (~0.3 g) ... IRM acquisition,
# hysteresis loops (± 1T), backfield, and magnetization vs. temperature curves up to 700 °C. Data were
# processed with the RockMag Analyzer 1.1 software". The paper gives no values per sample (Day plot,
# Fig. 2C). Thermal stability: "magnetization-temperature cycling experiments, starting from a 1 T imparted
# IRM at room temperature and heated to peak temperatures between 500°C and 560°C in a constant field of
# 38 mT".
ROCKMAG_SUFFIX = "r"
THERMAL_STABILITY_SUFFIX = "s"
# Table IV: the files of each row, in the order T1, T2, T3 (from the file names, the temperatures in them
# and the folder). GTX0705 is OLO705B_560.rmp in the folder GTX07, named GTX705B inside. GTX0604 has two
# files of the same specimen at 560 °C. OLO202 and OLO401 have none ("No data").
TABLE_IV_FILES = {
    "GTX0206": ["GTX206_540"], "GTX0208": ["GTX0208B"], "GTX0308": ["GTX0308B_500", "GTX308B_570"],
    "GTX0309": ["GTX309B_500", "GTX309B_600"], "GTX0501": ["GTX501B_500", "GTX501B_600"],
    "GTX0503": ["GTX503B_500", "GTX503B_600"], "GTX0504": ["GTX504B_560"],
    "GTX0505": ["GTX5-5_500", "GTX5-5_560", "GTX5-5_600"], "GTX0506": ["GTX506B_550"],
    "GTX0604": ["GTX604B_560", "GTX604_560"], "GTX0605": ["GTX0605A_560"], "GTX0705": ["OLO705B_560"],
    "GTX0802": ["GTX0802_500"], "GTX0803": ["GTX803_250", "GTX803_300"], "GTX1001": ["GTX10-1_450", "GTX10-1_520"],
    "GTX1003": ["GTX1003_500"], "GTX1101": ["GTX1101_500", "GTX1101_600"], "GTX1102": ["GTX1102_500", "GTX1102_600"],
    "GTX1103": ["GTX1103_560"], "OLO106": ["OLO106_250", "OLO106_300"], "OLO201": ["OLO201A_520"],
    "OLO202": [], "OLO203": ["OLO203B_540"], "OLO204": ["OLO204C_560"], "OLO209": ["OLO209C_540"],
    "OLO210": ["OLO210B_500", "OLO210B_600"], "OLO401": [], "OLO404": ["OLO404A_450", "OLO404A_520"],
    "OLO407": ["OLO407A_450", "OLO407A_500"], "OLO409": ["OLO409C_500", "OLO409C_600"],
    "OLO410": ["OLO410B_500", "OLO410B_600"]}
