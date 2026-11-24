"""Values transcribed from Yuan et al. (2025), and the choices made in the conversion, as
named constants. Nothing is calculated here. The comment above each block gives its source,
and README.md gives the reasons for the choices. The specimen directions (Table S3 of the
supplement) are in table_s3.csv, made by extract_table_s3.py.

    Yuan, J., Hao, W., & Qiu, R. (2025). New paleomagnetic and geochronologic results from
    the eastern Tethyan Himalaya refine the size of Greater India in the Early Cretaceous.
    Journal of Asian Earth Sciences, 278, 106428. https://doi.org/10.1016/j.jseaes.2024.106428
"""

PAPER_DOI = "10.1016/j.jseaes.2024.106428"
DATA_DOI = "10.57760/sciencedb.15244"

# ------------------------------------------------------------------ text of the paper
# Section 3: "All the rock magnetic and paleomagnetic measurements were performed at the
# Paleomagnetism and Geochronology Laboratory (PGL), Institute of Geology and Geophysics,
# Chinese Academy of Sciences." The name is the MagIC vocabulary item.
LABORATORIES = "Paleomagnetism and Geochronology Lab Beijing (Chinese Academy of Sciences, China)"
# Shown with the contribution in MagIC. <permalink> is the link to this folder at the commit the
# upload was built from, given by `python common/studies.py --permalink yuan_2025_jiabula`.
CONTRIBUTION_DESCRIPTION = (
    "Built from Table S3 of the supplement, which the authors archived at Science Data Bank "
    "(https://doi.org/10.57760/sciencedb.15244), and from the paper. Sources, choices and checks are "
    "documented at <permalink>.")

LOCATION = "Jiabula Formation, Zhangda section"
FORMATION = "Jiabula Formation"
# Section 1: "the Zhangda section (28.9°N, 91.1°E)". One coordinate pair for the section; no site coordinates.
LAT, LON = 28.9, 91.1
COORDINATE_PRECISION = 0.1  # degrees: the precision of the printed coordinates
# Section 2: "grey medium bedded limestone in the lower part"; "242 core samples at 27 sites from
# limestone beds ... from the lower part of the Zhangda section"
GEOLOGIC_CLASSES, GEOLOGIC_TYPES, LITHOLOGIES = "Sedimentary", "Sediment Layer", "Limestone"
# Section 2: "using a gasoline-powered portable drill"; "oriented using both magnetic and sun compasses"
SAMPLING_CODES = "FS-FD:SO-MAG:SO-SUN"
# Section 3: stepwise thermal demagnetization; "fitted by principal component analysis (Kirschvink, 1980)";
# "analyzed using the Paleomac software"; "classic Fisher statistics". Whether the lines were anchored
# to the origin is not said.
SOFTWARE = "PaleoMac"
COMPONENT = "HTC"
N_CORES, N_FIELD_SITES, N_SPECIMENS_CUT = 242, 27, 280

# ------------------------------------------------------------------ ages (sections 2 and 4.1)
# Section 4.1: youngest zircon dates of sandstone WMD01 (126.2 and 126.7 Ma) and andesite SX162-165
# (125.8 Ma): "interpreted as the maximum allowable depositional age of the Jiabula Formation ...
# We used ca. 126 Ma for the Jiabula Formation in further discussion."
AGE, AGE_OLDER = 126.0, 126.7
# Section 2: "the Lower Cretaceous Jiabula Formation, and the Upper Cretaceous Zongzhuo Formation".
# The paper gives no younger numerical bound, so the top of the Lower Cretaceous is used: 100.5 Ma in
# the International Chronostratigraphic Chart (choice, README.md).
AGE_YOUNGER = 100.5
CHART = "International Chronostratigraphic Chart v2024/12"

# ------------------------------------------------------------------ mean directions (section 4.4, Fig. 6)
# High-temperature component, 204 specimens, "between about 350 °C and 525 °C"
HTC_TILT_CORRECTED = dict(dec=140.5, inc=60.0, k=25.7, a95=2.0, n=204)
HTC_IN_SITU = dict(dec=131.6, inc=5.8, k=14.2, a95=2.7, n=204)
# Low-temperature component, 268 specimens, "between 20 °C and 350 °C"; no specimen directions published
LTC_IN_SITU = dict(dec=358.1, inc=44.3, k=122.4, a95=0.8, n=268)
LTC_TILT_CORRECTED = dict(dec=339.8, inc=3.6, k=30.3, a95=1.6, n=268)

# ------------------------------------------------------------------ pole (abstract, section 4.5)
# "paleopole of 11.2°N/300.5°E, A95 = 2.6°, with a paleolatitude of 40.9° ± 2.6°S at ca. 126 Ma"
POLE = dict(lat=11.2, lon=300.5, a95=2.6)
PALEOLATITUDE, PALEOLATITUDE_SIGMA = -40.9, 2.6

# ------------------------------------------------------------------ field tests (section 4.4)
# McElhinny (1964): "ks/kg = 1.81 > F (406, 406) at 5 % point = 1.18 and at 1 % point = 1.26"
MCELHINNY_RATIO = 1.81
# McFadden (1990): xi2 94.62 in situ and 5.44 tilt-corrected; critical values 16.61 (95 %) and 23.49 (99 %)
MCFADDEN_XI2 = dict(in_situ=94.62, tilt_corrected=5.44, critical_95=16.61, critical_99=23.49)
# Watson and Enkin (1993): "a maximum precision parameter (kmax = 25.6) at 100 % unfolding"
UNFOLDING = dict(k_max=25.6, percent=100)
FOLD_TEST = "F+"

# ------------------------------------------------------------------ inclination shallowing (section 4.5, Fig. 7)
# E/I analysis of the 204 directions: corrected inclination 63.0° (59.0° to 69.0°). After "a fixed 45°
# cutoff", 197 directions: Ds 140.6°, Is 59.3°, k 29.3, alpha95 1.9°; corrected inclination 61.0°
# (59.0° to 64.0°). The authors conclude that no significant shallowing occurred and use the uncorrected mean.
EI_ALL = dict(inc=63.0, low=59.0, high=69.0)
CUTOFF = dict(angle=45.0, dec=140.6, inc=59.3, k=29.3, a95=1.9, n=197)
EI_CUTOFF = dict(inc=61.0, low=59.0, high=64.0)

# ------------------------------------------------------------------ choices (README.md)
# Table S3 prints zl02-1 with the bedding of site ZL01 (strike 212, dip 46). Its tilt-corrected direction
# follows from the bedding of the other six ZL02 specimens (strike 203, dip 49), which is entered.
BEDDING_INFERRED = {"zl02-1": (203.0, 49.0)}
# A printed tilt-corrected direction is taken as reproduced within this angle of the rotated one
# (the directions are printed to 0.1 degree).
TILT_TOLERANCE = 0.15
# GPMDB (Pisarevsky et al., 2022) result number of the pole
GPMDB_RESULT = 10396
