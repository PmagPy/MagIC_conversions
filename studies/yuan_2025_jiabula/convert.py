"""Build the MagIC contribution for the Jiabula Formation, Zhangda section (Yuan et al., 2025).

Inputs: the specimen directions of Table S3 of the supplement (table_s3.csv, made from
data/supplementary_materials.pdf by extract_table_s3.py) and the values transcribed from
the paper (published.py). No measurement files are public, so no converter of
pmagpy.convert_2_magic applies. report.md gives the source of each part of the contribution:

    table      Table S3 of the supplement: the high-temperature component of 204 specimens
    text       mean directions, pole, field tests, age, lithology, laboratory, methods
    inferred   from recalculation, where the table and the paper leave something open
               (the bedding of one specimen)

Outputs, next to this script:
    magic_contribution.txt   the contribution
    report.md                contents, checks against the paper, and what is missing
    directions.png           the specimen directions and their means, in both coordinate systems
    build/                   the tables before they are joined (not kept in the repository)

The calculations are those of PmagPy: tilt corrections with pmag.dotilt, Fisher means with
pmag.fisher_mean, angles with pmag.angle, poles with pmag.dia_vgp, the paleolatitude with
pmag.plat, the elongation/inclination analysis with ipmag.find_ei, the plot with
ipmag.plot_net, plot_di and plot_di_mean, and the validation with pmagpy.magic_validation.

Usage:
    python convert.py

The two elongation/inclination analyses bootstrap 1000 times each, so the build takes
several minutes.

Requires numpy, pandas, matplotlib and pmagpy (see the repository README).
"""

import contextlib
import io
import re
import sys
from collections import OrderedDict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pmagpy import ipmag  # noqa: E402
from pmagpy import pmag  # noqa: E402

import published as pub  # noqa: E402

STUDY_DIR = Path(__file__).resolve().parent
REPO_DIR = STUDY_DIR.parents[1]
sys.path.insert(0, str(REPO_DIR))
from common.magic_tools import md_table, validate_upload_file, whole_numbers, write_upload_file  # noqa: E402
from common.studies import write_build_summary  # noqa: E402

BUILD_DIR = STUDY_DIR / "build"
IN_SITU, TILT_CORRECTED = 0, 100
# the bootstrap of ipmag.find_ei: number of pseudo-samples, and a seed so that a rebuild gives the same numbers
EI_BOOTSTRAPS, EI_SEED = 1000, 1
# The bootstrap is random, so its inclinations change with the seed (and the authors' are from another
# run): they are compared with the published ones loosely, within this many degrees, and only where
# enough pseudo-samples have a solution for the bounds to mean something. With seeds 1, 2 and 3 the
# 204 directions gave medians of 62.7, 62.3 and 62.9, lower bounds of 59.6, 59.5 and 59.5, upper bounds
# of 68.6, 71.1 and 69.8, and 94, 99 and 82 solutions (2026-11-23), which sets the tolerance.
EI_TOLERANCE, EI_MIN_SOLUTIONS = 2.5, 50
COORDINATES = OrderedDict([(IN_SITU, ("in situ", "dec_insitu", "inc_insitu", "DA-DIR-GEO")),
                           (TILT_CORRECTED, ("tilt-corrected", "dec_tilt", "inc_tilt", "DA-DIR-TILT"))])


def angle(d1, i1, d2, i2):
    """Angle in degrees between two directions (pmag.angle)."""
    return float(pmag.angle([d1, i1], [d2, i2])[0])


def geology(row):
    """Add the lithology columns that MagIC requires at every level."""
    row.update(geologic_classes=pub.GEOLOGIC_CLASSES, geologic_types=pub.GEOLOGIC_TYPES,
               lithologies=pub.LITHOLOGIES)
    return row


def field_site(specimen):
    """The field site of a specimen name, as the paper writes it: zl01-2 -> ZL01."""
    return re.fullmatch(r"(zl\d+)-[\d-]+", specimen).group(1).upper()


# ================================================================ Table S3
#
# One row per specimen: bedding (right-hand strike and dip), the direction of the
# high-temperature component in situ (Dg, Ig) and tilt-corrected (Ds, Is), and its MAD.
# Each printed tilt-corrected direction is recalculated from the in situ direction and the
# bedding (check_tilt), which tests the digits of the table and the reading of the bedding.

def read_table_s3():
    """Table S3 as printed (text), with the numbers also as floats and the field site."""
    table = pd.read_csv(STUDY_DIR / "table_s3.csv", dtype=str)
    for column in ("strike", "dip", "dec_insitu", "inc_insitu", "dec_tilt", "inc_tilt", "mad"):
        table[column + "_printed"] = table[column]
        table[column] = table[column].astype(float)
    table["field_site"] = table["specimen"].map(field_site)
    return table


