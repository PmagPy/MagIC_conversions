"""Values transcribed from Calvo Rathert et al. (2022) and its supporting information,
and the choices made in the conversion, as named constants. Nothing is calculated here.
The comment above each block gives its source, and README.md gives the reasons for the
choices.

    Calvo Rathert, M., Carrancho, Á., Morales, J., Pérez-Rodríguez, N., Lebedev, V. A.,
    Caccavari, A., Vegas, N., & Goguitchaichvili, A. (2022). Multimethod palaeointensity
    results from a rapidly emitted upper Miocene lava flow sequence in São Vicente
    (Cape Verde): new data for the African record. Geophysical Journal International,
    231(1), 215-229. https://doi.org/10.1093/gji/ggac173
"""

import pandas as pd

PAPER_DOI = "10.1093/gji/ggac173"
DATA_DOI = "10.5281/zenodo.5553392"

# ------------------------------------------------------------------ text of the paper
# Section 5: measurements at the University of Burgos. Section 7.2: the multispecimen experiments
# at UNAM in Morelia. The names are the MagIC vocabulary items.
LABORATORIES = ("Paleomagnetic and Rock Magnetic Laboratory (Universidad de Burgos, Spain):"
                "Interinstitutional Laboratory of Natural Magnetism (UNAM Morelia, Mexico)")
# Shown with the contribution in MagIC. <permalink> is the link to this folder at the commit the
# upload was built from, given by `python common/studies.py --permalink calvo-rathert_2022_praia_grande`.
CONTRIBUTION_DESCRIPTION = (
    "Converted from the laboratory files archived by the authors (https://doi.org/10.5281/zenodo.5553392) "
    "and from the paper and its supporting information. Sources, choices and checks are documented at "
    "<permalink>.")
LOCATION = "Praia Grande"
# Section 2: "nephelinitic lava flows"
GEOLOGIC_CLASSES, GEOLOGIC_TYPES, LITHOLOGIES = "Extrusive:Igneous", "Lava Flow", "Nephelinite"
# Section 2: K-Ar on the groundmass of the lowermost flow, PRG1: 6.07 ± 0.16 Ma (2 sigma)
AGE, AGE_2SIGMA = 6.07, 0.16
# Section 8.2: K-Ar age combined with the normal polarity of all flows (subchron C3An.1n,
# 6.033-6.252 Ma in Gradstein et al., 2004): "between 6.03 and 6.23 Ma"
AGE_LOW, AGE_HIGH = 6.03, 6.23
# Section 2: "a portable core drill"; "Both a solar and a magnetic compass were used"
ORIENTATION_CODES = "FS-FD:SO-SUN:SO-MAG"
# Section 7.1: Thellier-Coe experiments in a laboratory field of 40 microtesla
THELLIER_LAB_FIELD = 40e-6

# ------------------------------------------------------------------ Figure 1b
# The section is the red star on a map with a 4' graticule (N 16°46' to 16°54',
# W 24°52' to 25°00'); the paper gives no coordinates. Georeferenced on the figure image
# embedded in the PDF (2341 x 824 px): ticks of W 25°00', 24°56', 24°52' at x = 1567, 1844.5,
# 2122 and of N 16°54', 16°50', 16°46' at y = 126.5, 412.5, 700.5 (linear within 0.6"); the
# centroid of the star's red pixels is at x = 2012.0, y = 280.3, i.e. 16.8642°N, 24.8931°W.
# The Mindelo marker on the same map georeferences 0.35 km from Mindelo in OpenStreetMap.
LAT, LON = 16.864, round(360 - 24.893, 3)

# ------------------------------------------------------------------ decisions (see README.md)
# The authors' names for the characteristic component in the Remasoft files start with CA.
CHRM = "CA"
# Distinct specimens need distinct names (N. Swanson-Hysell, 2026-11-10). Thellier specimens
# are fragments published under the names of demagnetized specimens; multispecimen
# sub-specimens and rock-magnetic powders are named like cores. Each kind gets a suffix.
THELLIER_SUFFIX = "t"
MULTISPECIMEN_SUFFIX = "m"
ROCKMAG_SUFFIX = "r"
# Tilt is taken not to be an issue for these ca. 6 Ma lavas (N. Swanson-Hysell, 2026-11-10).
UNTILTED = ("No bedding or structural correction is reported; the flows are taken as untilted and the "
            "direction is in geographic coordinates.")
# Units of the moments in the demagnetization and Thellier files (README.md, "Units"): the values
# are taken as emu/cm3, the volume-normalized output of the 2G software, and multiplied by this
# factor to A/m. Table S1 of the same study shows the same factor of 1000 between the archived
# curves and its SI values.
EMU_PER_CM3_TO_A_PER_M = 1000.0
# The note on the rows of the specimens whose moments this assumption affects
UNITS_NOTE = ("The moments of the archived file are read as emu/cm3 (the file gives A/m or no unit) and "
              "multiplied by 1000 to A/m; if they were per gram, the magnetizations would be about 2.9 times "
              "higher (README, Units).")
# Density used only in the report, to compare volume- and mass-normalized values.
DENSITY = 2900.0

# ------------------------------------------------------------------ Table 1: paleomagnetic results
# flow, N (samples in the mean), n (specimens measured), dec, inc, alpha95, k, VGP lat, VGP lon.
# The table labels the flows "PGR"; the files and the text use "PRG".
TABLE1 = pd.DataFrame(
    [("PRG1", 6, 6, 330.6, 28.4, 2.3, 872, 61.7, 245.8),
     ("PRG2", 8, 8, 328.2, 33.3, 8.1, 48, 59.7, 252.4),
     ("PRG3", 8, 8, 329.7, 26.4, 3.4, 260, 60.7, 243.6),
     ("PRG4", 7, 7, 332.8, 27.4, 5.5, 122, 63.7, 243.9),
     ("PRG5", 7, 7, 335.1, 29.6, 5.4, 127, 66.1, 243.6),
     ("PRG6", 8, 9, 332.7, 28.7, 3.4, 269, 63.7, 245.6),
     ("PRG7", 8, 9, 332.2, 33.1, 3.9, 199, 63.5, 251.9),
     ("PRG8", 7, 8, 335.4, 31.5, 5.8, 111, 66.5, 249.2),
     ("PRG9", 6, 6, 334.4, 29.6, 5.8, 132, 65.4, 246.5),
     ("PRG10", 8, 8, 333.2, 26.9, 3.2, 307, 64.1, 243.1),
     ("PRG11", 2, 2, 329.0, 31.9, 5.0, 2467, 60.4, 250.6)],
    columns=["site", "N", "n_measured", "dec", "inc", "a95", "k", "vgp_lat", "vgp_lon"])
TABLE1_MEAN = dict(N=11, dec=332.1, inc=29.7, a95=1.8, k=631, vgp_lat=63.3, vgp_lon=247.0)