def check_tilt(table):
    """Recalculate each tilt-corrected direction with pmag.dotilt.

    The dip direction is the strike plus 90 degrees. A specimen that is not
    reproduced with its printed bedding takes the bedding of pub.BEDDING_INFERRED
    if that reproduces it.

    Returns:
        the table with strike_used, dip_used (the bedding entered), tilt_diff
        (angle between the printed and the rotated direction with the bedding
        entered) and tilt_diff_printed (the same with the printed bedding).
    """
    used, diffs, diffs_printed = [], [], []
    for r in table.itertuples():
        def difference(strike, dip):
            dec, inc = pmag.dotilt(r.dec_insitu, r.inc_insitu, (strike + 90) % 360, dip)
            return angle(dec, inc, r.dec_tilt, r.inc_tilt)
        printed = difference(r.strike, r.dip)
        strike, dip = pub.BEDDING_INFERRED.get(r.specimen, (r.strike, r.dip)) \
            if printed > pub.TILT_TOLERANCE else (r.strike, r.dip)
        used.append((strike, dip))
        diffs.append(difference(strike, dip))
        diffs_printed.append(printed)
    table["strike_used"], table["dip_used"] = zip(*used)
    table["tilt_diff"], table["tilt_diff_printed"] = diffs, diffs_printed
    return table


# ================================================================ checks against the paper

def fisher(table, coordinates):
    """Fisher mean (pmag.fisher_mean) of the directions of a table in one coordinate system."""
    _, dec, inc, _ = COORDINATES[coordinates]
    return pmag.fisher_mean(table[[dec, inc]].values.tolist())


def mean_check(label, mean, published):
    return dict(result=label, N_pub=published["n"], N=mean["n"], dec_pub=published["dec"], dec=mean["dec"],
                inc_pub=published["inc"], inc=mean["inc"], k_pub=published["k"], k=mean["k"],
                a95_pub=published["a95"], a95=mean["alpha95"],
                angle=angle(mean["dec"], mean["inc"], published["dec"], published["inc"]),
                reproduced="yes" if (angle(mean["dec"], mean["inc"], published["dec"], published["inc"]) <= 0.1
                                     and abs(mean["k"] - published["k"]) <= 0.06
                                     and abs(mean["alpha95"] - published["a95"]) <= 0.06) else "no")


def north_pole(dec, inc, a95):
    """Pole of a direction at the section (pmag.dia_vgp), as the pole in the northern hemisphere.

    Returns:
        (lat, lon, dp, dm)
    """
    lon, lat, dp, dm = pmag.dia_vgp(dec, inc, a95, pub.LAT, pub.LON)
    if lat < 0:
        lat, lon = -lat, (lon + 180) % 360
    return float(lat), float(lon), float(dp), float(dm)


def unfolding(table):
    """Precision parameter of the mean as the beds are untilted in steps of 1 percent of the dip."""
    rows = []
    for percent in range(0, 101):
        directions = [list(pmag.dotilt(r.dec_insitu, r.inc_insitu, (r.strike_used + 90) % 360,
                                       r.dip_used * percent / 100.))
                      for r in table.itertuples()]
        rows.append((percent, pmag.fisher_mean(directions)["k"]))
    return pd.DataFrame(rows, columns=["percent", "k"])


def vgp_cutoff(table):
    """The specimens whose tilt-corrected VGP is more than the cutoff angle from the mean VGP."""
    vgps = [pmag.dia_vgp(r.dec_tilt, r.inc_tilt, 0, pub.LAT, pub.LON)[:2] for r in table.itertuples()]
    mean = pmag.fisher_mean([list(v) for v in vgps])
    away = np.array([angle(lon, lat, mean["dec"], mean["inc"]) for lon, lat in vgps])
    return mean, away > pub.CUTOFF["angle"]


def elongation_inclination(table):
    """Elongation/inclination analysis (Tauxe and Kent, 2004) of tilt-corrected directions with ipmag.find_ei.

    Returns:
        dict with n; inclination and elongation of the directions and the
        elongation that the TK03 model expects at that inclination (pmag.EI);
        f and inc, the flattening factor and corrected inclination of the data
        set (0 where ipmag.find_ei finds none: its "pathological distribution");
        solutions, the number of bootstrap pseudo-samples with a solution; and
        inc_low, inc_median, inc_high from their corrected inclinations.
    """
    directions = table[["dec_tilt", "inc_tilt"]].values.tolist()
    principal = pmag.doprinc(directions)
    with contextlib.redirect_stdout(io.StringIO()):   # find_ei prints its progress and results
        f, inclinations, _, _ = ipmag.find_ei(directions, nb=EI_BOOTSTRAPS, return_values=True,
                                              random_seed=EI_SEED)
        solution = pmag.find_f(directions)
    plt.close("all")                                  # and draws four figures
    low, median, high = np.quantile(inclinations, [0.025, 0.5, 0.975]) if len(inclinations) else (np.nan,) * 3
    return dict(n=len(directions), inclination=float(abs(principal["inc"])),
                elongation=float(np.real(principal["tau2"] / principal["tau3"])),
                expected=float(pmag.EI(abs(principal["inc"]))), f=float(f), inc=float(solution[1][-1]),
                solutions=len(inclinations), inc_low=float(low), inc_median=float(median), inc_high=float(high))