# ------------------------------------------------------------------ Table 2: Thellier-Coe determinations
# specimen, range (deg C), N, f, q, sigma/slope, d(CK), k', MAD, alpha, B (microtesla),
# standard error of B, class
TABLE2_THELLIER = pd.DataFrame(
    [("PRG1-1A", 20, 512, 7, 0.74, 14.4, 0.047, 4.7, 0.029, 3.5, 0.9, 19.5, 0.8, "C1"),
     ("PRG1-2A", 20, 484, 6, 0.62, 10.5, 0.042, 4.7, 0.071, 2.9, 0.5, 17.4, 0.7, "C1"),
     ("PRG1-3A", 20, 512, 7, 0.64, 15.9, 0.030, 1.1, 0.049, 5.3, 2.7, 18.2, 0.6, "C1"),
     ("PRG1-5A", 328, 512, 5, 0.60, 12.3, 0.036, 6.7, 0.081, 5.4, 5.3, 18.1, 0.7, "C1"),
     ("PRG1-7A", 226, 512, 6, 0.74, 65.0, 0.001, 2.6, 0.053, 3.0, 1.2, 17.7, 0.1, "C1"),
     ("PRG1-8", 226, 584, 9, 0.84, 35.1, 0.020, 4.2, 0.129, 5.4, 3.3, 17.2, 0.3, "C2"),
     ("PRG2-4A", 20, 512, 7, 0.55, 17.3, 0.024, 3.8, 0.220, 2.5, 1.5, 17.7, 0.5, "C2"),
     ("PRG3-1A", 20, 512, 7, 0.48, 12.1, 0.033, 3.4, 0.040, 3.0, 3.8, 22.5, 0.8, "C2"),
     ("PRG3-2A", 20, 565, 9, 0.64, 10.4, 0.052, 5.6, 0.138, 3.1, 3.5, 19.1, 1.0, "C1"),
     ("PRG3-3", 20, 537, 8, 0.52, 12.0, 0.037, 5.9, 0.130, 6.0, 4.4, 25.3, 0.9, "C1"),
     ("PRG3-4", 20, 537, 8, 0.59, 10.7, 0.046, 7.2, 0.010, 4.0, 4.8, 19.3, 0.9, "C2"),
     ("PRG3-6A", 20, 512, 7, 0.41, 7.8, 0.045, 1.7, 0.140, 7.2, 5.7, 17.0, 0.8, "C2"),
     ("PRG3-7C", 20, 512, 7, 0.48, 7.3, 0.055, 3.0, 0.090, 5.0, 1.9, 23.2, 1.3, "C2"),
     ("PRG3-8", 20, 512, 7, 0.55, 6.9, 0.065, 2.3, 0.232, 3.6, 3.1, 19.1, 1.3, "C2"),
     ("PRG4-2A", 328, 537, 6, 0.55, 6.4, 0.067, 7.0, 0.258, 4.1, 4.8, 19.2, 1.3, "C2"),
     ("PRG4-3B", 20, 512, 7, 0.40, 4.8, 0.068, 4.3, 0.091, 5.5, 5.7, 21.4, 1.5, "C2"),
     ("PRG4-4", 328, 512, 5, 0.45, 4.2, 0.077, 2.2, 0.237, 2.7, 2.7, 18.7, 1.4, "C2"),
     ("PRG4-5A", 20, 512, 6, 0.54, 5.9, 0.071, 4.2, 0.044, 6.3, 8.5, 19.9, 1.4, "C2"),
     ("PRG4-6", 20, 537, 8, 0.60, 9.4, 0.053, 3.6, 0.135, 4.0, 2.4, 19.3, 1.0, "C1"),
     ("PRG4-8", 20, 512, 7, 0.50, 4.3, 0.093, 4.8, 0.235, 5.6, 0.6, 25.6, 2.4, "C2"),
     ("PRG9-6A", 328, 512, 5, 0.62, 8.9, 0.091, 1.7, 0.139, 7.0, 5.9, 12.0, 0.6, "C2"),
     ("PRG11-2A", 389, 565, 6, 0.84, 6.8, 0.084, 1.8, 0.221, 2.4, 1.0, 10.0, 0.8, "C2")],
    columns=["specimen", "t_min", "t_max", "N", "f", "q", "beta", "dck", "k_prime", "mad", "alpha",
             "B", "B_sigma", "class"])

# ------------------------------------------------------------------ Table 2: multispecimen determinations
# flow, B, Bmin, Bmax (microtesla), N used, r rejected, determination type, R2, average alteration
# (percent), b / intersection, class. Types: DB standard (Dekkers and Böhnel), FC fraction
# corrected (Fabian and Leonhardt); a trailing "c" means alignment corrected.
TABLE2_MULTISPECIMEN = pd.DataFrame(
    [("PRG1", 18.7, 16.0, 20.0, 6, 1, "FCc", 0.972, -0.9, "-0.03/YES", "C1"),
     ("PRG2", 15.1, 9.1, 23.8, 5, 2, "DBc", 0.977, -17.5, "N.A.", "C2"),
     ("PRG3", 19.1, 13.2, 22.1, 6, 1, "FCc", 0.975, -2.6, "-0.01/YES", "C1"),
     ("PRG4", 18.3, 10.5, 22.2, 6, 1, "FCc", 0.920, -4.5, "-0.04/YES", "C1"),
     ("PRG5", 20.1, 14.2, 27.7, 6, 1, "DBc", 0.944, -14.2, "N.A.", "C2"),
     ("PRG7", 15.5, 7.9, 18.5, 6, 1, "DBc", 0.961, -5.0, "N.A.", "C1"),
     ("PRG10", 17.7, 12.6, 26.1, 7, 0, "DBc", 0.930, -10.1, "N.A.", "C2"),
     ("PRG11", 18.9, 12.8, 21.2, 7, 0, "DB", 0.943, -6.0, "N.A.", "C1")],
    columns=["site", "B", "B_min", "B_max", "N", "rejected", "type", "r2", "eps_alt", "b_intersection",
             "class"])

# ------------------------------------------------------------------ Table 2: selection criteria
# (statistic, MagIC column or None, operation, class C1 threshold, class C2 threshold)
THELLIER_CRITERIA = [
    ("N", "specimens.int_n_measurements", ">=", 5, 5),
    ("f", "specimens.int_f", ">=", 0.50, 0.35),
    ("q", "specimens.int_q", ">=", 5, 1),
    ("sigma/slope", "specimens.int_b_beta", "<=", 0.100, 0.150),
    ("d(CK)", "specimens.int_dck", "<=", 7, 9),
    ("k'", "specimens.int_k_prime", "<=", 0.164, 0.270),
    ("MAD", "specimens.int_mad_anc", "<=", 6, 15),
    ("alpha", "specimens.int_alpha", "<=", 15, 15)]
MULTISPECIMEN_CRITERIA = ("N >= 6 (C1) or 5 (C2); R2 >= 0.9 (C1) or 0.85 (C2); average alteration <= 10 "
                          "percent (C1) or 20 percent (C2); b <= 0.1 and within error (C1) or <= 0.15 "
                          "and/or within error (C2)")
# Table 3: threshold for a flow mean: standard deviation <= 15 percent of the mean, or <= 5 microtesla
FLOW_MEAN_SIGMA_PERCENT, FLOW_MEAN_SIGMA_MICROTESLA = 15, 5

# ------------------------------------------------------------------ Table 3: flow means
# flow, treatment, N (samples; a multispecimen result counts as one), B, standard deviation
# (Coe and Coe + MS) or (Bmin, Bmax) (MS), percent as printed, class as printed ("" if none)
TABLE3 = pd.DataFrame(
    [("PRG1", "Coe", 6, 18.0, 0.8, None, None, 4.4, ""),
     ("PRG1", "Coe + MS", 7, 18.1, 0.4, None, None, 3.9, "1"),
     ("PRG2", "Coe + MS", 2, 16.4, 1.8, None, None, 11.0, "2"),
     ("PRG3", "Coe", 7, 20.8, 2.9, None, None, 13.9, ""),
     ("PRG3", "Coe + MS", 8, 20.6, 2.8, None, None, 13.6, "1"),
     ("PRG4", "Coe", 6, 20.7, 2.6, None, None, 12.6, ""),
     ("PRG4", "Coe + MS", 7, 20.3, 2.5, None, None, 12.3, "1"),
     ("PRG5", "MS", 1, 20.1, None, 14.2, 27.7, None, "3"),
     ("PRG7", "MS", 1, 15.5, None, 7.9, 18.5, None, "3"),
     ("PRG9", "Coe", 1, 12.0, 0.6, None, None, 5.0, "4"),
     ("PRG10", "MS", 1, 17.7, None, 12.6, 26.1, None, "3"),
     ("PRG11", "Coe", 1, 10.0, 0.8, None, None, 8.0, ""),
     ("PRG11", "MS", 1, 18.9, None, 12.8, 21.2, None, "3")],
    columns=["site", "treatment", "N", "B", "sigma", "B_min", "B_max", "percent", "class"])
# Section 8: the quality classes of a flow result
CLASSES = {
    "1": "class 1: a Thellier-Coe flow mean of at least three determinations coincides with a successful "
         "multispecimen determination",
    "2": "class 2: a Thellier-Coe flow mean of fewer than three determinations coincides with a successful "
         "multispecimen determination, or a mean of at least three has no multispecimen result or does "
         "not agree with it",
    "3": "class 3: a successful multispecimen result but no Thellier-Coe result",
    "4": "class 4: fewer than three Thellier-Coe results and no multispecimen result"}
# Table 3, last rows: means of the flow results (microtesla; VADM in 10^22 Am2; N flows)
SEQUENCE_MEANS = [
    dict(classes="1 and 2", B=18.9, sigma=2.0, vadm=4.4, vadm_sigma=0.5, N=4,
         sites=["PRG1", "PRG2", "PRG3", "PRG4"]),
    dict(classes="1 to 3", B=18.5, sigma=1.9, vadm=4.3, vadm_sigma=0.4, N=8,
         sites=["PRG1", "PRG2", "PRG3", "PRG4", "PRG5", "PRG7", "PRG10", "PRG11"])]

# ================================================================== supporting information
# "Supporting Information for ..." of the paper (10 pages: Figure S1, Tables S1 to S4).
# Table S2 (a model calculation of secular variation) holds no data of this study.