# ================================================================ the figure

def plot_directions(table, means, path):
    """Equal-area plots of the specimen directions and their Fisher means, in situ and tilt-corrected."""
    plt.figure(num=1, figsize=(9, 4.8))
    for k, (coordinates, (label, dec, inc, _)) in enumerate(COORDINATES.items(), start=1):
        plt.subplot(1, 2, k)
        ipmag.plot_net()  # on the current axes; with a figure number it would clear the figure
        ipmag.plot_di(dec=table[dec].tolist(), inc=table[inc].tolist(), color="0.35", markersize=14)
        mean = means[coordinates]
        ipmag.plot_di_mean(mean["dec"], mean["inc"], mean["alpha95"], color="r", marker="*", markersize=120)
        plt.title(f"{pub.COMPONENT}, {label} (n = {mean['n']})\n"
                  f"{mean['dec']:.1f}/{mean['inc']:.1f}, k {mean['k']:.1f}, α95 {mean['alpha95']:.1f}", fontsize=10)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(1)


# ================================================================ the build

def main():
    BUILD_DIR.mkdir(exist_ok=True)
    table = check_tilt(read_table_s3())
    inferred = table[table["specimen"].isin(pub.BEDDING_INFERRED) & (table["tilt_diff_printed"] > pub.TILT_TOLERANCE)]
    not_reproduced = table[table["tilt_diff"] > pub.TILT_TOLERANCE]

    # ---- checks against the paper
    means = {coordinates: fisher(table, coordinates) for coordinates in COORDINATES}
    checks = pd.DataFrame([
        mean_check("HTC, in situ (Fig. 6c)", means[IN_SITU], pub.HTC_IN_SITU),
        mean_check("HTC, tilt-corrected (Fig. 6d)", means[TILT_CORRECTED], pub.HTC_TILT_CORRECTED)])
    tc = means[TILT_CORRECTED]
    pole_recalculated = north_pole(tc["dec"], tc["inc"], tc["alpha95"])
    pole_of_published = north_pole(pub.HTC_TILT_CORRECTED["dec"], pub.HTC_TILT_CORRECTED["inc"],
                                   pub.HTC_TILT_CORRECTED["a95"])
    pole_diff = angle(pole_recalculated[1], pole_recalculated[0], pub.POLE["lon"], pub.POLE["lat"])
    a95_from_dp_dm = float(np.sqrt(pole_of_published[2] * pole_of_published[3]))
    vgp_mean, outside = vgp_cutoff(table)
    vgp_mean_north = (abs(vgp_mean["inc"]), (vgp_mean["dec"] + 180) % 360 if vgp_mean["inc"] < 0 else vgp_mean["dec"])
    vgp_mean_diff = angle(vgp_mean_north[1], vgp_mean_north[0], pub.POLE["lon"], pub.POLE["lat"])
    paleolatitude = float(pmag.plat(tc["inc"]))
    cutoff_mean = fisher(table[~outside], TILT_CORRECTED)
    cutoff_check = mean_check(f"HTC, tilt-corrected, {pub.CUTOFF['angle']:.0f}° cutoff (Fig. 7d)", cutoff_mean,
                              pub.CUTOFF)
    checks = pd.concat([checks, pd.DataFrame([cutoff_check])], ignore_index=True)
    ei_rows = []
    for label, published, subset in (("all", pub.EI_ALL, table),
                                     (f"within the {pub.CUTOFF['angle']:.0f}° cutoff", pub.EI_CUTOFF,
                                      table[~outside])):
        row = dict(directions=label, published=f"{published['inc']} ({published['low']} to {published['high']})",
                   **elongation_inclination(subset))
        if row["solutions"] < EI_MIN_SOLUTIONS:
            row["comparable"] = "too few solutions"
        else:
            close = all(abs(row[ours] - published[theirs]) <= EI_TOLERANCE for ours, theirs in
                        (("inc_median", "inc"), ("inc_low", "low"), ("inc_high", "high")))
            row["comparable"] = f"within {EI_TOLERANCE:g}°" if close else f"not within {EI_TOLERANCE:g}°"
        ei_rows.append(row)
    ei_checks = pd.DataFrame(ei_rows)
    ei = ei_checks.iloc[0]
    ei_note = (
        f"Recalculated with the function ipmag.find_ei of PmagPy ({EI_BOOTSTRAPS} bootstrap samples), the "
        f"corrected inclination of the {int(ei['n'])} directions is about {ei['inc_median']:.0f}° "
        f"({ei['inc_low']:.0f} to {ei['inc_high']:.0f}°), the median and 95 percent bounds of the bootstrap "
        "samples that have a solution, "
        + ("in agreement with the published values; " if ei["comparable"].startswith("within")
           else "which differs from the published values; ")
        + "the numbers vary with the random bootstrap.")
    k_ratio = means[TILT_CORRECTED]["k"] / means[IN_SITU]["k"]
    unfold = unfolding(table)
    k_max = unfold.loc[unfold["k"].idxmax()]
    plot_directions(table, means, STUDY_DIR / "directions.png")

    # ---- descriptions shared by the rows
    age_basis = (
        f"Age ca. {pub.AGE:.0f} Ma, the age the authors use. Older bound {pub.AGE_OLDER} Ma: the oldest of the "
        "youngest zircon dates (126.7 to 125.8 Ma, LA-ICP-MS U-Pb) of a sandstone and an andesite from the upper "
        "part of the section, which the authors interpret as the maximum depositional age of the formation; the "
        "sampled limestones are in the lower part of the section. "
        f"Younger bound {pub.AGE_YOUNGER} Ma: the top of the Lower Cretaceous ({pub.CHART}); the paper assigns "
        "the formation to the Lower Cretaceous, below the Upper Cretaceous Zongzhuo Formation, and gives no "
        "younger numerical bound.")
    position = (f"Position: that of the section ({pub.LAT}°N, {pub.LON}°E); the paper gives no coordinates for "
                "its sites.")
    as_site = ("The authors average the directions of the specimens, so each specimen is entered as its own site, "
               "with the same name as sample and as specimen.")
    age_columns = dict(age=pub.AGE, age_low=pub.AGE_YOUNGER, age_high=pub.AGE_OLDER, age_unit="Ma")

    # ---- specimens, samples and sites: one of each for every row of Table S3
    specimens, samples, sites = [], [], []
    outside_names = set(table.loc[outside, "specimen"])
    for r in table.itertuples():
        name = r.specimen
        bedding_note = ""
        if (r.strike_used, r.dip_used) != (r.strike, r.dip):
            bedding_note = (
                f" Bedding inferred: Table S3 prints strike {r.strike_printed}, dip {r.dip_printed}, the bedding "
                f"of site ZL01, with which the in situ direction rotates to {r.tilt_diff_printed:.1f}° from the "
                f"printed tilt-corrected direction; strike {r.strike_used:.0f}, dip {r.dip_used:.0f}, the bedding "
                f"of the other specimens of {r.field_site}, gives it within {r.tilt_diff:.2f}° and is entered.")
        cutoff_note = ""
        if name in outside_names:
            cutoff_note = (f" Its tilt-corrected VGP is more than {pub.CUTOFF['angle']:.0f}° from the mean VGP: "
                           f"one of the {int(outside.sum())} specimens left out of the authors' second "
                           "elongation/inclination analysis (inferred by recalculating their mean of 197). It is "
                           "part of the published mean and pole.")
        bedding = dict(bed_dip_direction=f"{(r.strike_used + 90) % 360:.0f}", bed_dip=f"{r.dip_used:.0f}")
        for coordinates, (label, dec, inc, code) in COORDINATES.items():
            dec_printed, inc_printed = getattr(r, dec + "_printed"), getattr(r, inc + "_printed")
            specimens.append(geology(OrderedDict(
                specimen=name, sample=name, dir_comp=pub.COMPONENT, dir_tilt_correction=coordinates,
                dir_dec=dec_printed, dir_inc=inc_printed, dir_mad_free=r.mad_printed,
                method_codes=f"LP-DIR-T:DE-BFL:{code}", result_quality="g", citations="This study",
                software_packages=pub.SOFTWARE,
                description=(f"High-temperature component, {label}, of Table S3 of the supplement: a line fitted "
                             "to thermal demagnetization steps between about 350 and 525 °C. The steps of each "
                             "fit, and whether the line was anchored to the origin, are not published."
                             + (bedding_note if coordinates == TILT_CORRECTED else "") + cutoff_note))))
            sites.append(geology(OrderedDict(
                site=name, location=pub.LOCATION, formation=pub.FORMATION, result_type="i", result_quality="g",
                citations="This study", lat=pub.LAT, lon=pub.LON, geographic_precision=pub.COORDINATE_PRECISION,
                **age_columns, **bedding, dir_comp_name=pub.COMPONENT, dir_tilt_correction=coordinates,
                dir_dec=dec_printed, dir_inc=inc_printed, dir_n_samples=1, dir_n_specimens=1,
                dir_n_specimens_lines=1, dir_polarity="r", method_codes=f"LP-DIR-T:DE-BFL:{code}",
                samples=name, specimens=name, software_packages=pub.SOFTWARE,
                description=(f"Specimen {name} of field site {r.field_site}, one of {pub.N_FIELD_SITES} sites in "
                             f"limestone beds of the lower part of the section. {as_site} High-temperature "
                             f"component, {label} (Table S3 of the supplement). {position}"
                             + bedding_note + cutoff_note))))
        samples.append(geology(OrderedDict(
            sample=name, site=name, lat=pub.LAT, lon=pub.LON, **bedding, method_codes=pub.SAMPLING_CODES,
            citations="This study",
            description=(f"Specimen {name} of field site {r.field_site}, entered as its own sample and site. "
                         f"The paper reports {pub.N_CORES} cores, drilled with a portable drill and oriented with "
                         f"magnetic and sun compasses, cut into {pub.N_SPECIMENS_CUT} specimens; the core "
                         "orientations are not published. Bedding (right-hand strike and dip in Table S3) entered "
                         "as dip direction and dip." + bedding_note))))
    specimens, samples, sites = pd.DataFrame(specimens), pd.DataFrame(samples), pd.DataFrame(sites)

    # ---- locations: the section, and the published results as rows with the same location name
    site_names = ":".join(table["specimen"])
    location_columns = OrderedDict(
        location=pub.LOCATION, location_type="Stratigraphic Section", result_type="a", citations="This study",
        geologic_classes=pub.GEOLOGIC_CLASSES, lithologies=pub.LITHOLOGIES, formations=pub.FORMATION,
        lat_s=pub.LAT, lat_n=pub.LAT, lon_w=pub.LON, lon_e=pub.LON, continent_ocean="Asia", country="China",
        region="Southern Tibet", terranes="Tethyan Himalaya", plate_blocks="Indian Plate")
    section = (f"Lower Cretaceous Jiabula Formation at the Zhangda section ({pub.LAT}°N, {pub.LON}°E), Nagarze, "
               "northern subzone of the Tethyan Himalaya, southern Tibet. The formation is about 200 m thick "
               "here; the paleomagnetic samples are from grey, medium-bedded limestone of its lower part: "
               f"{pub.N_CORES} cores at {pub.N_FIELD_SITES} sites (ZL01 to ZL27), whose beds dip 45 to 87° to the "
               "northwest.")
    htc = pub.HTC_TILT_CORRECTED
    fold_tests = (
        f"Fold tests positive: McElhinny (1964), ks/kg = {pub.MCELHINNY_RATIO} against 1.26 at the 1 percent "
        f"point; McFadden (1990), ξ2 {pub.MCFADDEN_XI2['in_situ']} in situ and "
        f"{pub.MCFADDEN_XI2['tilt_corrected']} tilt-corrected against a critical value of "
        f"{pub.MCFADDEN_XI2['critical_99']} at 99 percent; Watson and Enkin (1993), maximum k "
        f"{pub.UNFOLDING['k_max']} at {pub.UNFOLDING['percent']} percent unfolding.")
    rows = [
        OrderedDict(
            **location_columns, sites=site_names, method_codes=f"{pub.SAMPLING_CODES}:LP-DIR-T:DE-BFL",
            **age_columns,
            description=(f"{section} Table S3 of the supplement gives the high-temperature component of "
                         f"{len(table)} specimens, without site means. {as_site} The published results are the "
                         "rows with a result name: the high-temperature component tilt-corrected (with the pole) "
                         f"and in situ, and the low-temperature component in situ. {age_basis}")),
        OrderedDict(
            **location_columns, result_name="High-temperature component, tilt-corrected", sites=site_names,
            method_codes=f"{pub.SAMPLING_CODES}:LP-DIR-T:DE-BFL:DE-FM:DA-DIR-TILT",
            external_database_ids=f"GPMDB[{pub.GPMDB_RESULT}]", **age_columns,
            dir_tilt_correction=TILT_CORRECTED, dir_dec=htc["dec"],
            dir_inc=htc["inc"], dir_k=htc["k"], dir_alpha95=htc["a95"], dir_n_sites=htc["n"],
            dir_n_samples=htc["n"], dir_n_specimens=htc["n"], dir_polarity="r",
            pole_comp_name=pub.COMPONENT, pole_lat=pub.POLE["lat"], pole_lon=pub.POLE["lon"],
            pole_alpha95=pub.POLE["a95"], pole_n_sites=htc["n"], pole_reversed_perc=100, fold_test=pub.FOLD_TEST,
            paleolat=pub.PALEOLATITUDE, paleolat_sigma=pub.PALEOLATITUDE_SIGMA,
            description=(
                "Published mean of the high-temperature component after tilt correction, and the pole of the "
                f"study. The mean is the Fisher mean of the {htc['n']} specimen directions of Table S3, which "
                f"gives {tc['dec']:.1f}/{tc['inc']:.1f}, k {tc['k']:.1f}, α95 {tc['alpha95']:.1f}. The published "
                f"pole ({pub.POLE['lat']}°N, {pub.POLE['lon']}°E, A95 {pub.POLE['a95']}°) is the pole of that "
                f"mean direction at the section: the published mean gives {pole_of_published[0]:.1f}°N, "
                f"{pole_of_published[1]:.1f}°E with dp {pole_of_published[2]:.1f}° and dm "
                f"{pole_of_published[3]:.1f}°, and √(dp·dm) = {a95_from_dp_dm:.1f}° is the printed A95. The Fisher "
                f"mean of the {htc['n']} specimen VGPs is {vgp_mean_north[0]:.1f}°N, {vgp_mean_north[1]:.1f}°E "
                f"(A95 {vgp_mean['alpha95']:.1f}°), {vgp_mean_diff:.1f}° from the published pole. All directions "
                "are of reversed polarity; the authors conclude that the magnetization was acquired in the "
                f"reverse polarity chron of M3. {fold_tests} Inclination shallowing: an elongation/inclination "
                f"analysis gives a corrected inclination of {pub.EI_ALL['inc']}° ({pub.EI_ALL['low']} to "
                f"{pub.EI_ALL['high']}°) for all directions, and {pub.EI_CUTOFF['inc']}° ({pub.EI_CUTOFF['low']} "
                f"to {pub.EI_CUTOFF['high']}°) for the {pub.CUTOFF['n']} left by a {pub.CUTOFF['angle']:.0f}° "
                "cutoff; the authors conclude that no significant shallowing occurred and use the uncorrected "
                f"mean. {ei_note} Paleolatitude {abs(pub.PALEOLATITUDE)} ± {pub.PALEOLATITUDE_SIGMA}°S.")),
        OrderedDict(
            **location_columns, result_name="High-temperature component, in situ", sites=site_names,
            method_codes=f"{pub.SAMPLING_CODES}:LP-DIR-T:DE-BFL:DE-FM:DA-DIR-GEO", **age_columns,
            dir_tilt_correction=IN_SITU, dir_dec=pub.HTC_IN_SITU["dec"],
            dir_inc=pub.HTC_IN_SITU["inc"], dir_k=pub.HTC_IN_SITU["k"], dir_alpha95=pub.HTC_IN_SITU["a95"],
            dir_n_sites=pub.HTC_IN_SITU["n"], dir_n_samples=pub.HTC_IN_SITU["n"],
            dir_n_specimens=pub.HTC_IN_SITU["n"], dir_polarity="r", fold_test=pub.FOLD_TEST,
            description=("Published mean of the high-temperature component before tilt correction. The "
                         "magnetization predates the folding, so no pole is entered in these coordinates. "
                         + fold_tests)),
        OrderedDict(
            **location_columns, result_name="Low-temperature component, in situ",
            method_codes=f"{pub.SAMPLING_CODES}:LP-DIR-T:DE-BFL:DE-FM:DA-DIR-GEO",
            age=0, age_low=0, age_high=pub.AGE_OLDER, age_unit="Ma",
            dir_tilt_correction=IN_SITU, dir_dec=pub.LTC_IN_SITU["dec"],
            dir_inc=pub.LTC_IN_SITU["inc"], dir_k=pub.LTC_IN_SITU["k"], dir_alpha95=pub.LTC_IN_SITU["a95"],
            dir_n_specimens=pub.LTC_IN_SITU["n"], dir_polarity="n",
            description=(
                f"Published mean of the low-temperature component of {pub.LTC_IN_SITU['n']} specimens, isolated "
                "between 20 and 350 °C, before tilt correction. The specimen directions are not published, so "
                f"no sites are listed. After tilt correction the mean is {pub.LTC_TILT_CORRECTED['dec']}/"
                f"{pub.LTC_TILT_CORRECTED['inc']} with k {pub.LTC_TILT_CORRECTED['k']} (α95 "
                f"{pub.LTC_TILT_CORRECTED['a95']}°); the authors interpret the component as a post-folding "
                "overprint of the present geomagnetic field, so the age is entered as 0 Ma, with the age of the "
                "rocks as the older bound.")),
    ]
    locations = pd.DataFrame(rows)
    locations["age_low"] = locations["age_low"].map("{:g}".format)   # 0 and 100.5, not 0.0

    ages = pd.DataFrame([OrderedDict(
        location=pub.LOCATION, **age_columns, method_codes="GM-UPB:GM-CC-STRAT", citations="This study",
        description=(age_basis + " The sandstone (WMD01) gave 82 detrital zircon dates, the two youngest 126.2 "
                     "and 126.7 Ma; the andesite (SX162-165) gave 10 concordant dates, the youngest 125.8 Ma."))])

    # ---- assemble, write, validate
    for frame in (locations, sites, ages):
        whole_numbers(frame)
    tables = OrderedDict(locations=locations, sites=sites, samples=samples, specimens=specimens, ages=ages)
    write_upload_file(tables, BUILD_DIR, STUDY_DIR / "magic_contribution.txt")
    problems = validate_upload_file(STUDY_DIR / "magic_contribution.txt")

    # ================================================================ report
    n_tilt = int((table["tilt_diff"] <= pub.TILT_TOLERANCE).sum())
    rep = ["# Jiabula Formation, Zhangda section: build report\n",
           "Written by `convert.py`; do not edit. Study: Yuan et al. (2025), "
           f"doi:{pub.PAPER_DOI}; data doi:{pub.DATA_DOI}. `README.md` explains the sources and the decisions.\n",
           "## Contents of the contribution\n",
           "| Table | Rows | Source |", "| --- | --- | --- |",
           f"| specimens | {len(specimens)}: the high-temperature component of {len(table)} specimens, in situ and "
           "tilt-corrected | table (Table S3) |",
           f"| samples | {len(samples)}: one for each specimen | table (bedding); text (sampling, orientation) |",
           f"| sites | {len(sites)}: one for each specimen, in situ and tilt-corrected | table (directions, "
           "bedding); text (position, age, lithology) |",
           f"| locations | {len(locations)}: the section, and three published mean directions, one with the pole "
           "| text |",
           f"| ages | {len(ages)} | text |\n",
           "## Validation with the rules of MagIC (`pmagpy.magic_validation`)\n",
           "No problems.\n" if not problems else "\n".join(f"- {p}" for p in problems) + "\n",
           "## Uploading to MagIC\n",
           "`magic_contribution.txt` holds every table except the contribution table, which is made on MagIC "
           "when the file is uploaded (the file is written with `ipmag.upload_magic`). Enter there:\n",
           "\n".join([f"- Reference: {pub.PAPER_DOI}",
                      f"- Laboratory: {pub.LABORATORIES}",
                      f"- Description: {pub.CONTRIBUTION_DESCRIPTION}"]) + "\n",
           "`<permalink>` is the link to this study folder at the commit the upload is made from, so that it "
           "keeps pointing to the files that made the contribution. After committing and pushing, "
           f"`python common/studies.py --permalink {STUDY_DIR.name}` prints it; enter that commit as "
           "`upload_commit` in `study.json`.\n",
           "## Table S3\n",
           f"`table_s3.csv` has {len(table)} rows, from {table['field_site'].nunique()} field sites "
           f"({table['field_site'].min()} to {table['field_site'].max()}). Each printed tilt-corrected direction "
           "was recalculated from the printed in situ direction and bedding (dip direction = strike + 90°) with "
           f"`pmag.dotilt`. {int((table['tilt_diff_printed'] <= pub.TILT_TOLERANCE).sum())} of {len(table)} are "
           f"reproduced within {pub.TILT_TOLERANCE}° with the printed bedding (largest difference "
           f"{table.loc[table['tilt_diff_printed'] <= pub.TILT_TOLERANCE, 'tilt_diff_printed'].max():.2f}°); with "
           f"the bedding entered, {n_tilt} of {len(table)}.\n"]
    for r in inferred.itertuples():
        rep.append(f"- {r.specimen}: printed with strike {r.strike_printed}, dip {r.dip_printed}, which gives a "
                   f"direction {r.tilt_diff_printed:.2f}° from the printed one. Strike {r.strike_used:.0f}, dip "
                   f"{r.dip_used:.0f}, the bedding of the other specimens of {r.field_site}, gives it within "
                   f"{r.tilt_diff:.2f}° and is entered as inferred.")
    for r in not_reproduced.itertuples():
        rep.append(f"- {r.specimen}: not reproduced ({r.tilt_diff:.2f}°).")
    beddings = table.groupby("field_site").apply(
        lambda g: len(set(zip(g["strike_used"], g["dip_used"]))), include_groups=False)
    rep.append(f"\nWith the bedding entered, each field site has one bedding "
               f"({'true for all ' + str(len(beddings)) if (beddings == 1).all() else 'not true for ' + ', '.join(beddings[beddings > 1].index)}).\n")
    rep.append("## Mean directions\n")
    rep.append("Fisher means of the directions of Table S3 (`pmag.fisher_mean`) against the published means.\n")
    rep.append(md_table(checks, ["result", "N_pub", "N", "dec_pub", "dec", "inc_pub", "inc", "k_pub", "k",
                                 "a95_pub", "a95", "angle", "reproduced"],
                        {"dec": ".2f", "inc": ".2f", "k": ".2f", "a95": ".2f", "angle": ".2f"}))
    rep.append(f"\nThe {pub.CUTOFF['angle']:.0f}° cutoff of the authors' second elongation/inclination analysis "
               "is reproduced as a cutoff on the tilt-corrected VGPs about their Fisher mean. It leaves out "
               f"{int(outside.sum())} specimens: {', '.join(sorted(outside_names))}.\n")
    rep.append("![Specimen directions](directions.png)\n")
    rep.append("## Pole\n")
    rep.append(md_table(pd.DataFrame([
        dict(calculation="published", lat=pub.POLE["lat"], lon=pub.POLE["lon"], A95=pub.POLE["a95"], dp=np.nan,
             dm=np.nan, from_published=0.0),
        dict(calculation="pole of the published mean direction", lat=pole_of_published[0],
             lon=pole_of_published[1], A95=a95_from_dp_dm, dp=pole_of_published[2], dm=pole_of_published[3],
             from_published=angle(pole_of_published[1], pole_of_published[0], pub.POLE["lon"], pub.POLE["lat"])),
        dict(calculation="pole of the mean direction of Table S3", lat=pole_recalculated[0],
             lon=pole_recalculated[1], A95=float(np.sqrt(pole_recalculated[2] * pole_recalculated[3])),
             dp=pole_recalculated[2], dm=pole_recalculated[3], from_published=pole_diff),
        dict(calculation="Fisher mean of the specimen VGPs", lat=vgp_mean_north[0], lon=vgp_mean_north[1],
             A95=vgp_mean["alpha95"], dp=np.nan, dm=np.nan, from_published=vgp_mean_diff)]),
        ["calculation", "lat", "lon", "A95", "dp", "dm", "from_published"],
        {"lat": ".2f", "lon": ".2f", "A95": ".2f", "dp": ".2f", "dm": ".2f", "from_published": ".2f"}))
    rep.append("\nIn the A95 column, the two poles of a mean direction have √(dp·dm). The published pole is "
               "the pole of the mean direction (`pmag.dia_vgp`), given as the pole in the northern hemisphere, "
               f"and its A95 is √(dp·dm). Paleolatitude from the mean inclination of Table S3 (`pmag.plat`): "
               f"{paleolatitude:.1f}° (published {abs(pub.PALEOLATITUDE)}°S).\n")
    rep.append("## Fold tests\n")
    rep.append(f"- McElhinny (1964): k tilt-corrected / k in situ from Table S3 is {k_ratio:.2f} (published "
               f"{pub.MCELHINNY_RATIO}).")
    rep.append(f"- Progressive unfolding: untilting the directions of Table S3 in steps of 1 percent of the dip, "
               f"k rises from {unfold['k'].iloc[0]:.1f} to a maximum of {k_max['k']:.1f} at "
               f"{int(k_max['percent'])} percent (published: maximum {pub.UNFOLDING['k_max']} at "
               f"{pub.UNFOLDING['percent']} percent).")
    rep.append("- The McFadden (1990) statistics are entered as published and are not recalculated.\n")
    rep.append("## Elongation/inclination\n")
    rep.append(f"`ipmag.find_ei` on the tilt-corrected directions, with {EI_BOOTSTRAPS} bootstrap pseudo-samples "
               f"(seed {EI_SEED}). `elongation` is that of the directions and `expected` the elongation of the "
               "TK03 model at their inclination (`pmag.EI`). The method looks for the flattening factor at which "
               "the unflattened directions reach the model's elongation; `f` and `inc` are 0 where the function "
               "finds none for the data set (its \"pathological distribution\"). `solutions` is the number of "
               "pseudo-samples that have one, and the last three columns are the median and the 95 percent "
               "bounds of their corrected inclinations. `published` is the corrected inclination and its bounds "
               "in the paper. The bootstrap is random, so these inclinations change with the seed, and the "
               "authors' are from another run: with seeds 1, 2 and 3 the median for all directions was 62.7, "
               "62.3 and 62.9°, the lower bound 59.6, 59.5 and 59.5° and the upper bound 68.6, 71.1 and 69.8°. "
               "The comparison is therefore loose: `comparable` says whether the "
               f"median and both bounds are within {EI_TOLERANCE:g}° of the published values, where at least "
               f"{EI_MIN_SOLUTIONS} pseudo-samples have a solution.\n")
    rep.append(md_table(ei_checks, ["directions", "n", "inclination", "elongation", "expected", "f", "inc",
                                    "solutions", "inc_median", "inc_low", "inc_high", "published", "comparable"],
                        {"elongation": ".2f", "expected": ".2f", "f": ".2f"}))
    rep.append("\nThe directions are already more elongate than the model expects at their inclination, so the "
               "function finds no flattening factor for either set. The published values are entered in the "
               "description of the pole as printed, with this recalculation beside them.\n")
    rep.append("## Information that would complete the contribution\n")
    rep.append("\n".join([
        "- The demagnetization measurements, and the steps and line type of each fit.",
        "- The directions of the low-temperature component (268 specimens).",
        "- The core orientations.",
        "- The coordinates of the 27 sites.",
        "- Confirmation of the bedding of specimen zl02-1."]) + "\n")
    (STUDY_DIR / "report.md").write_text("\n".join(rep) + "\n")

    reproduced = int((checks["reproduced"] == "yes").sum())
    write_build_summary(STUDY_DIR, tables, len(problems), [
        f"{n_tilt} of {len(table)} tilt-corrected specimen directions",
        f"{reproduced} of {len(checks)} mean directions",
        "the pole" if pole_diff <= 0.15 else f"the pole within {pole_diff:.1f}°"])
    print(f"{len(problems)} validation problems")
    for p in problems[:40]:
        print("  ", p)
    print("wrote", STUDY_DIR / "magic_contribution.txt")
    print({name: len(frame) for name, frame in tables.items()})


if __name__ == "__main__":
    main()