# ------------------------------------------------------------------ Table S1: rock-magnetic results
# sample, Mrs, Ms (printed "Am2/kg"), Bc, Bcr (mT), Mrs/Ms, Bcr/Bc, Brh/Bcr, shape parameter sigma,
# S(0.3 T), then four Curie temperatures (deg C) in the printed column order TC1(H), TC2(H),
# TC1(C), TC2(C). The H columns are 20 to 50 degrees higher than the C columns, as the text says
# of the heating branch against the cooling branch; the table caption assigns them the other way.
TABLE_S1 = pd.DataFrame(
    [("PRG1-2", 1.07e-4, 3.25e-4, 27.98, 52.80, 0.33, 1.89, 1.17, -0.51, 0.95, 557, None, 504, None),
     ("PRG2-4", 1.58e-4, 1.09e-3, 17.78, 42.81, 0.14, 2.41, 1.54, -0.86, 0.98, 579, None, 564, None),
     ("PRG3-5", 1.42e-4, 8.88e-4, 17.17, 42.36, 0.16, 2.47, 1.58, -0.72, 0.96, 579, None, 558, None),
     ("PRG4-2", 1.70e-4, 1.04e-3, 19.80, 49.10, 0.16, 2.48, 1.53, -0.80, 0.96, 588, None, 564, None),
     ("PRG5-6", 3.42e-4, 1.33e-3, 22.84, 59.21, 0.26, 2.59, 1.40, -0.52, 0.98, 578, 102, 555, 66),
     ("PRG6-7", 5.77e-4, 2.03e-3, 26.99, 54.52, 0.28, 2.02, 1.39, -0.71, 0.99, 576, None, 549, None),
     ("PRG7-8", 4.44e-4, 1.41e-3, 41.34, 69.02, 0.32, 1.67, 1.33, -0.85, 1.00, 579, None, 552, None),
     ("PRG8-7", 3.28e-4, 1.19e-3, 28.25, 70.45, 0.28, 2.49, 1.36, -0.53, 0.98, 572, None, 545, None),
     ("PRG9-8", 3.85e-4, 2.44e-3, 20.89, 41.76, 0.16, 2.00, 1.83, -0.94, 0.98, 587, None, 564, None),
     ("PRG10-5", 7.54e-4, 1.89e-3, 53.37, 75.40, 0.40, 1.41, 1.28, -0.84, 0.98, 573, None, 549, None),
     ("PRG11-1", 4.37e-4, 1.28e-3, 40.37, 65.50, 0.34, 1.62, 1.27, -0.83, 0.98, 570, None, 543, None)],
    columns=["sample", "mrs", "ms", "bc", "bcr", "mrs_ms", "bcr_bc", "brh_bcr", "sigma", "s_ratio",
             "tc1_heating", "tc2_heating", "tc1_cooling", "tc2_cooling"])
# The printed Mrs and Ms are 1000 times smaller than the archived curves in emu/g (= Am2/kg);
# they are entered in Am2/kg after multiplying by this factor (README.md, "Units").
TABLE_S1_MOMENT_FACTOR = 1000.0

# ------------------------------------------------------------------ Table S3: all multispecimen protocols
# flow, protocol, F, Fmin, Fmax (microtesla), N used, r rejected, average alteration (percent),
# ordinate intercept, R2. Rows printed "No coherent results" are left out. The table labels most
# flows "PGR". None where the table is blank.
TABLE_S3 = pd.DataFrame(
    [("PRG1", "DB", 18.8, 15.1, 20.1, 7, 0, -0.9, None, 0.990),
     ("PRG1", "FC", 2.8, None, None, 7, 0, -0.9, 1.21, 0.194),
     ("PRG1", "DSC", 2.8, None, None, 7, 0, -0.9, 1.22, 0.178),
     ("PRG1", "DBc", 18.8, 14.0, 20.1, 7, 0, -0.9, None, 0.990),
     ("PRG1", "FCc", 18.7, 16.0, 20.0, 6, 1, -0.9, -0.03, 0.972),
     ("PRG1", "DSCc", 18.6, 14.8, 21.2, 7, 0, -0.9, -0.19, 0.943),
     ("PRG2", "DB", 15.1, 9.1, 23.5, 5, 2, -21.5, None, 0.979),
     ("PRG2", "DBc", 15.1, 9.1, 23.8, 5, 2, -17.5, None, 0.977),
     ("PRG3", "DB", 19.3, 9.5, 22.8, 7, 0, -1.1, None, 0.938),
     ("PRG3", "FC", 20.0, 15.0, 29.8, 6, 1, -1.1, -2.39, 0.896),
     ("PRG3", "DSC", 19.2, 14.6, 28.3, 6, 1, -1.1, -2.12, 0.924),
     ("PRG3", "DBc", 19.3, 8.4, 22.7, 7, 0, -1.1, None, 0.937),
     ("PRG3", "FCc", 19.1, 13.2, 22.1, 6, 1, -2.6, -0.01, 0.975),
     ("PRG3", "DSCc", 17.6, 10.6, 20.6, 6, 1, -1.1, 0.06, 0.966),
     ("PRG4", "DB", 20.7, 14.6, 26.9, 7, 0, -4.4, None, 0.906),
     ("PRG4", "DBc", 21.0, 14.4, 28.6, 7, 0, -4.0, None, 0.875),
     ("PRG4", "FCc", 18.3, 10.5, 22.2, 6, 1, -4.5, -0.04, 0.920),
     ("PRG4", "DSCc", 16.2, 6.7, 20.5, 6, 1, -3.6, 0.08, 0.932),
     ("PRG5", "DB", 20.2, 14.0, 27.7, 6, 1, -14.5, None, 0.945),
     ("PRG5", "DBc", 20.1, 14.2, 27.7, 6, 1, -14.2, None, 0.944),
     ("PRG5", "FCc", 17.4, None, 32.4, 6, 1, -15.0, -2.42, 0.739),
     ("PRG5", "DSCc", 15.9, None, 31.2, 6, 1, -15.0, -2.58, 0.753),
     ("PRG6", "DB", 7.3, None, 17.9, 7, 0, -17.6, None, 0.809),
     ("PRG6", "DBc", 7.2, None, 17.9, 7, 0, -17.4, None, 0.810),
     ("PRG7", "DB", 13.6, None, 17.8, 7, 0, -6.2, None, 0.910),
     ("PRG7", "DBc", 15.5, 7.3, 18.4, 6, 1, -5.0, None, 0.961),
     ("PRG8", "DSCc", 14.5, 8.3, 19.6, 4, 3, -14.8, -64.51, 0.828),
     ("PRG9", "DB", 13.7, None, 28.3, 6, 1, -20.3, None, 0.802),
     ("PRG9", "FC", 203.6, None, None, 7, 0, -18.2, -1.27, 0.819),
     ("PRG9", "DSC", 164.6, None, None, 6, 1, -20.3, -1.94, 0.855),
     ("PRG9", "DBc", 13.6, None, 28.6, 6, 1, -20.1, None, 0.800),
     ("PRG10", "DB", 17.8, 12.7, 26.5, 7, 0, -10.7, None, 0.931),
     ("PRG10", "DBc", 17.7, 12.6, 26.1, 7, 0, -10.1, None, 0.930),
     ("PRG10", "DSCc", 12.7, 10.4, 16.1, 4, 3, -11.1, -0.44, 0.959),
     ("PRG11", "DB", 18.9, 12.8, 21.2, 7, 0, -6.0, None, 0.943),
     ("PRG11", "FC", 17.7, 4.8, 26.5, 6, 1, -6.1, -2.64, 0.645),
     ("PRG11", "DSC", 19.3, 13.8, 29.4, 5, 2, -6.5, -2.55, 0.919),
     ("PRG11", "DBc", 18.8, 12.2, 20.8, 7, 0, -5.8, None, 0.942),
     ("PRG11", "FCc", 20.6, 15.2, 29.3, 5, 2, -6.3, -2.23, 0.902),
     ("PRG11", "DSCc", 19.2, 13.9, 28.3, 5, 2, -6.3, -2.45, 0.921)],
    columns=["site", "type", "B", "B_min", "B_max", "N", "rejected", "eps_alt", "intercept", "r2"])

# ------------------------------------------------------------------ Table S4: K-Ar dating of PRG-1
K_AR = ("K-Ar on groundmass of flow PRG1 (sample PRG-1): K 0.752 ± 0.015 percent, radiogenic 40Ar "
        "0.317 ± 0.002 ng/g, atmospheric 40Ar 76.4 percent, age 6.07 ± 0.16 Ma at 2 sigma (Table S4)")
