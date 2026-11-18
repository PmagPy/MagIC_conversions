"""Build the MagIC contribution for the Praia Grande lava sequence (Calvo Rathert et al., 2022).

Inputs: the four archives of the Zenodo record (data/), unmodified, and the
values transcribed from the paper (published.py). report.md gives the source of
each part of the contribution:

    files      the archived laboratory files, read with PmagPy converters
    table      Tables 1 to 3 of the paper and Tables S1, S3 and S4 of its supporting information
    text       age, lithology, laboratory, methods
    figure     the position of the section, read off Figure 1b
    inferred   from recalculation, where neither the files nor the paper give it
               (e.g. which specimens enter a flow mean)

Outputs, next to this script:
    magic_contribution.txt   the contribution
    report.md                contents, checks against the paper, and what is missing
    build/                   extracted archives and converter output (not kept in the repository)

Sections:
    directions (.rs3)        convert_2_magic.rs3; stored fits recalculated; specimens of each flow mean
    Thellier-Coe (.tdt)      the 66 coded files sorted from the 16 copies; convert_2_magic.tdt; Table 2 recalculated
    multispecimen (.jr6)     the five step files read and lined up; Tables 2 and S3 recalculated
    rock magnetism (VFTB)    convert_2_magic.vftb; Table S1 entered and recalculated
    the contribution         sites, location, ages and criteria; validation; report.md

Usage:
    python convert.py

Requires numpy, pandas and pmagpy with convert_2_magic.rs3 (see the repository README).
"""

import itertools
import re
import shutil
import sys
import zipfile
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from pmagpy import convert_2_magic
from pmagpy import ipmag
from pmagpy import pmag

import published as pub

STUDY_DIR = Path(__file__).resolve().parent
REPO_DIR = STUDY_DIR.parents[1]
sys.path.insert(0, str(REPO_DIR))
from common.magic_tools import load_resources, md_table, read_magic_table, validate  # noqa: E402

DATA_DIR = STUDY_DIR / "data"
BUILD_DIR = STUDY_DIR / "build"
ARCHIVES = OrderedDict([
    ("directions", "Praia Grande Paleomagnetism Data"),
    ("thellier", "Praia Grande Thellier-Coe Data"),
    ("multispecimen", "Praia Grande Multispecimen Data"),
    ("rockmag", "Praia Grande Rock Magnetism Data")])


def join(names):
    return ":".join(names)


def geology(df):
    """Add the lithology columns that MagIC requires at every level."""
    df["geologic_classes"], df["geologic_types"] = pub.GEOLOGIC_CLASSES, pub.GEOLOGIC_TYPES
    df["lithologies"] = pub.LITHOLOGIES
    return df


def whole_numbers(df):
    """Write columns of whole numbers without a decimal point (6, not 6.0), keeping blanks."""
    for column in df.columns:
        values = df[column]
        if values.dtype.kind == "f" and values.notna().any() and (values.dropna() % 1 == 0).all():
            df[column] = values.astype("Int64")
    return df


# ---------------------------------------------------------------- names and directions

def sample_name(specimen):
    """The core a specimen was cut from: PRG1-2A, PRG10-1, PRG6-3A' -> PRG1-2, PRG10-1, PRG6-3."""
    return re.fullmatch(r"(PRG\d+-\d+)[A-Z]?'?[a-z]?", specimen).group(1)


def flow_name(name):
    """The flow (site) of a specimen or sample name."""
    return name.split("-")[0]


def flow_number(site):
    return int(site[3:])


def angle(d1, i1, d2, i2):
    """Angle in degrees between two directions."""
    a, b = pmag.dir2cart([d1, i1, 1.0]), pmag.dir2cart([d2, i2, 1.0])
    return float(np.degrees(np.arccos(np.clip(np.dot(a, b), -1.0, 1.0))))


def fisher(directions):
    """Fisher mean of a list of (dec, inc): dict with dec, inc, n, k, alpha95."""
    if len(directions) == 1:
        return dict(dec=directions[0][0], inc=directions[0][1], n=1, k=np.nan, alpha95=np.nan)
    return pmag.fisher_mean([[d, i] for d, i in directions])


def site_row(site, result_quality="g", **columns):
    """A sites-table row with the columns every row of this study shares."""
    row = OrderedDict(
        site=site, location=pub.LOCATION, result_type="i", result_quality=result_quality,
        citations="This study", geologic_classes=pub.GEOLOGIC_CLASSES, geologic_types=pub.GEOLOGIC_TYPES,
        lithologies=pub.LITHOLOGIES, lat=pub.LAT, lon=pub.LON, age=pub.AGE, age_sigma=pub.AGE_2SIGMA / 2,
        age_unit="Ma")
    row.update(columns)
    return row


def write_upload_file(tables, path):
    """Write the tables as one MagIC upload file with ipmag.upload_magic.

    The contribution table (reference, laboratories, description) is not part
    of an upload file: it is made on MagIC when the file is uploaded, from the
    values that report.md lists under "Uploading to MagIC".
    """
    upload_dir = BUILD_DIR / "upload"
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    upload_dir.mkdir(parents=True)
    for name, df in tables.items():
        pmag.magic_write(str(upload_dir / f"{name}.txt"), df.dropna(axis=1, how="all"), name, dataframe=True)
    written = ipmag.upload_magic(dir_path=str(upload_dir), input_dir_path=str(upload_dir), validate=False,
                                 verbose=False)[0]
    if not written:
        raise RuntimeError("ipmag.upload_magic did not write an upload file")
    shutil.copyfile(written, path)


def extract_archives():
    """Unzip the four archives into build/extracted and return their folders."""
    folders = {}
    for key, name in ARCHIVES.items():
        target = BUILD_DIR / "extracted"
        with zipfile.ZipFile(DATA_DIR / f"{name}.zip") as archive:
            archive.extractall(target)
        folders[key] = target / name
    return folders


# ================================================================ directions (.rs3)
#
# The Remasoft files hold the measurements and the line fits the authors saved.
# They are converted with convert_2_magic.rs3. The stored fits are recalculated
# from the measurements, and the fits in each published flow mean (Table 1),
# which the files do not record, are identified:
#
#     refit_stored                   each stored fit recalculated between its limits
#     flow_mean_members              the specimens, or samples, whose mean is the published one
#     refit_with_other_line_types    for a flow that the stored fits do not reproduce, the one
#                                    stored line whose type (free or anchored) explains it

REMADE = 0.15  # degrees: a recalculated fit agrees with the stored one within this angle


def cartesian(steps, coordinates):
    """Moment vectors of the steps, in "sp" (specimen) or "ge" (geographic) coordinates."""
    return np.array([pmag.dir2cart([s["D" + coordinates], s["I" + coordinates], s["M"]]) for s in steps])


def fit_line(vectors, line_type):
    """Principal component line fit (Kirschvink, 1980).

    Args:
        vectors: (n, 3) array of moment vectors, in demagnetization order.
        line_type: "free" (line through the center of mass), "anchored" (line
            forced through the origin) or "origin" (free line with the origin
            added as a data point).

    Returns:
        (dec, inc, mad) with the direction pointing from the last step towards the first.
    """
    x = np.asarray(vectors, dtype=float)
    if line_type == "origin":
        x = np.vstack([x, np.zeros(3)])
    centerd = x if line_type == "anchored" else x - x.mean(axis=0)
    eigval, eigvec = np.linalg.eigh(centerd.T @ centerd)
    v = eigvec[:, 2]
    if np.dot(v, x[0] - x[-1]) < 0:
        v = -v
    mad = np.degrees(np.arctan(np.sqrt(max(eigval[0] + eigval[1], 0.0) / eigval[2])))
    dec, inc, _ = pmag.cart2dir(v)
    return float(dec), float(inc), float(mad)


def limit_index(steps, label, last):
    """Index of the step named by a Remasoft limit such as "NRM", "35mT" or "300°C"."""
    if label == "NRM":
        return 0
    m = re.fullmatch(r"([\d.]+)(mT|°C)", label)
    if not m:
        raise ValueError(f"limit {label!r} not understood")
    row_id = "A" if m.group(2) == "mT" else "T"
    hits = [i for i, s in enumerate(steps) if s["ID"] == row_id and float(s["Step"]) == float(m.group(1))]
    if not hits:
        raise ValueError(f"no step {label}")
    return hits[-1] if last else hits[0]


def sample_means(candidates, sample_of):
    """Average the specimens of each sample: list of (sample, dec, inc)."""
    groups = defaultdict(list)
    for label, d, i in candidates:
        groups[sample_of[label]].append((d, i))
    out = []
    for sample, dirs in groups.items():
        mean = fisher(dirs)
        out.append((sample, mean["dec"], mean["inc"]))
    return out


def load_rs3(folder):
    """Read every .rs3 file in a folder with the reader of the PmagPy converter.

    Returns:
        list of dicts: file, name, site, sample, steps (with the moment as a
        float) and fits (with "anchored" True for the flag OA).
    """
    specimens = []
    for path in sorted(folder.glob("*.rs3")):
        head, steps, fits = convert_2_magic._rs3_read_file(str(path))
        for step in steps:
            step["M"] = float(step["M"])
        for fit in fits:
            fit["anchored"] = fit["flag"] == "OA"
        name = head["Name"]
        specimens.append(dict(file=path.name, name=name, site=flow_name(name), sample=sample_name(name),
                              steps=steps, fits=fits))
    return specimens


# ---------------------------------------------------------------- the stored fits

def refit_stored(specimens):
    """Re-make each stored line from the measurements between its stated limits.

    Returns:
        DataFrame, one row per stored line: the stored direction and MAD, and
        the angle (diff_stated) and MAD difference of the fit recalculated with the
        stated line type. Where that is more than REMADE degrees off,
        other_steps names a run of steps ending at the same limit that gives
        the stored fit.
    """
    rows = []
    for sp in specimens:
        for fit in sp["fits"]:
            if fit["ID"] != "C":
                continue
            i0 = limit_index(sp["steps"], fit["Limit1"], last=False)
            i1 = limit_index(sp["steps"], fit["Limit2"], last=True)
            used = sp["steps"][i0:i1 + 1]
            stated = "anchored" if fit["anchored"] else "free"
            d, i, mad = fit_line(cartesian(used, "ge"), stated)
            row = dict(specimen=sp["name"], site=sp["site"], sample=sp["sample"], component=fit["name"],
                       anchored=fit["anchored"], first=fit["Limit1"], last=fit["Limit2"], n_steps=len(used),
                       dec_geo=fit["Dge"], inc_geo=fit["Ige"], mad=fit["Prec"],
                       diff_stated=angle(d, i, fit["Dge"], fit["Ige"]), mad_diff_stated=mad - fit["Prec"],
                       other_steps="", other_n=np.nan)
            if row["diff_stated"] > REMADE:
                for start in range(0, i1):
                    d, i, mad = fit_line(cartesian(sp["steps"][start:i1 + 1], "ge"), stated)
                    if angle(d, i, fit["Dge"], fit["Ige"]) <= 0.1 and abs(mad - fit["Prec"]) <= 0.06:
                        first = sp["steps"][start]
                        row["other_steps"] = f"{first['ID']} {first['Step']} to {fit['Limit2']}"
                        row["other_n"] = i1 + 1 - start
                        break
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- the published flow means

def matches(mean, target, tol_angle=0.15, tol_a95=0.06, tol_k=0.006):
    """True if a recalculated mean agrees with the published one to its printed precision."""
    return (angle(mean["dec"], mean["inc"], target["dec"], target["inc"]) <= tol_angle
            and abs(mean["alpha95"] - target["a95"]) <= tol_a95
            and abs(mean["k"] - target["k"]) <= max(0.5, tol_k * target["k"]))


def search_subsets(candidates, target):
    """All subsets of N directions whose Fisher mean matches the published flow mean.

    Args:
        candidates: list of (label, dec, inc).
        target: published row with N, dec, inc, a95 and k.

    Returns:
        list of tuples of labels.
    """
    found = []
    for subset in itertools.combinations(candidates, int(target["N"])):
        mean = fisher([(d, i) for _, d, i in subset])
        if matches(mean, target):
            found.append(tuple(label for label, _, _ in subset))
    return found


def flow_mean_members(chrm_geo, table1):
    """Find, for each flow, the specimens or samples whose mean is the published one.

    Args:
        chrm_geo: rows with site, specimen, sample, dir_dec, dir_inc for the
            characteristic component in geographic coordinates.
        table1: the published flow means.

    Returns:
        dict by site of dict(level, used, left_out, reproduced): level is
        "specimens" or "samples"; used and left_out are lists of specimen names.
    """
    sample_of = dict(zip(chrm_geo["specimen"], chrm_geo["sample"]))
    out = {}
    for _, target in table1.iterrows():
        rows = chrm_geo[chrm_geo["site"] == target["site"]]
        cands = [(r.specimen, float(r.dir_dec), float(r.dir_inc)) for r in rows.itertuples()]
        result = dict(level="specimens", used=[c[0] for c in cands], left_out=[], reproduced=False)
        # specimens as independent directions first, then specimens averaged by sample
        for level, pool in (("specimens", cands), ("samples", sample_means(cands, sample_of))):
            if len(pool) < target["N"]:
                continue
            found = search_subsets(pool, target)
            if len(found) == 1:
                kept = set(found[0])
                used = [s for s, _, _ in cands if (s if level == "specimens" else sample_of[s]) in kept]
                result = dict(level=level, used=used, reproduced=True,
                              left_out=[s for s, _, _ in cands if s not in used])
                break
        out[target["site"]] = result
    return out


def refit_with_other_line_types(specimens, stored, target):
    """Look for one stored fit whose line type explains a flow mean that is not reproduced.

    Each stored characteristic line of the flow is recalculated over its own steps as a
    free, an anchored and an origin-included line, one specimen at a time, and the
    flow mean is recalculated with it in place of the stored direction.

    Args:
        specimens: the study, from load_rs3.
        stored: rows of refit_stored for the characteristic component.
        target: published row with site, N, dec, inc, a95 and k.

    Returns:
        list of dicts, one per change that gives the published mean, k and alpha95.
    """
    by_name = {sp["name"]: sp for sp in specimens}
    rows = stored[stored["site"] == target["site"]]
    found = []
    if len(rows) != target["N"]:
        return found
    for r in rows.itertuples():
        steps = by_name[r.specimen]["steps"]
        used = steps[limit_index(steps, r.first, False):limit_index(steps, r.last, True) + 1]
        others = [(o.dec_geo, o.inc_geo) for o in rows.itertuples() if o.specimen != r.specimen]
        stored_type = "anchored" if r.anchored else "free"
        for line_type in ("free", "anchored", "origin"):
            if line_type == stored_type:
                continue
            dec, inc, mad = fit_line(cartesian(used, "ge"), line_type)
            if matches(fisher(others + [(dec, inc)]), target):
                dec_sp, inc_sp, _ = fit_line(cartesian(used, "sp"), line_type)
                found.append(dict(specimen=r.specimen, component=r.component, stored_type=stored_type,
                                  line_type=line_type, first=r.first, last=r.last, n_steps=len(used),
                                  dec_geo=dec, inc_geo=inc, dec_spec=dec_sp, inc_spec=inc_sp, mad=mad,
                                  stored_dec=r.dec_geo, stored_inc=r.inc_geo, stored_mad=r.mad))
    return found


def recalculated_mean(chrm_geo, site, level):
    """Fisher mean of a flow from the fits flagged good, at specimen or sample level."""
    rows = chrm_geo[(chrm_geo["site"] == site) & (chrm_geo["result_quality"] == "g")]
    dirs = [(r.specimen, float(r.dir_dec), float(r.dir_inc)) for r in rows.itertuples()]
    if level == "samples":
        dirs = sample_means(dirs, dict(zip(rows["specimen"], rows["sample"])))
    return fisher([(d, i) for _, d, i in dirs])


# ---------------------------------------------------------------- the directions tables

def build_directions(folder, notes):
    """Demagnetization data: measurements, specimens with the stored fits, samples, flow means."""
    converted = BUILD_DIR / "converted_directions"
    converted.mkdir(parents=True, exist_ok=True)
    ok, message = convert_2_magic.rs3(input_dir_path=str(folder), dir_path=str(converted), samp_con="2",
                              location=pub.LOCATION, lat=pub.LAT, lon=pub.LON, meth_code=pub.ORIENTATION_CODES)
    if not ok:
        raise RuntimeError(message)
    meas, spec, samp = (read_magic_table(converted / f"{t}.txt") for t in ("measurements", "specimens", "samples"))
    # Units: the files label the moments A/m; the values are taken as emu/cm3 and converted
    # (README.md, "Units").
    meas["magn_volume"] = (meas["magn_volume"].astype(float) * pub.EMU_PER_CM3_TO_A_PER_M).map("{:.4g}".format)

    # samples: several specimens were cut from some cores
    spec["sample"] = spec["specimen"].map(sample_name)
    samp["specimen"] = samp["sample"]
    samp["sample"] = samp["sample"].map(sample_name)
    for sample, group in samp.groupby("sample"):
        if len(group) > 1 and (group["azimuth"].nunique() > 1 or group["dip"].nunique() > 1):
            notes.append(f"Sample {sample}: its specimens carry different orientations in their file headers ("
                         + "; ".join(f"{r.specimen} {float(r.azimuth):.0f}/{float(r.dip):.0f}"
                                     for r in group.itertuples())
                         + "). The sample row keeps the first; the specimen directions in geographic "
                           "coordinates are those of the files.")
    samp = samp.drop_duplicates("sample").drop(columns="specimen")
    spec["site"] = spec["sample"].map(flow_name)

    # the stored fits, recalculated from the measurements
    study = load_rs3(folder)
    stored = refit_stored(study)
    for r in stored[stored["diff_stated"] > REMADE].itertuples():
        rows = (spec["specimen"] == r.specimen) & (spec["dir_comp"] == r.component)
        spec.loc[rows, "dir_n_measurements"] = int(r.other_n)
        spec.loc[rows, "meas_step_min"] = "0.000e+00"
        spec.loc[rows, "description"] = (
            f"The file gives the limits {r.first} to {r.last}; the stored direction and MAD are those of the "
            f"{int(r.other_n)} steps from {r.other_steps}.")
        if str(r.other_steps).startswith("T"):
            # the range starts at a heating step: both protocols, and the field of that step (0 T) as minimum
            for i in spec.index[rows]:
                codes = spec.at[i, "method_codes"].split(":")
                if "LP-DIR-T" not in codes:
                    codes.insert(codes.index("LP-DIR-AF") if "LP-DIR-AF" in codes else 0, "LP-DIR-T")
                spec.at[i, "method_codes"] = ":".join(codes)
            spec.loc[rows, "description"] += (" The range starts at the heating step, before the alternating-field "
                                              "steps, so meas_step_min is 0 T, the field of that step.")
        notes.append(f"{r.specimen} {r.component}: the stored fit is {r.diff_stated:.2f}° from a fit between "
                     f"its stated limits ({r.first} to {r.last}) and is recalculated with {r.other_steps} "
                     f"({int(r.other_n)} steps). dir_n_measurements and meas_step_min were set accordingly.")

    # specimens without a stored fit (the converter gives them the method of their experiment)
    no_fit = spec["dir_comp"].isna()
    spec.loc[no_fit, "description"] = "Measured; no interpretation stored in the archived file."

    # which fits enter each flow mean (inferred)
    def characteristic(table):
        is_chrm = table["dir_comp"].fillna("").str.startswith(pub.CHRM)
        return is_chrm, table[is_chrm & (table["dir_tilt_correction"].astype(float) == 0)]

    is_chrm, chrm_geo = characteristic(spec)
    members = flow_mean_members(chrm_geo, pub.TABLE1)
    for site, m in members.items():
        rows = spec["specimen"].isin(m["left_out"]) & is_chrm
        spec.loc[rows, "result_quality"] = "b"
        spec.loc[rows, "description"] = ("Not in the published flow mean: inferred by recalculating the mean, "
                                         "not flagged in the archived file.")
    # a flow that the stored fits do not reproduce: one stored line recalculated with another line type
    stored_chrm = stored[stored["component"].str.startswith(pub.CHRM)]
    for _, row in pub.TABLE1.iterrows():
        site = row["site"]
        if members[site]["reproduced"]:
            continue
        refits = refit_with_other_line_types(study, stored_chrm, row)
        if len(refits) != 1:
            continue
        f = refits[0]
        stored_rows = (spec["specimen"] == f["specimen"]) & (spec["dir_comp"] == f["component"])
        new_rows = spec[stored_rows].copy()
        code = {"anchored": "DE-BFL-A", "origin": "DE-BFL-O", "free": "DE-BFL"}[f["line_type"]]
        for i, new in new_rows.iterrows():
            geographic = float(new["dir_tilt_correction"]) == 0
            new_rows.loc[i, "dir_dec"] = f"{f['dec_geo' if geographic else 'dec_spec']:.1f}"
            new_rows.loc[i, "dir_inc"] = f"{f['inc_geo' if geographic else 'inc_spec']:.1f}"
            new_rows.loc[i, "method_codes"] = join([code] + new["method_codes"].split(":")[1:])
        new_rows["dir_mad_free"], new_rows["dir_mad_anc"] = np.nan, np.nan
        new_rows["dir_mad_anc" if f["line_type"] == "anchored" else "dir_mad_free"] = f"{f['mad']:.1f}"
        new_rows["software_packages"] = np.nan
        new_rows["description"] = (
            f"Not stored in the archived file: the stored {f['stored_type']} line recalculated here over the same "
            f"{f['n_steps']} steps as an {f['line_type']} line. With it the published flow mean is reproduced.")
        spec.loc[stored_rows, "result_quality"] = "b"
        spec.loc[stored_rows, "description"] = (
            f"As stored in the archived file ({f['stored_type']} line). The published flow mean is reproduced "
            f"with the {f['line_type']} line over the same steps, entered as a separate row.")
        spec = pd.concat([spec, new_rows], ignore_index=True).sort_values(
            ["specimen", "dir_comp"], kind="stable", na_position="first").reset_index(drop=True)
        members[site]["reproduced"] = True
        members[site]["refit"] = f
        rows = stored_chrm[stored_chrm["site"] == site]
        stored_mean = fisher(list(zip(rows["dec_geo"], rows["inc_geo"])))
        notes.append(f"{site}: the stored fits give {stored_mean['dec']:.1f}/{stored_mean['inc']:.1f} "
                     f"(k {stored_mean['k']:.0f}), {angle(stored_mean['dec'], stored_mean['inc'], row['dec'], row['inc']):.1f}° "
                     f"from the published mean. It is reproduced when the {f['stored_type']} line stored for "
                     f"{f['specimen']} ({f['first']} to {f['last']}, {f['stored_dec']:.1f}/{f['stored_inc']:.1f}, "
                     f"MAD {f['stored_mad']:.1f}°) is recalculated over the same steps as an {f['line_type']} line "
                     f"({f['dec_geo']:.1f}/{f['inc_geo']:.1f}, MAD {f['mad']:.1f}°). The stored row is flagged b "
                     "and the recalculated fit is entered as a new row.")
    is_chrm, chrm_geo = characteristic(spec)

    # sites: the published flow means (Table 1)
    site_rows, checks = [], []
    for _, row in pub.TABLE1.iterrows():
        site, m = row["site"], members[row["site"]]
        used_samples = list(OrderedDict.fromkeys(sample_name(s) for s in m["used"]))
        mean = recalculated_mean(chrm_geo, site, m["level"])
        plon, plat, _, _ = pmag.dia_vgp(row["dec"], row["inc"], row["a95"], pub.LAT, pub.LON)
        vgp_diff = float(pmag.angle([plon, plat], [row["vgp_lon"], row["vgp_lat"]])[0])
        checks.append(dict(site=site, level=m["level"], N_pub=row["N"], N=mean["n"],
                           dec=mean["dec"], inc=mean["inc"], k=mean["k"], a95=mean["alpha95"],
                           dec_pub=row["dec"], inc_pub=row["inc"], k_pub=row["k"], a95_pub=row["a95"],
                           angle=angle(mean["dec"], mean["inc"], row["dec"], row["inc"]),
                           reproduced="yes" if m["reproduced"] else "no",
                           left_out=", ".join(m["left_out"]), vgp_diff=vgp_diff))
        description = f"Flow {flow_number(site)} of 11, numbered from the base of the sequence. "
        if m["reproduced"]:
            description += ("Published mean direction (Table 1), reproduced from the listed "
                            + ("samples (specimens of one core averaged first)" if m["level"] == "samples"
                               else "specimens") + ".")
            if "refit" in m:
                f = m["refit"]
                description += (f" For {f['specimen']} this needs the {f['line_type']} line over the steps of "
                                f"its stored {f['stored_type']} fit.")
        else:
            description += ("Published mean direction (Table 1). It is not reproduced by the fits stored in "
                            f"the archived files, whose mean is {mean['dec']:.1f}/{mean['inc']:.1f} "
                            f"(k {mean['k']:.0f}, alpha95 {mean['alpha95']:.1f}).")
        if vgp_diff > 0.5:
            description += (f" The published VGP ({row['vgp_lat']}°N, {row['vgp_lon']}°E) is {vgp_diff:.1f}° "
                            f"from the VGP of the published direction at the position used "
                            f"({plat:.1f}°N, {plon:.1f}°E).")
            notes.append(f"{site}: the published VGP ({row['vgp_lat']}°N, {row['vgp_lon']}°E) is "
                         f"{vgp_diff:.2f}° from the VGP calculated from the published direction "
                         f"({plat:.1f}°N, {plon:.1f}°E); for the other flows the two agree within 0.05°. "
                         "The published values are entered as printed.")
        site_rows.append(site_row(
            site, method_codes="LP-DIR-AF:LP-DIR-T:DE-BFL-A:DE-FM:DA-DIR-GEO",
            dir_comp_name=pub.CHRM, dir_tilt_correction=0, dir_dec=row["dec"], dir_inc=row["inc"],
            dir_alpha95=row["a95"], dir_k=row["k"], dir_n_samples=row["N"],
            dir_n_specimens=len(m["used"]), dir_n_specimens_lines=len(m["used"]), dir_polarity="n",
            vgp_lat=row["vgp_lat"], vgp_lon=row["vgp_lon"],
            samples=join(used_samples), specimens=join(m["used"]),
            software_packages="Remasoft", description=description + " " + pub.UNTILTED))
    spec["description"] = [" ".join([d, pub.UNITS_NOTE]) if isinstance(d, str) and d else pub.UNITS_NOTE
                           for d in spec["description"]]
    return dict(meas=meas, spec=spec.drop(columns="site"), samp=samp, site_rows=site_rows,
                checks=pd.DataFrame(checks), stored=stored)


# ================================================================ Thellier-Coe (.tdt)
#
# 82 ThellierTool files (laboratory field 40 μT): the 66 specimens of the paper,
# written with ThellierTool step codes (T.00 zero field, T.11 in field, T.12
# pTRM check), and 16 files with the steps as labeled at measurement (125C,
# 126C, ...), earlier copies of 16 of the 66 (survey_tdt). The 66 are converted
# with convert_2_magic.tdt (convert_thellier), each Table 2 determination is
# recalculated (recalculate_thellier), and the published results become
# specimens rows (thellier_specimen_rows).

# ---------------------------------------------------------------- reading

def read_tdt(path):
    """Read one .tdt file, tolerating empty lines at the top and empty fields.

    Returns:
        dict with file (name without extension), title, header (fields of the
        line after the title) and rows: list of (name, label, moment, dec, inc).
    """
    lines = [ln for ln in Path(path).read_text(encoding="latin-1").splitlines()]
    while lines and not lines[0].strip():
        lines = lines[1:]
    title, header = lines[0].split(), lines[1].split()
    rows = []
    for ln in lines[2:]:
        t = ln.split()
        if len(t) >= 5:
            rows.append((t[0], t[1], float(t[2]), float(t[3]), float(t[4])))
    return dict(file=Path(path).stem, title=title, header=header, rows=rows, relabeled=[])


def relabel_infield_steps(tdt):
    """Correct in-field steps labeled a degree or two off their zero-field step.

    In a Coe experiment every in-field step follows a zero-field step at the
    same temperature. An in-field step at a temperature without a zero-field
    step, within 2 degrees of the latest zero-field step that still lacks its
    in-field step, is relabeled to that temperature (e.g. 566.11 after 565.00).
    """
    zero, infield, last_zero, rows = set(), set(), None, []
    for name, label, m, d, i in tdt["rows"]:
        t, kind = decode_coded(label)
        if kind in ("NRM", "Z"):
            zero.add(t)
            last_zero = t
        elif kind == "I":
            if t not in zero and last_zero not in infield and abs(t - last_zero) <= 2:
                tdt["relabeled"].append((label, f"{last_zero}.11"))
                label, t = f"{last_zero}.11", last_zero
            infield.add(t)
        rows.append((name, label, m, d, i))
    tdt["rows"] = rows
    return tdt


def is_coded(tdt):
    """True if the steps carry ThellierTool codes (e.g. 328.11), False for labels such as 329C."""
    return not any(label.endswith("C") for _, label, _, _, _ in tdt["rows"])


def decode_coded(label):
    """(temperature, kind) for a ThellierTool step code: kind is NRM, Z, I or check."""
    temperature, _, code = label.partition(".")   # a zero-field step may be written without decimals
    kind = {"": "Z", "00": "Z", "0": "Z", "11": "I", "12": "check"}[code]
    return int(temperature), "NRM" if (kind == "Z" and int(temperature) < 50) else kind


def decode_raw(labels):
    """Steps of a file labeled at measurement: list of (temperature, kind).

    A zero-field step at T is followed by T+1 (in field at T), or by T+1 (pTRM
    check at the preceding temperature) and T+2 (in field at T).
    """
    numbers = [None if lab == "NRM" else int(lab[:-1]) for lab in labels]
    steps, previous, i = [], None, 0
    while i < len(numbers):
        if numbers[i] is None:
            steps.append((20, "NRM"))
            i += 1
            continue
        t = numbers[i]
        group = [t]
        while i + len(group) < len(numbers) and numbers[i + len(group)] is not None \
                and 0 < numbers[i + len(group)] - t <= 2:
            group.append(numbers[i + len(group)])
        if len(group) == 2:
            steps += [(t, "Z"), (t, "I")]
        elif len(group) == 3:
            steps += [(t, "Z"), (previous, "check"), (t, "I")]
        else:
            raise ValueError(f"steps {group} not understood")
        previous = t
        i += len(group)
    return steps


def survey_tdt(folder):
    """Read every file; pair each file labeled at measurement with its coded copy.

    Returns:
        (coded, raw_pairs, notes): coded maps specimen name to its tdt dict;
        raw_pairs is a DataFrame comparing each raw file with the coded file
        that has the same NRM.
    """
    files = [read_tdt(p) for p in sorted(Path(folder).glob("*.tdt"))]
    notes, coded = [], OrderedDict()
    for tdt in (f for f in files if is_coded(f)):
        names = Counter(r[0] for r in tdt["rows"])
        written = names.most_common(1)[0][0]
        name = re.sub("-+", "-", written)
        if len(names) > 1:
            notes.append(f"{tdt['file']}.tdt: several names in the specimen column "
                         f"({', '.join(f'{k} ({v} rows)' for k, v in names.most_common())}); {name} is used.")
        if name != written:
            notes.append(f"{tdt['file']}.tdt: specimen written {written} in the file, entered as {name}.")
        if name != tdt["file"]:
            notes.append(f"{tdt['file']}.tdt holds specimen {name}.")
        if tdt["header"][:1] != ["40"]:
            notes.append(f"{tdt['file']}.tdt: header line reads {' '.join(tdt['header'])}.")
        relabel_infield_steps(tdt)
        for old, new in tdt["relabeled"]:
            notes.append(f"{tdt['file']}.tdt: in-field step {old} follows the zero-field step at "
                         f"{new.split('.')[0]} °C and is entered as {new}.")
        tdt["specimen"] = name
        coded[name] = tdt
    pairs = []
    for raw in (f for f in files if not is_coded(f)):
        rows = raw["rows"]
        labels = [r[1] for r in rows]
        # the coded file that shares the most measured directions (declination, inclination)
        a = [r[3:] for r in rows]
        shared = {n: sum(1 for x in a if x in [r[3:] for r in c["rows"]]) for n, c in coded.items()}
        best = max(shared, key=shared.get)
        match = [best] if shared[best] >= len(a) // 2 else []
        entry = dict(raw_file=raw["file"], name_column=f"{rows[0][0]} to {rows[-1][0]}", rows=len(rows),
                     coded_specimen=match[0] if match else "", same_directions="", moment_ratio=np.nan,
                     rows_not_in_coded="", step_kinds_agree="")
        if match:
            b = {r[3:]: r[2] for r in coded[match[0]]["rows"]}
            entry["same_directions"] = f"{shared[best]} of {len(a)}"
            entry["moment_ratio"] = float(np.median([b[r[3:]] / r[2] for r in rows if r[3:] in b]))
            entry["rows_not_in_coded"] = "; ".join(f"{r[1]} {r[2]:g} {r[3]:g}/{r[4]:g}" for r in rows if r[3:] not in b)
            try:
                steps = decode_raw(labels)
                kinds_coded = [decode_coded(r[1])[1] for r in coded[match[0]]["rows"]]
                entry["step_kinds_agree"] = [k for _, k in steps] == kinds_coded
            except (ValueError, KeyError):
                entry["step_kinds_agree"] = "labels not regular"
        pairs.append(entry)
    return coded, pd.DataFrame(pairs), notes


# ---------------------------------------------------------------- Arai analysis

def arai_points(tdt):
    """NRM remaining and pTRM gained at each temperature, and the pTRM checks.

    Returns:
        (points, checks): points is a list of dicts (t, nrm, ptrm, zero-field
        vector); checks a list of dicts (t, after, ptrm) where `after` is the
        zero-field temperature that preceded the check.
    """
    def vector(row):
        return np.array(pmag.dir2cart([row[3], row[4], row[2]]))

    zero, infield, checks, last_zero = OrderedDict(), {}, [], None
    for row in tdt["rows"]:
        t, kind = decode_coded(row[1])
        if kind in ("NRM", "Z"):
            zero[t] = vector(row)
            last_zero = t
        elif kind == "I":
            infield[t] = vector(row)
        else:
            checks.append(dict(t=t, after=last_zero, ptrm=np.linalg.norm(vector(row) - zero[last_zero])))
    points = []
    for t, z in zero.items():
        if t < 50:
            points.append(dict(t=t, nrm=np.linalg.norm(z), ptrm=0.0, z=z))
        elif t in infield:
            points.append(dict(t=t, nrm=np.linalg.norm(z), ptrm=np.linalg.norm(infield[t] - z), z=z))
    return points, checks


def paleointensity(points, t_min, t_max, lab_field=pub.THELLIER_LAB_FIELD):
    """Best-fit line on the Arai plot (Coe et al., 1978) between two temperatures.

    Returns:
        dict with n, B and B_sigma (tesla), beta (sigma/slope), f (relative to
        the y intercept of the line), g and q.
    """
    # the unheated point (NRM, no pTRM) is not one of the N points of a ThellierTool fit
    sel = [p for p in points if t_min <= p["t"] <= t_max and p["t"] > 50]
    x, y = np.array([p["ptrm"] for p in sel]), np.array([p["nrm"] for p in sel])
    n = len(sel)
    dx, dy = x - x.mean(), y - y.mean()
    slope = -np.sqrt(np.sum(dy ** 2) / np.sum(dx ** 2))
    sigma = np.sqrt((2 * np.sum(dy ** 2) - 2 * slope * np.sum(dx * dy)) / ((n - 2) * np.sum(dx ** 2)))
    intercept = y.mean() - slope * x.mean()
    # the selected points projected on the line
    y_line = (slope * x + intercept + y) / 2
    delta_y = abs(y_line[0] - y_line[-1])
    f = delta_y / intercept
    g = 1 - np.sum(np.diff(y_line) ** 2) / delta_y ** 2
    beta = sigma / abs(slope)
    return dict(n=n, B=abs(slope) * lab_field, B_sigma=sigma * lab_field, beta=beta, f=f, g=g,
                q=f * g / beta, first=sel[0]["t"], last=sel[-1]["t"])


def recalculate_thellier(coded):
    """Recalculate each Table 2 determination from the archived measurements."""
    rows = []
    for p in pub.TABLE2_THELLIER.itertuples():
        points, _ = arai_points(coded[p.specimen])
        temps = [p["t"] for p in points]
        result = paleointensity(points, p.t_min, p.t_max)
        row = dict(specimen=p.specimen, range=f"{p.t_min}-{p.t_max}",
                   N_pub=p.N, N=result["n"], B_pub=p.B, B=result["B"] * 1e6,
                   B_sigma_pub=p.B_sigma, B_sigma=result["B_sigma"] * 1e6,
                   beta_pub=p.beta, beta=result["beta"], f_pub=p.f, f=result["f"],
                   q_pub=p.q, q=result["q"])
        # the archived moments have three significant figures, so the last printed digit can differ
        agree = (row["N"] == p.N and abs(row["B"] - p.B) <= 0.1 and abs(row["B_sigma"] - p.B_sigma) <= 0.1
                 and abs(row["f"] - p.f) <= 0.025 and abs(row["q"] - p.q) <= max(0.1, 0.03 * p.q))
        row["agrees"] = "yes" if agree and abs(row["beta"] - p.beta) <= 0.0015 else \
            "yes, except sigma/slope" if agree else "no"
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- conversion

def convert_thellier(coded, work_dir):
    """Convert the 66 coded files with PmagPy and return the measurements table.

    The files are written to work_dir/tdt with the specimen names and step
    labels as entered in the contribution (the measurements are unchanged); the
    converter writes its tables to work_dir/converted_thellier.
    """
    tdt_dir, out_dir = Path(work_dir) / "tdt", Path(work_dir) / "converted_thellier"
    for d in (tdt_dir, out_dir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for name, tdt in coded.items():
        # the file as archived, with the specimen name and step labels as entered here
        lines = ["Thellier-TDT", "\t".join(tdt["header"][:5])]
        lines += ["\t".join([name + pub.THELLIER_SUFFIX, label, f"{m:.3E}", f"{d:g}", f"{i:g}"])
                  for _, label, m, d, i in tdt["rows"]]
        (tdt_dir / f"{name}{pub.THELLIER_SUFFIX}.tdt").write_text("\n".join(lines) + "\n")
    # The in-field steps point to -Z in specimen coordinates. The files state no unit for the
    # moments. They have the values of the demagnetization files flow by flow and are treated the
    # same way: emu/cm3, converted to A/m (README.md, "Units"). The converter copies the numbers
    # unchanged; they are scaled and the column renamed below.
    ok, message = convert_2_magic.tdt(str(tdt_dir), output_dir_path=str(out_dir), moment_units="Am^2",
                              lab_dec=0, lab_inc=-90, location=pub.LOCATION)
    if not ok:
        raise RuntimeError(message)
    meas = pd.read_csv(out_dir / "measurements.txt", sep="\t", header=1, dtype=object,
                       keep_default_na=False, na_values=[""])
    meas["magn_volume"] = (meas.pop("magn_moment").astype(float) * pub.EMU_PER_CM3_TO_A_PER_M).map("{:.4g}".format)
    return meas


def thellier_specimen_rows(meas):
    """Specimens-table rows for the Thellier specimens: the Table 2 results, or a bare record."""
    experiments = meas.groupby("specimen")["experiment"].first()
    codes = meas.groupby("specimen")["method_codes"].agg(
        lambda c: ":".join(sorted({x for code in c for x in code.split(":") if x.startswith("LP-")})))
    table2 = pub.TABLE2_THELLIER.set_index("specimen")
    rows = []
    for specimen in experiments.index:
        row = OrderedDict(specimen=specimen, experiments=experiments[specimen],
                          method_codes=codes[specimen], citations="This study")
        name = specimen[:-len(pub.THELLIER_SUFFIX)]
        if name in table2.index:
            p = table2.loc[name]
            row.update(method_codes=codes[specimen] + ":IE-TT", result_quality="g",
                       int_abs=f"{p['B'] * 1e-6:.3e}", int_abs_sigma=f"{p['B_sigma'] * 1e-6:.1e}",
                       int_treat_dc_field=f"{pub.THELLIER_LAB_FIELD:.1e}", int_n_measurements=int(p["N"]),
                       int_f=p["f"], int_q=p["q"], int_b_beta=p["beta"], int_dck=p["dck"],
                       int_k_prime=p["k_prime"], int_mad_anc=p["mad"], int_alpha=p["alpha"],
                       meas_step_min=f"{p['t_min'] + 273:.0f}", meas_step_max=f"{p['t_max'] + 273:.0f}",
                       meas_step_unit="K", software_packages="ThellierTool 4.22",
                       description=(f"Published as {name}. Thellier-Coe determination, class {p['class']} "
                                    f"(Table 2), published range {p['t_min']}-{p['t_max']} °C; the N points "
                                    "are heating steps, the unheated point is not one of them."))
            if abs(p["beta"] - p["B_sigma"] / p["B"]) > 0.01:
                row["description"] += (f" Table 2 gives β {p['beta']:.3f}, but its B and standard error give "
                                       f"{p['B_sigma'] / p['B']:.3f}; entered as printed.")
            row["description"] += " " + pub.UNITS_NOTE
        else:
            row["description"] = (f"Named {name} in the archived file. Thellier-Coe experiment; no "
                                  "determination accepted by the authors. " + pub.UNITS_NOTE)
        rows.append(row)
    return pd.DataFrame(rows)


# ================================================================ multispecimen (.jr6)
#
# Five JR6 files, M0 to M4, one per step of the protocol of Fabian and
# Leonhardt (2010) (section 7.2 of the paper), each with one row for each of 77
# sub-specimens: seven per flow, numbered 1 to 7, heated in fields of 10 to 70
# μT. In M1 to M4 the step label of a row is the field ("A10" is 10 μT;
# convert_2_magic.jr6_jr6 takes it for an alternating field of 10 mT), so the
# files are read here.

MS_STEPS = OrderedDict([
    (0, "natural remanence"),
    (1, "after heating and cooling in the laboratory field, parallel to the NRM"),
    (2, "after heating and cooling in the laboratory field, antiparallel to the NRM"),
    (3, "after heating in zero field and cooling in the laboratory field"),
    (4, "repeat of step 1 (alteration check)")])
MS_EXPERIMENT = "LP-PI-MULT-FL"
MS_TEMPERATURE_NOTE = "heated to 400 or 450 °C (the paper does not say which flows had which)"


def read_jr6(path):
    """Rows of a .jr6 file in order: list of (name, label, moment vector in A/m)."""
    rows = []
    for line in path.read_text(encoding="latin-1").splitlines():
        if not line.strip():
            continue
        x, y, z, exponent = float(line[18:24]), float(line[24:30]), float(line[30:36]), int(line[36:40])
        rows.append((line[:10].strip(), line[10:18].strip(), np.array([x, y, z]) * 10.0 ** exponent))
    return rows


def load_multispecimen(folder):
    """Read M0 to M4 and line the rows up by sub-specimen.

    A row of M1 to M4 is identified by the flow in its name and the field in
    its step label, because in two rows the name carries another sub-specimen
    number. In two files a name occurs twice and another is absent; the files
    list each field as a block of the eleven flows, and the order of the flows
    in the other blocks of the file shows which of the two rows is the absent
    sub-specimen.

    Returns:
        (specimens, notes): specimens is an ordered dict of name (as in M0) to
        dict(field in tesla, vectors: list of the five moment vectors); notes
        lists the rows whose name was corrected.
    """
    files = [read_jr6(folder / f"M{k}.jr6") for k in MS_STEPS]
    reference = [name for name, _, _ in files[0]]
    if len(set(reference)) != len(reference):
        raise ValueError("M0.jr6 has repeated names")
    flows = sorted({name.split("-")[0] for name in reference}, key=lambda f: int(f[3:]))
    notes, specimens = [], OrderedDict((name, dict(field=None, vectors=[v])) for name, _, v in files[0])
    for k, rows in enumerate(files[1:], start=1):
        # the blocks of the file: field label -> rows in file order
        blocks = OrderedDict()
        for written, label, vector in rows:
            blocks.setdefault(label, []).append([written.split("-")[0], written, vector])
        orders = [tuple(r[0] for r in block) for block in blocks.values()
                  if sorted(r[0] for r in block) == sorted(flows)]
        for label, block in blocks.items():
            sequence = [r[0] for r in block]
            repeated = [f for f in flows if sequence.count(f) > 1]
            absent = [f for f in flows if f not in sequence]
            if repeated:
                if len(repeated) != 1 or len(absent) != 1 or sequence.count(repeated[0]) != 2:
                    raise ValueError(f"M{k}.jr6, {label}: flows {sequence} not understood")
                # which of the two rows makes the block follow the order of another block
                positions = [i for i, f in enumerate(sequence) if f == repeated[0]]
                fits = [i for i in positions
                        if tuple(sequence[:i] + absent + sequence[i + 1:]) in orders]
                if len(fits) != 1:
                    raise ValueError(f"M{k}.jr6, {label}: cannot tell which {repeated[0]} row is {absent[0]}")
                block[fits[0]][0] = absent[0]
            for flow, written, vector in block:
                number = int(label[1:]) // 10
                name = f"{flow}-{number}"
                if written != name:
                    notes.append(f"M{k}.jr6: the row named {written} with field label {label} is entered as "
                                 f"{name}" + (" (it stands where the other blocks of the file have flow "
                                              f"{flow})" if written.split("-")[0] != flow else "") + ".")
                if len(specimens[name]["vectors"]) != k:
                    raise ValueError(f"M{k}.jr6: {name} occurs twice")
                specimens[name]["field"] = float(label[1:]) * 1e-6
                specimens[name]["vectors"].append(vector)
    incomplete = [name for name, sp in specimens.items() if len(sp["vectors"]) != len(MS_STEPS)]
    if incomplete:
        raise ValueError(f"sub-specimens without all steps: {incomplete}")
    return specimens, notes


def ms_measurement_rows(specimens):
    """MagIC measurements: five rows per sub-specimen."""
    rows = []
    for name, sp in specimens.items():
        specimen = name + pub.MULTISPECIMEN_SUFFIX
        for k, description in MS_STEPS.items():
            dec, inc, moment = pmag.cart2dir(sp["vectors"][k])
            row = OrderedDict(
                measurement=f"{specimen}_{MS_EXPERIMENT}-{k + 1}", experiment=f"{specimen}_{MS_EXPERIMENT}",
                specimen=specimen, dir_dec=f"{dec:.1f}", dir_inc=f"{inc:.1f}", magn_volume=f"{moment:.4g}",
                treat_step_num=k, meas_temp="273", quality="g", standard="u", citations="This study",
                method_codes=("LT-NO" if k == 0 else "LT-T-I") + ":" + MS_EXPERIMENT,
                description=f"Multispecimen step m{k}: {description}"
                            + ("" if k == 0 else f"; {MS_TEMPERATURE_NOTE}") + ".")
            if k > 0:
                row["treat_dc_field"] = f"{sp['field']:.1e}"
            rows.append(row)
    return pd.DataFrame(rows)


def ms_specimen_rows(specimens):
    """MagIC specimens: one row per sub-specimen, in the sample `<flow>-MS`."""
    rows = []
    for name, sp in specimens.items():
        flow, number = name.split("-")
        rows.append(OrderedDict(
            specimen=name + pub.MULTISPECIMEN_SUFFIX, sample=f"{flow}-MS", experiments=f"{name}{pub.MULTISPECIMEN_SUFFIX}_{MS_EXPERIMENT}",
            method_codes=MS_EXPERIMENT, citations="This study",
            description=(f"Named {name} in the archived files. Multispecimen sub-specimen {number} of flow "
                         f"{flow}, pressed into a salt pellet; laboratory field {sp['field'] * 1e6:.0f} μT.")))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- a check on the published values

def ms_ratios(sp):
    """The multispecimen ms_ratios of one sub-specimen.

    Returns:
        dict with field (microtesla), db: (m1 - m0) / m0 from the moduli
        (Dekkers and Böhnel, 2006), fc: 2 (m1 - m0) / (2 m0 - m1 - m2) from the
        components along the NRM (fraction correction of Fabian and Leonhardt,
        2010), and alteration: (m4 - m1) / m1 in percent.
    """
    m = sp["vectors"]
    modulus = [float(np.linalg.norm(v)) for v in m]
    unit = m[0] / modulus[0]
    along = [float(v @ unit) for v in m]
    return dict(field=sp["field"] * 1e6, db=(modulus[1] - modulus[0]) / modulus[0],
                fc=2 * (along[1] - along[0]) / (2 * along[0] - along[1] - along[2]),
                alteration=100 * (modulus[4] - modulus[1]) / modulus[1])


def regression_zero(fields, values):
    """Field at which the least-squares line through (field, ratio) crosses zero, and R squared."""
    slope, intercept = np.polyfit(fields, values, 1)
    return -intercept / slope, float(np.corrcoef(fields, values)[0, 1] ** 2)


def closest_subset(specimens, site, key, n, target):
    """The n sub-specimens of a flow whose regression comes closest to a published value.

    Returns:
        dict with B and r2 of all sub-specimens and of the closest subset, the
        mean alteration of the subset, and the names used and left out.
    """
    names = [name for name in specimens if name.split("-")[0] == site]
    data = [ms_ratios(specimens[name]) for name in names]
    fields, values = np.array([d["field"] for d in data]), np.array([d[key] for d in data])
    alteration = np.array([d["alteration"] for d in data])
    b_all, r2_all = regression_zero(fields, values)
    best = None
    for subset in itertools.combinations(range(len(names)), int(n)):
        idx = list(subset)
        b, r2 = regression_zero(fields[idx], values[idx])
        if best is None or abs(b - target) < abs(best[0] - target):
            best = (b, r2, idx)
    b, r2, idx = best
    return dict(B_all=b_all, r2_all=r2_all, B=b, r2=r2, alteration=float(alteration[idx].mean()),
                used=[names[i] for i in idx], left_out=[names[i] for i in range(len(names)) if i not in idx])


def recalculate_ms_standard(specimens):
    """The standard (MSP-DB) determinations of Table S3, recalculated.

    The ratio (m1 - m0) / m0 from the moduli is regressed on the field; the
    zero crossing is the paleointensity. Where Table S3 rejects sub-specimens
    the N that come closest to its value are used. `agrees` is yes when B is
    within 0.15 microtesla, R squared within 0.002 and the mean alteration
    within 0.7 percent of Table S3.
    """
    rows = []
    for p in pub.TABLE_S3[pub.TABLE_S3["type"] == "DB"].itertuples():
        c = closest_subset(specimens, p.site, "db", p.N, p.B)
        agrees = (abs(c["B"] - p.B) <= 0.15 and abs(c["r2"] - p.r2) <= 0.002
                  and abs(c["alteration"] - p.eps_alt) <= 0.7)
        rows.append(dict(site=p.site, N_pub=p.N, B_pub=p.B, B=c["B"], r2_pub=p.r2, r2=c["r2"],
                         alteration_pub=p.eps_alt, alteration=c["alteration"], used=c["used"],
                         left_out=c["left_out"], agrees="yes" if agrees else "no"))
    return pd.DataFrame(rows)


def recalculate_multispecimen(specimens):
    """The determinations selected by the authors (Table 2), compared with a plain calculation.

    For each flow the ratio of the selected protocol (db for DB and DBc, fc for
    FCc) is regressed on the field, with all seven sub-specimens and with the N
    that come closest to the published value. This is not the authors'
    calculation: there is no alignment correction and no bootstrap for the
    bounds. The rejected sub-specimens are taken to be those left out where

        - this calculation gives the published B (within 0.35 microtesla), R
          squared (0.003) and alteration (1 percent), or
        - the protocol is DB or DBc, the standard determination of Table S3
          rejects the same number, and that determination is reproduced
          (recalculate_ms_standard).

    Returns:
        DataFrame, one row per flow; `established` says whether the rejected
        sub-specimens are identified, and how.
    """
    standard = recalculate_ms_standard(specimens).set_index("site")
    rows = []
    for p in pub.TABLE2_MULTISPECIMEN.itertuples():
        key = "fc" if p.type.startswith("FC") else "db"
        c = closest_subset(specimens, p.site, key, p.N, p.B)
        agrees = (abs(c["B"] - p.B) <= 0.35 and abs(c["r2"] - p.r2) <= 0.003
                  and abs(c["alteration"] - p.eps_alt) <= 1.0)
        established = "this calculation" if agrees else "no"
        used, left_out = c["used"], c["left_out"]
        if not agrees and key == "db" and p.site in standard.index:
            st = standard.loc[p.site]
            if st["N_pub"] == p.N and st["agrees"] == "yes":
                established, used, left_out = "standard determination (Table S3)", st["used"], st["left_out"]
        rows.append(dict(site=p.site, type=p.type, ratio=key, B_pub=p.B, N_pub=p.N,
                         B_all=c["B_all"], B_closest=c["B"], r2_pub=p.r2, r2_closest=c["r2"],
                         alteration_pub=p.eps_alt, alteration=c["alteration"], used=used, left_out=left_out,
                         established=established))
    return pd.DataFrame(rows)


# ================================================================ rock magnetism (VFTB)
#
# One powder per flow, measured on a variable field translation balance: an IRM
# acquisition curve (.irm), a hysteresis loop (.hys), a back-field curve (.coe)
# and a magnetization-temperature curve in 38 mT (.rmp; none for PRG8-7), in
# emu/g with the weight of the powder. Each file is converted with
# convert_2_magic.vftb, which takes the kind of curve from the extension.

VFTB_CURVES = OrderedDict([("irm", "IRM acquisition"), ("hys", "hysteresis loop"),
                      ("coe", "back-field demagnetization of the IRM"),
                      ("rmp", "magnetization against temperature in a field of 38 mT, heating and cooling")])


def convert_vftb(folder, work_dir):
    """Convert every VFTB file and gather the measurements and specimens.

    Args:
        folder: directory with the .irm, .hys, .coe and .rmp files.
        work_dir: build directory; the converter output goes to work_dir/converted_rockmag.

    Returns:
        (measurements, specimens, notes): DataFrames in MagIC columns. The
        specimen of a file PRG1-2.irm is PRG1-2 with the rock-magnetic suffix,
        a powder of the core PRG1-2.
    """
    out_dir = work_dir / "converted_rockmag"
    out_dir.mkdir(parents=True, exist_ok=True)
    measurements, specimens, notes = [], OrderedDict(), []
    for path in sorted(folder.iterdir()):
        extension = path.suffix.lstrip(".").lower()
        if extension not in VFTB_CURVES:
            notes.append(f"{path.name}: not a VFTB curve file, not converted.")
            continue
        core = path.stem
        specimen = core + pub.ROCKMAG_SUFFIX
        stem = f"{core}_{extension}"
        ok, message = convert_2_magic.vftb(path.name, dir_path=str(out_dir), input_dir_path=str(folder),
                                   meas_outfile=f"{stem}_measurements.txt", spec_outfile=f"{stem}_specimens.txt",
                                   samp_outfile=f"{stem}_samples.txt", site_outfile=f"{stem}_sites.txt",
                                   loc_outfile=f"{stem}_locations.txt", specimen=specimen, samp_con="2",
                                   location=pub.LOCATION)
        if not ok:
            raise RuntimeError(f"{path.name}: {message}")
        meas = pd.read_csv(out_dir / f"{stem}_measurements.txt", sep="\t", header=1, dtype=object,
                           keep_default_na=False, na_values=[""])
        experiment = meas["experiment"].iloc[0]
        measurements.append(meas)
        spec = pd.read_csv(out_dir / f"{stem}_specimens.txt", sep="\t", header=1, dtype=object,
                           keep_default_na=False, na_values=[""]).iloc[0]
        entry = specimens.setdefault(specimen, dict(core=core, weight=spec.get("weight"), experiments=[],
                                                     codes=[], curves=[]))
        if spec.get("weight") != entry["weight"]:
            notes.append(f"{path.name}: weight {spec.get('weight')} kg differs from the other files of "
                         f"{core} ({entry['weight']} kg).")
        entry["experiments"].append(experiment)
        entry["codes"].append(meas["method_codes"].iloc[0].split(":")[0])
        entry["curves"].append(VFTB_CURVES[extension])
    missing = [f"{entry['core']}.{ext}" for entry in specimens.values() for ext in VFTB_CURVES
               if VFTB_CURVES[ext] not in entry["curves"]]
    if missing:
        notes.append("No file for: " + ", ".join(missing) + ".")
    rows = [OrderedDict(
        specimen=name, sample=entry["core"], weight=entry["weight"], experiments=":".join(entry["experiments"]),
        method_codes=":".join(entry["codes"]), citations="This study",
        description=(f"Named {entry['core']} in the archived files. Powder of the core, measured on a variable "
                     f"field translation balance: {'; '.join(entry['curves'])}."))
        for name, entry in specimens.items()]
    return pd.concat(measurements, ignore_index=True), pd.DataFrame(rows), notes


def saturation_remanence(measurements):
    """Largest IRM (Am2/kg) of each specimen's acquisition curve, by core name."""
    irm = measurements[measurements["method_codes"] == "LP-IRM"]
    return irm["magn_mass"].astype(float).groupby(irm["specimen"].str[:-len(pub.ROCKMAG_SUFFIX)]).max()


# ---------------------------------------------------------------- the published results (Table S1)

def rockmag_specimen_rows():
    """Specimens-table rows with the rock-magnetic results of Table S1.

    One row per powder with the hysteresis parameters, and one row for each
    Curie temperature. Mrs and Ms are multiplied by pub.TABLE_S1_MOMENT_FACTOR
    (README.md: printed 1000 times smaller than the archived curves).

    Returns:
        (hysteresis, curie): two DataFrames keyed by specimen.
    """
    hysteresis, curie = [], []
    for r in pub.TABLE_S1.itertuples():
        specimen = r.sample + pub.ROCKMAG_SUFFIX
        hysteresis.append(OrderedDict(
            specimen=specimen,
            hyst_mr_mass=f"{r.mrs * pub.TABLE_S1_MOMENT_FACTOR:.3g}", hyst_ms_mass=f"{r.ms * pub.TABLE_S1_MOMENT_FACTOR:.3g}",
            hyst_mr_ms=r.mrs_ms, hyst_bc=f"{r.bc * 1e-3:.5f}", hyst_bcr=f"{r.bcr * 1e-3:.5f}", hyst_bcr_bc=r.bcr_bc,
            rem_sratio=r.s_ratio, rem_sratio_back=0.3,
            results=(f"Rock-magnetic results of Table S1; Mrs and Ms are printed there as {r.mrs:.2E} and "
                     f"{r.ms:.2E} \"Am2/kg\" and entered 1000 times larger, in line with the archived curves in "
                     f"emu/g. Also in Table S1: Brh/Bcr {r.brh_bcr:g}, shape parameter {r.sigma:g}.")))
        for branch, code, order in (("heating", "LP-MW-I", (r.tc1_heating, r.tc2_heating)),
                                    ("cooling", "LP-MC-I", (r.tc1_cooling, r.tc2_cooling))):
            for k, value in enumerate(order, start=1):
                if value is None or np.isnan(value):
                    continue
                curie.append(OrderedDict(
                    specimen=specimen, sample=r.sample, critical_temp=f"{value + 273:.0f}",
                    critical_temp_type="Curie", method_codes=f"LP-IMT:{code}:SM-2TAN", citations="This study",
                    description=(f"Curie temperature {value:g} °C from the {branch} branch of the "
                                 f"magnetization-temperature curve, two-tangent method (Table S1, column "
                                 f"TC{k}({'H' if branch == 'heating' else 'C'}))"
                                 + ("; a second, low-temperature phase." if k == 2 else "."))))
    return pd.DataFrame(hysteresis), pd.DataFrame(curie)


# ---------------------------------------------------------------- a check on the published results

def first_zero_crossing(x, y):
    """x at which y first changes sign, by linear interpolation between the two points."""
    for k in range(len(y) - 1):
        if y[k] == 0:
            return float(x[k])
        if y[k] * y[k + 1] < 0:
            return float(x[k] - y[k] * (x[k + 1] - x[k]) / (y[k + 1] - y[k]))
    return np.nan


def recalculate_rockmag(measurements):
    """Hysteresis and remanence parameters from the archived curves, against Table S1.

    A simple calculation, not that of the authors' software: the saturation
    remanence is the largest IRM and the first point of the back-field curve;
    Bcr is where the back-field curve crosses zero; the S ratio is
    (1 - IRM(-0.3 T) / SIRM) / 2; for the loop, the high-field slope is fitted
    above 60 percent of the peak field and removed, Ms is the intercept, and
    Mrs and Bc are read from the two branches of the corrected loop.
    """
    rows = []
    for r in pub.TABLE_S1.itertuples():
        m = measurements[measurements["specimen"] == r.sample + pub.ROCKMAG_SUFFIX]
        out = dict(sample=r.sample, mrs_pub=r.mrs * pub.TABLE_S1_MOMENT_FACTOR, ms_pub=r.ms * pub.TABLE_S1_MOMENT_FACTOR,
                   bc_pub=r.bc, bcr_pub=r.bcr, s_pub=r.s_ratio)
        irm = m[m["method_codes"] == "LP-IRM"]
        out["sirm_irm"] = irm["magn_mass"].astype(float).max()
        back = m[m["method_codes"] == "LP-IRM-DCD"]
        field, moment = back["treat_dc_field"].astype(float).values, back["magn_mass"].astype(float).values
        out["sirm_back"] = float(moment[0])
        out["bcr"] = abs(first_zero_crossing(field, moment)) * 1e3
        out["s_ratio"] = (1 - float(np.interp(0.3, -field, moment)) / moment[0]) / 2
        loop = m[m["method_codes"] == "LP-HYS"]
        h, mag = loop["meas_field_dc"].astype(float).values, loop["magn_mass"].astype(float).values
        top, bottom = int(h.argmax()), int(h.argmin())
        high = h >= 0.6 * h.max()
        low = h <= 0.6 * h.min()
        slope_high, intercept_high = np.polyfit(h[high], mag[high], 1)
        slope_low, intercept_low = np.polyfit(h[low], mag[low], 1)
        slope = (slope_high + slope_low) / 2
        corrected = mag - slope * h
        out["ms"] = (intercept_high - intercept_low) / 2
        descending, ascending = slice(top, bottom + 1), slice(bottom, len(h))
        out["mrs_loop"] = (abs(float(np.interp(0, h[descending][::-1], corrected[descending][::-1])))
                           + abs(float(np.interp(0, h[ascending], corrected[ascending])))) / 2
        out["bc"] = (abs(first_zero_crossing(h[descending], corrected[descending]))
                     + abs(first_zero_crossing(h[ascending], corrected[ascending]))) / 2 * 1e3
        rows.append(out)
    return pd.DataFrame(rows)


# ================================================================ the contribution

# ---------------------------------------------------------------- flow-mean paleointensities

def build_intensity_sites(thellier_names, ms_check):
    """Sites-table rows for the flow paleointensities of Table 3, and a check of their means.

    Each flow gets one row: the result to which Table 3 gives a class. The
    other rows of Table 3 for that flow are described in it.

    Args:
        thellier_names: dict of published Thellier specimen name to the name in the contribution.
        ms_check: the recalculation of the multispecimen determinations.

    Returns:
        (rows, checks): the sites rows, and a DataFrame comparing every row of
        Table 3 with the mean and standard deviation of the Table 2 values.
    """
    coe = pub.TABLE2_THELLIER.assign(site=pub.TABLE2_THELLIER["specimen"].map(flow_name))
    ms = pub.TABLE2_MULTISPECIMEN.set_index("site")
    recalculated = ms_check.set_index("site")
    rows, checks = [], []
    # Table 2 against the rows of Table S3 for the same protocol (noted on the flow's row)
    s3 = pub.TABLE2_MULTISPECIMEN.merge(pub.TABLE_S3, on=["site", "type"], suffixes=("_t2", "_s3"))
    s3_notes = {r["site"]: [f"{c} {r[c + '_t2']} in Table 2, {r[c + '_s3']} in Table S3"
                            for c in ("B", "B_min", "B_max", "N", "rejected", "eps_alt", "r2")
                            if r[c + "_t2"] != r[c + "_s3"]] for _, r in s3.iterrows()}
    for site, group in pub.TABLE3.groupby("site", sort=False):
        specimens = coe[coe["site"] == site]
        values = list(specimens["B"])
        sds = {}
        for r in group.itertuples():
            if r.treatment == "MS":
                continue
            pooled = values + ([ms.loc[site, "B"]] if r.treatment == "Coe + MS" else [])
            sd = float(np.std(pooled, ddof=1)) if len(pooled) > 1 else float(specimens["B_sigma"].iloc[0])
            sds[r.treatment] = sd
            checks.append(dict(site=site, treatment=r.treatment, N_pub=r.N, N=len(pooled), B_pub=r.B,
                               B=float(np.mean(pooled)), sigma_pub=r.sigma, sigma=sd, percent_pub=r.percent,
                               percent=100 * sd / float(np.mean(pooled))))
        final = group[group["class"] != ""].iloc[0]
        description = f"Flow paleointensity (Table 3, {final['treatment']}), {pub.CLASSES[final['class']]}."
        if final["treatment"] in sds and abs(100 * final["sigma"] / final["B"] - final["percent"]) > 0.5:
            description += (f" Table 3 gives σ {final['sigma']:.1f} μT and {final['percent']} percent, which do "
                            f"not agree ({final['percent']} percent of {final['B']:.1f} μT is "
                            f"{final['percent'] * final['B'] / 100:.1f} μT); the standard deviation of the values "
                            f"is {sds[final['treatment']]:.2f} μT. Both are entered as printed.")
        columns = dict(int_abs=f"{final['B'] * 1e-6:.3e}", int_n_samples=int(final["N"]))
        codes = []
        if "Coe" in final["treatment"]:
            codes += ["LP-PI-TRM", "LP-PI-ALT-PTRM", "IE-TT"]
            columns.update(int_abs_sigma=f"{final['sigma'] * 1e-6:.1e}", int_abs_sigma_perc=final["percent"],
                           int_n_specimens=len(specimens),
                           specimens=join(thellier_names[s] for s in specimens["specimen"]))
            description += (f" Thellier-Coe determinations (Table 2): "
                            + ", ".join(f"{b:.1f}" for b in values) + " μT.")
            alone = group[group["treatment"] == "Coe"]
            if final["treatment"] == "Coe + MS" and len(alone):
                a = alone.iloc[0]
                description += f" Thellier-Coe alone: {a['B']:.1f} ± {a['sigma']:.1f} μT (N = {a['N']})."
        if "MS" in final["treatment"]:
            m = ms.loc[site]
            codes.append("LP-PI-MULT-FL" if m["type"].startswith("FC") else "LP-PI-MULT-DB")
            description += (f" Multispecimen determination (Table 2): {m['B']:.1f} μT, bounds {m['B_min']:.1f} to "
                            f"{m['B_max']:.1f} μT, type {m['type']}, {m['N']} sub-specimens used and "
                            f"{m['rejected']} rejected, R² {m['r2']:.3f}, average alteration {m['eps_alt']:.1f} "
                            f"percent, class {m['class']}.")
            if s3_notes.get(site):
                description += " It differs from Table S3: " + "; ".join(s3_notes[site]) + "."
            check = recalculated.loc[site]
            used = [name + pub.MULTISPECIMEN_SUFFIX for name in check["used"]] if check["established"] != "no" else []
            left = ", ".join(name + pub.MULTISPECIMEN_SUFFIX for name in check["left_out"])
            if used and m["rejected"] and check["established"] == "this calculation":
                description += (f" The rejected sub-specimens ({left}) are inferred: leaving them out comes "
                                f"closest to the published values in a plain recalculation (B "
                                f"{check['B_closest']:.2f} μT, R² {check['r2_closest']:.3f}, alteration "
                                f"{check['alteration']:.1f} percent; no alignment correction).")
            elif used and m["rejected"]:
                description += (f" The rejected sub-specimens ({left}) are inferred from the standard "
                                "determination of Table S3, which a recalculation without them reproduces; the "
                                "determination of Table 2 may leave out others.")
            elif not used:
                description += " Which sub-specimens were rejected is not recorded."
            if final["treatment"] == "MS":
                columns.update(int_abs_min=f"{m['B_min'] * 1e-6:.3e}", int_abs_max=f"{m['B_max'] * 1e-6:.3e}",
                               int_n_specimens=int(m["N"]))
                if used:
                    columns["specimens"] = join(used)
                other = group[group["treatment"] == "Coe"]
                if len(other):
                    o = other.iloc[0]
                    description += (f" The single Thellier-Coe determination of this flow ({o['B']:.1f} ± "
                                    f"{o['sigma']:.1f} μT) disagrees with it and the authors place more confidence "
                                    "in the multispecimen result.")
            else:
                description += " In the mean it counts as one sample."
                if used:
                    columns["specimens"] = columns["specimens"] + ":" + join(used)
        if columns.get("specimens"):
            # the Thellier-Coe specimens and multispecimen sub-specimens of the result
            columns["int_n_specimens"] = len(columns["specimens"].split(":"))
        quality = "g"
        if final["class"] == "4":
            quality = "b"
            description += " The authors do not use this flow in the sequence means."
        rows.append(site_row(site, result_quality=quality, method_codes=join(codes), **columns,
                             description=description))
    return rows, pd.DataFrame(checks)


# ---------------------------------------------------------------- the build

def main():
    BUILD_DIR.mkdir(exist_ok=True)
    folders = extract_archives()
    notes = OrderedDict((k, []) for k in ("directions", "thellier", "multispecimen", "rockmag"))

    # ---- directions (.rs3)
    d = build_directions(folders["directions"], notes["directions"])
    meas, spec, samp = d["meas"], d["spec"], d["samp"]
    n_directions = len(meas)
    first_steps = meas.groupby("specimen").head(1)
    nrm_by_flow = first_steps["magn_volume"].astype(float).groupby(
        first_steps["specimen"].map(flow_name)).median()

    # ---- Thellier-Coe (.tdt) and Table 2
    coded, raw_pairs, notes["thellier"] = survey_tdt(folders["thellier"])
    thellier_check = recalculate_thellier(coded)
    thellier_meas = convert_thellier(coded, BUILD_DIR).dropna(axis=1, how="all")
    thellier_spec = thellier_specimen_rows(thellier_meas)
    thellier_spec["sample"] = thellier_spec["specimen"].map(sample_name)
    shared_names = sorted(set(thellier_spec["specimen"].str[:-len(pub.THELLIER_SUFFIX)]) & set(spec["specimen"]))
    thellier_names = {name: name + pub.THELLIER_SUFFIX for name in coded}
    thellier_first = thellier_meas.groupby("specimen").head(1)
    thellier_nrm = thellier_first["magn_volume"].astype(float).groupby(
        thellier_first["specimen"].map(flow_name)).median()

    # ---- multispecimen (.jr6)
    ms_specimens, notes["multispecimen"] = load_multispecimen(folders["multispecimen"])
    ms_meas = ms_measurement_rows(ms_specimens)
    ms_spec = ms_specimen_rows(ms_specimens)
    ms_check = recalculate_multispecimen(ms_specimens)
    ms_standard = recalculate_ms_standard(ms_specimens)
    for r in ms_check[ms_check["established"] != "no"].itertuples():
        rows = ms_spec["specimen"].isin([name + pub.MULTISPECIMEN_SUFFIX for name in r.left_out])
        ms_spec.loc[rows, "description"] += (" Not in the published multispecimen determination of the flow: "
                                             "inferred by recalculation, not flagged in the archived files.")
    pellet_nrm = pd.Series({name: float(np.linalg.norm(sp["vectors"][0])) for name, sp in ms_specimens.items()})
    pellet_nrm = pellet_nrm.groupby(pellet_nrm.index.map(flow_name)).median()

    # ---- rock magnetism (VFTB)
    rock_meas, rock_spec, notes["rockmag"] = convert_vftb(folders["rockmag"], BUILD_DIR)
    sirm = saturation_remanence(rock_meas)
    # the published results (Table S1): hysteresis parameters on the specimen's row, Curie temperatures as rows
    rock_hysteresis, rock_curie = rockmag_specimen_rows()
    rock_spec = rock_spec.merge(rock_hysteresis, on="specimen", how="left")
    rock_spec["description"] = rock_spec["description"] + " " + rock_spec.pop("results")
    rock_check = recalculate_rockmag(rock_meas)
    no_curve = sorted(set(rock_curie["specimen"]) - set(
        rock_meas[rock_meas["method_codes"].str.startswith("LP-IMT")]["specimen"]))
    for specimen in no_curve:
        notes["rockmag"].append(f"{specimen[:-len(pub.ROCKMAG_SUFFIX)]}: Table S1 gives Curie temperatures, but "
                                "the archive has no magnetization-temperature file for it.")
    rock_spec = pd.concat([rock_spec, rock_curie], ignore_index=True)

    # ---- specimens and samples of all experiments
    spec = pd.concat([spec, thellier_spec, ms_spec, rock_spec], ignore_index=True)
    if spec.groupby("specimen")["sample"].nunique().max() > 1:
        raise RuntimeError("a specimen name is used for two samples")
    known = set(samp["sample"])
    new_cores = sorted((set(thellier_spec["sample"]) | set(rock_spec["sample"])) - known,
                       key=lambda x: (flow_number(flow_name(x)), x))
    core_rows = [dict(sample=x, site=flow_name(x), method_codes=pub.ORIENTATION_CODES,
                      description="No orientation in the archived files (no demagnetization file for this core).")
                 for x in new_cores]
    ms_rows = [dict(sample=x, site=flow_name(x), method_codes="FS-FD",
                    description=("The standard sample of this flow that was cut into sub-specimens for the "
                                 "multispecimen experiment; the paper does not say which core it is."))
               for x in sorted(set(ms_spec["sample"]), key=lambda x: flow_number(flow_name(x)))]
    samp = pd.concat([samp, pd.DataFrame(core_rows + ms_rows)], ignore_index=True)
    samp["lat"], samp["lon"] = pub.LAT, pub.LON
    for table in (spec, samp):
        geology(table)
        table["citations"] = "This study"
    spec = spec.sort_values("specimen", kind="stable").reset_index(drop=True)

    # ---- measurements of all experiments
    meas = pd.concat([meas, thellier_meas, ms_meas, rock_meas], ignore_index=True)
    meas["sequence"] = range(1, len(meas) + 1)

    # ---- sites: flow directions (Table 1) and flow paleointensities (Table 3)
    intensity_rows, intensity_check = build_intensity_sites(thellier_names, ms_check)
    sites = pd.DataFrame(d["site_rows"] + intensity_rows)

    # ---- location: the sequence means
    mean = pub.TABLE1_MEAN
    mean_of_vgps = fisher(list(zip(pub.TABLE1["vgp_lon"], pub.TABLE1["vgp_lat"])))
    plon, plat, _, _ = pmag.dia_vgp(mean["dec"], mean["inc"], mean["a95"], pub.LAT, pub.LON)
    d_vgp = float(pmag.angle([mean_of_vgps["dec"], mean_of_vgps["inc"]], [mean["vgp_lon"], mean["vgp_lat"]])[0])
    d_dir = float(pmag.angle([plon, plat], [mean["vgp_lon"], mean["vgp_lat"]])[0])
    pole_code = "DE-VGP" if d_vgp <= d_dir else "DE-DI"
    narrow, wide = pub.SEQUENCE_MEANS
    flow_values = {r["site"]: float(r["int_abs"]) * 1e6 for r in intensity_rows}
    sequence_check = pd.DataFrame([dict(
        classes=s["classes"], N_pub=s["N"], N=len(s["sites"]), B_pub=s["B"],
        B=float(np.mean([flow_values[x] for x in s["sites"]])), sigma_pub=s["sigma"],
        sigma=float(np.std([flow_values[x] for x in s["sites"]], ddof=1)),
        vadm_pub=s["vadm"], vadm=pmag.b_vdm(s["B"] * 1e-6, pub.LAT) / 1e22) for s in pub.SEQUENCE_MEANS])
    locations = pd.DataFrame([OrderedDict(
        location=pub.LOCATION, location_type="Stratigraphic Section",
        result_name="Praia Grande sequence mean", result_type="a", result_quality="g",
        method_codes=f"DE-FM:{pole_code}:DA-DIR-GEO:LP-PI-TRM:LP-PI-MULT", citations="This study",
        geologic_classes=pub.GEOLOGIC_CLASSES, lithologies=pub.LITHOLOGIES,
        country="Cape Verde", continent_ocean="Atlantic Ocean", ocean_sea="Atlantic Ocean",
        plate_blocks="African Plate", tectonic_settings="Volcanic Island",
        lat_s=pub.LAT, lat_n=pub.LAT, lon_w=pub.LON, lon_e=pub.LON,
        age_low=pub.AGE_LOW, age_high=pub.AGE_HIGH, age_unit="Ma",
        dir_tilt_correction=0, dir_dec=mean["dec"], dir_inc=mean["inc"], dir_alpha95=mean["a95"],
        dir_k=mean["k"], dir_n_sites=mean["N"], dir_polarity="n",
        pole_comp_name=pub.CHRM, pole_lat=mean["vgp_lat"], pole_lon=mean["vgp_lon"], pole_n_sites=mean["N"],
        int_abs=f"{wide['B'] * 1e-6:.3e}", int_abs_sigma=f"{wide['sigma'] * 1e-6:.1e}", int_n_sites=wide["N"],
        sites=join(sites["site"].drop_duplicates()),
        description=(
            "Direction: mean of the 11 flow means (Table 1). The authors conclude that the flows were emplaced "
            "within some centuries, so the mean is not taken to average secular variation. Paleointensity: "
            f"mean of the {wide['N']} flow results of classes {wide['classes']} (Table 3; flows "
            f"{', '.join(wide['sites'])}), the value given in the abstract, with a VADM of {wide['vadm']:.1f} × 10²² Am² "
            f"(uncertainty {wide['vadm_sigma']:.1f} × 10²² Am² in Table 3 and 1.0 × 10²² Am² in the text; the "
            f"locations table has no VADM column). The {narrow['N']} flows "
            f"of classes {narrow['classes']} alone give {narrow['B']:.1f} ± {narrow['sigma']:.1f} μT and a VADM of "
            f"({narrow['vadm']:.1f} ± {narrow['vadm_sigma']:.1f}) × 10²² Am². The position is the star marking the "
            "section on the map of Figure 1b, georeferenced from its graticule; the paper gives no coordinates. "
            + pub.UNTILTED))])

    # ---- ages
    ages = pd.DataFrame([
        OrderedDict(location=pub.LOCATION, site="PRG1", age=pub.AGE, age_sigma=pub.AGE_2SIGMA / 2, age_unit="Ma",
                    method_codes="GM-KAR", citations="This study",
                    description=pub.K_AR + "; entered with one sigma."),
        OrderedDict(location=pub.LOCATION, age_low=pub.AGE_LOW, age_high=pub.AGE_HIGH, age_unit="Ma",
                    timescale_stage="Messinian", method_codes="GM-KAR:GM-PMAG-POL", citations="This study",
                    description=("K-Ar age of flow PRG1 combined with the normal polarity of all flows: "
                                 "subchron C3An.1n in the timescale of Gradstein et al. (2004)."))]).astype(object)

    # ---- selection criteria (Tables 2 and 3)
    criteria = [OrderedDict(
        criterion="IE-SPEC", table_column=column, criterion_operation=operation, criterion_value=c2,
        citations="This study",
        description=(f"Thellier-Coe determinations, {name}: class C2, the threshold for acceptance (Table 2); "
                     f"class C1 requires {operation} {c1:g}."))
        for name, column, operation, c1, c2 in pub.THELLIER_CRITERIA]
    criteria.append(OrderedDict(
        criterion="IE-SITE", table_column="sites.int_abs_sigma_perc", criterion_operation="<=",
        criterion_value=pub.FLOW_MEAN_SIGMA_PERCENT, citations="This study",
        description=(f"Flow means: standard deviation at most {pub.FLOW_MEAN_SIGMA_PERCENT} percent of the mean, "
                     f"or at most {pub.FLOW_MEAN_SIGMA_MICROTESLA} μT (Table 3).")))
    criteria.append(OrderedDict(
        criterion="IE-SITE", table_column="sites.int_n_specimens", criterion_operation=">=", criterion_value=5,
        citations="This study",
        description="Multispecimen determinations (Table 2): " + pub.MULTISPECIMEN_CRITERIA + "."))
    criteria = pd.DataFrame(criteria)

    # ---- assemble, validate, write
    for table in (locations, sites, criteria):
        whole_numbers(table)
    tables = OrderedDict(locations=locations, sites=sites, samples=samp, specimens=spec, measurements=meas,
                         ages=ages, criteria=criteria)
    dm, vocab, codes = load_resources()
    problems = validate(tables, dm, vocab, codes)
    write_upload_file(tables, STUDY_DIR / "magic_contribution.txt")

    # ================================================================ report
    n_remade = int(spec["description"].fillna("").str.startswith("Not stored").sum())
    n_fit_rows = int(spec["dir_comp"].notna().sum()) - n_remade
    rep = ["# Praia Grande: build report\n",
           "Written by `convert.py`; do not edit. Study: Calvo Rathert et al. (2022), "
           f"doi:{pub.PAPER_DOI}; data doi:{pub.DATA_DOI}. `README.md` explains the sources and the decisions.\n",
           "## Contents of the contribution\n",
           "| Table | Rows | Source |", "| --- | --- | --- |",
           f"| measurements | {len(meas)}: {n_directions} demagnetization steps (`.rs3`), {len(thellier_meas)} "
           f"Thellier-Coe steps (`.tdt`), {len(ms_meas)} multispecimen steps (`.jr6`), {len(rock_meas)} "
           "rock-magnetic points (VFTB) | files |",
           f"| specimens | {len(spec)} rows for {spec['specimen'].nunique()} specimens: "
           f"{spec['specimen'].nunique() - len(thellier_spec) - len(ms_spec) - rock_spec['specimen'].nunique()} demagnetized "
           f"({n_fit_rows} rows of stored fits in specimen and geographic coordinates, {n_remade} rows of a fit "
           f"recalculated here), {len(thellier_spec)} Thellier ({int(thellier_spec['int_abs'].notna().sum())} with a "
           f"determination), {len(ms_spec)} multispecimen, {rock_spec['specimen'].nunique()} rock-magnetic "
           f"({len(rock_curie)} rows of Curie temperatures) | files; table (Tables 2 and S1); inferred (use in "
           "the flow means) |",
           f"| samples | {len(samp)}: {len(known)} cores with a demagnetization file, {len(new_cores)} cores "
           f"without, {len(ms_rows)} multispecimen samples | files (orientation); text (method) |",
           f"| sites | {len(sites)}: {len(d['site_rows'])} flow directions, {len(intensity_rows)} flow "
           "paleointensities | table (Tables 1 to 3); text (age, lithology); figure (position) |",
           f"| locations | {len(locations)} | table (Tables 1 and 3); text; figure |",
           f"| ages | {len(ages)} | text |",
           f"| criteria | {len(criteria)} | table (Tables 2 and 3) |", ""]
    rep.append("## Validation against the MagIC data model\n")
    rep.append("No problems.\n" if not problems else "\n".join(f"- {p}" for p in problems) + "\n")
    rep.append("## Uploading to MagIC\n")
    rep.append("`magic_contribution.txt` holds every table except the contribution table, which is made on MagIC "
               "when the file is uploaded (the file is written with `ipmag.upload_magic`). Enter there:\n")
    rep.append("\n".join([
        f"- Reference: {pub.PAPER_DOI}",
        "- Laboratories: " + "; ".join(pub.LABORATORIES.split(":")),
        f"- Description: {pub.CONTRIBUTION_DESCRIPTION}"]) + "\n")

    # ---- directions
    stored = d["stored"]
    rep.append("## Directions\n")
    rep.append(f"The demagnetization files hold {len(stored)} stored line fits. Re-made from the measurements "
               f"between their stated limits, with the line type the file flags (OA = anchored), "
               f"{(stored['diff_stated'] <= REMADE).sum()} agree with the stored direction within "
               f"{REMADE}° (largest MAD difference "
               f"{stored[stored['diff_stated'] <= REMADE]['mad_diff_stated'].abs().max():.2f}°).\n")
    rep.append("Flow means recalculated from the contribution: Fisher mean of the characteristic fits flagged "
               "good, at the level given, against Table 1. `vgp_diff` is the angle between the published VGP "
               f"and the VGP of the published mean direction at {pub.LAT}°N, {pub.LON:.3f}°E.\n")
    rep.append(md_table(d["checks"], ["site", "level", "N_pub", "N", "dec", "inc", "k", "a95", "dec_pub",
                                      "inc_pub", "k_pub", "a95_pub", "angle", "reproduced", "left_out",
                                      "vgp_diff"],
                        {"k": ".0f", "k_pub": ".0f", "angle": ".2f", "vgp_diff": ".2f"}))
    rep.append(f"\nSequence-mean VGP: published {mean['vgp_lat']}°N, {mean['vgp_lon']}°E; the Fisher mean of the "
               f"11 published VGPs is {d_vgp:.2f}° from it and the VGP of the mean direction {d_dir:.2f}°, so "
               f"the pole is coded {pole_code}.\n")
    rep.append("\n".join(f"- {n}" for n in notes["directions"]) + "\n")

    # ---- Thellier
    rep.append("## Thellier-Coe files\n")
    identical = raw_pairs[raw_pairs["moment_ratio"].round(3) == 1]
    scaled = raw_pairs[raw_pairs["moment_ratio"].round(3) != 1]
    extra = raw_pairs[raw_pairs["rows_not_in_coded"] != ""]
    rep.append(f"The archive holds {len(coded) + len(raw_pairs)} `.tdt` files. {len(coded)} carry ThellierTool "
               "step codes (T.00 zero field, T.11 in field, T.12 pTRM check) and are the 66 specimens of the "
               f"paper. The other {len(raw_pairs)} carry the steps as labeled at measurement (125C, 126C, ...) "
               "and specimen names that count up row by row. Each matches one "
               f"of the 66 on its measured directions: {len(identical)} with identical moments"
               + (", " + "; ".join(f"{r.raw_file} with the moments of {r.coded_specimen} multiplied by "
                                   f"{1 / r.moment_ratio:.2f}" for r in scaled.itertuples()) if len(scaled) else "")
               + f". {len(extra)} of them hold one or two rows that the coded file does not. They are not "
               "converted.\n")
    rep.append(md_table(raw_pairs.rename(columns={"raw_file": "file", "coded_specimen": "same data as"}),
                        ["file", "name_column", "rows", "same data as", "same_directions", "moment_ratio",
                         "rows_not_in_coded"], {"moment_ratio": ".2f"}))
    rep.append("\nIn the 66 converted files:\n")
    rep.append("\n".join(f"- {n}" for n in notes["thellier"]))
    rep.append(f"- The Thellier specimens are fragments in 10 mm vials, distinct from the demagnetized specimens, "
               f"but {len(shared_names)} of them were published under the name of a demagnetized specimen of the "
               f"same core ({', '.join(shared_names)}). Every Thellier specimen is entered with the suffix "
               f"`{pub.THELLIER_SUFFIX}` (PRG1-2A becomes PRG1-2A{pub.THELLIER_SUFFIX}), and its description gives "
               "the published name.")
    rep.append("- The specimen directions are in the coordinates of the unoriented fragment.\n")
    rep.append("Published determinations recalculated: best-fit line on the Arai plot (Coe et al., 1978) over "
               "the published range, from the converted measurements, against Table 2. d(CK), k', MAD and α are "
               "entered as published and are not recalculated.\n")
    rep.append(md_table(thellier_check, ["specimen", "range", "N_pub", "N", "B_pub", "B", "B_sigma_pub", "B_sigma",
                                         "beta_pub", "beta", "f_pub", "f", "q_pub", "q", "agrees"],
                        {"B": ".2f", "B_sigma": ".2f", "beta_pub": ".3f", "beta": ".3f", "f": ".2f",
                         "f_pub": ".2f", "q": ".1f"}))
    off = thellier_check[thellier_check["agrees"] != "yes"]
    rep.append(f"\n{(thellier_check['agrees'] != 'no').sum()} of {len(thellier_check)} determinations recalculate "
               "in N, B, its standard error, f and q. "
               + (f"For {', '.join(off['specimen'])} the recalculated σ/slope is the value that follows from "
                  "the published B, standard error and q. " if len(off) else "")
               + "A published range that starts at 20 °C is reproduced only when the unheated point is left out "
                 "of the fit, so N counts heating steps.\n")

    # ---- multispecimen
    rep.append("## Multispecimen files\n")
    rep.append(f"Five JR6 files (M0 to M4), one per step of the protocol, each with {len(ms_specimens)} rows: "
               "seven sub-specimens per flow, in fields of 10 to 70 μT. The paper speaks of eight sub-specimens "
               "per sample (88 in total). The step label of a row is the field (A10 = 10 μT); a JR6 reader "
               "takes it for an alternating field in mT, so the rows are read directly here.\n")
    rep.append("\n".join(f"- {n}" for n in notes["multispecimen"]))
    rep.append(f"- The sub-specimens are named like cores (PRG1-1 is sub-specimen 1 of flow PRG1, not core 1). "
               f"They are entered with the suffix `{pub.MULTISPECIMEN_SUFFIX}`, in a sample `<flow>-MS`.")
    rep.append("- The heating temperature (400 or 450 °C) is not given per flow, so `treat_temp` is empty and "
               "the description says so. The moments are in A/m of pellet (`magn_volume`).\n")
    rep.append("Standard determinations of Table S3 (MSP-DB) recalculated: (m1 − m0)/m0 from the moduli, "
               "regressed on the field, zero crossing in μT; `alteration` is the mean of (m4 − m1)/m1 in "
               "percent. Where Table S3 rejects sub-specimens, the N that come closest to its value are used and "
               "`left_out` names the others.\n")
    shown = ms_standard.assign(left_out=ms_standard["left_out"].map(lambda names: ", ".join(names)))
    rep.append(md_table(shown, ["site", "N_pub", "B_pub", "B", "r2_pub", "r2", "alteration_pub", "alteration",
                                "left_out", "agrees"], {"r2_pub": ".3f", "r2": ".3f"}))
    rep.append(f"\n{(ms_standard['agrees'] == 'yes').sum()} of {len(ms_standard)} agree in B (0.15 μT), R² "
               "(0.002) and alteration (0.7 percent).\n")
    rep.append("Determinations selected by the authors (Table 2) against a plain calculation of the selected "
               "protocol (`db` as above; `fc`: 2(m1 − m0)/(2m0 − m1 − m2) along the NRM), with all seven "
               "sub-specimens (`B_all`) and with the N that come closest to the published value (`B_closest`). "
               "This is not the authors' calculation (no alignment correction, no bootstrap bounds), and the "
               "published values are what is entered. `established` says whether the rejected sub-specimens "
               "(`left_out`) are identified: by this calculation reproducing B, R² and alteration, or by the "
               "standard determination of Table S3 with the same number rejected.\n")
    shown = ms_check.assign(left_out=ms_check["left_out"].map(lambda names: ", ".join(names)))
    rep.append(md_table(shown, ["site", "type", "ratio", "N_pub", "B_pub", "B_all", "B_closest", "r2_pub",
                                "r2_closest", "alteration_pub", "alteration", "left_out", "established"],
                        {"r2_pub": ".3f", "r2_closest": ".3f"}))
    differences = pub.TABLE2_MULTISPECIMEN.merge(pub.TABLE_S3, on=["site", "type"], suffixes=("_t2", "_s3"))
    differing = ["{} {}: {} {:g} in Table 2, {:g} in Table S3".format(r["site"], r["type"], c, r[c + "_t2"], r[c + "_s3"])
                 for _, r in differences.iterrows() for c in ("B", "B_min", "B_max", "N", "rejected", "eps_alt", "r2")
                 if r[c + "_t2"] != r[c + "_s3"]]
    rep.append("\nTable 2 against the rows of Table S3 for the same protocols: "
               + ("; ".join(differing) if differing else "identical") + ".\n")

    # ---- flow means
    rep.append("## Flow and sequence paleointensities (Table 3)\n")
    rep.append("Every Thellier-Coe and combined row of Table 3 against the mean and standard deviation of the "
               "Table 2 values (a multispecimen result counts as one value):\n")
    rep.append(md_table(intensity_check, ["site", "treatment", "N_pub", "N", "B_pub", "B", "sigma_pub", "sigma",
                                          "percent_pub", "percent"], {"B": ".2f", "sigma": ".2f"}))
    rep.append("\nFor a single determination `sigma` is its standard error. Sequence means against the flow "
               "values entered, and the VADM of the published mean at the latitude used:\n")
    rep.append(md_table(sequence_check, ["classes", "N_pub", "N", "B_pub", "B", "sigma_pub", "sigma", "vadm_pub",
                                         "vadm"], {"B": ".2f", "sigma": ".2f", "vadm": ".2f"}))
    rep.append("")

    # ---- rock magnetism
    rep.append("## Rock-magnetic files\n")
    counts = rock_meas.groupby(rock_meas["method_codes"].str.split(":").str[0]).agg(
        specimens=("specimen", "nunique"), points=("specimen", "size"))
    rep.append(f"{rock_spec['specimen'].nunique()} powders, one per flow, converted with the PmagPy VFTB "
               "converter: " + "; ".join(f"{code} {r.specimens} curves, {r.points} points"
                                          for code, r in counts.iterrows())
               + f". Each specimen is entered with the suffix `{pub.ROCKMAG_SUFFIX}` in the sample named by the "
               "file (PRG1-2.irm is a powder of core PRG1-2), with the weight given in the file.\n")
    rep.append("The results of Table S1 are entered on the specimen rows (hysteresis parameters, S ratio) and as "
               "one row per Curie temperature. A simple recalculation from the archived curves, against Table "
               "S1 with its Mrs and Ms multiplied by 1000 (`_pub`; Am²/kg, mT): `sirm_irm` largest IRM, "
               "`sirm_back` first point of the back-field curve, `mrs_loop`, `ms` and `bc` from the loop after "
               "removing the high-field slope, `bcr` zero crossing of the back-field curve, `s_ratio` from the "
               "back-field curve at 0.3 T.\n")
    rep.append(md_table(rock_check, ["sample", "mrs_pub", "sirm_irm", "sirm_back", "mrs_loop", "ms_pub", "ms",
                                     "bc_pub", "bc", "bcr_pub", "bcr", "s_pub", "s_ratio"],
                        {c: ".3f" for c in ("mrs_pub", "sirm_irm", "sirm_back", "mrs_loop", "ms_pub", "ms")}
                        | {"s_pub": ".2f", "s_ratio": ".2f"}))
    ratio_ms = rock_check["ms"] / rock_check["ms_pub"]
    ratio_mrs = rock_check["sirm_irm"] / rock_check["mrs_pub"]
    ratio_bc = rock_check["bc"] / rock_check["bc_pub"]
    ratio_bcr = rock_check["bcr"] / rock_check["bcr_pub"]
    rep.append(f"\nRecalculated over published: Ms {ratio_ms.min():.3f} to {ratio_ms.max():.3f}; saturation "
               f"remanence {ratio_mrs.min():.3f} to {ratio_mrs.max():.3f}; Bc {ratio_bc.min():.2f} to "
               f"{ratio_bc.max():.2f}; Bcr {ratio_bcr.min():.2f} to {ratio_bcr.max():.2f} (the largest is "
               f"{rock_check.loc[ratio_bcr.idxmax(), 'sample']}); S ratio within "
               f"{(rock_check['s_ratio'] - rock_check['s_pub']).abs().max():.3f}. The agreement of Ms fixes the factor "
               "of 1000 between Table S1 and the archived curves in emu/g. The Curie temperatures were not "
               "recalculated; on the archived curves the magnetization falls fastest 20 to 30 °C lower on "
               "cooling than on heating, so the higher column of Table S1 (H) is entered as the heating "
               "branch, as in the text of the paper.\n")
    rep.append("\n".join(f"- {n}" for n in notes["rockmag"]) + "\n")

    # ---- units
    units = pd.DataFrame([dict(flow=flow_name(k), rs3=nrm_by_flow[flow_name(k)],
                               tdt=thellier_nrm[flow_name(k)], sirm=v,
                               rem=100 * nrm_by_flow[flow_name(k)] / (v * pub.DENSITY),
                               pellets=8 * pellet_nrm[flow_name(k)],
                               as_mass=nrm_by_flow[flow_name(k)] / pub.EMU_PER_CM3_TO_A_PER_M * pub.DENSITY)
                          for k, v in sorted(sirm.items(),
                                             key=lambda kv: flow_number(flow_name(kv[0])))])
    file_min, file_max = (nrm_by_flow.min() / pub.EMU_PER_CM3_TO_A_PER_M,
                          nrm_by_flow.max() / pub.EMU_PER_CM3_TO_A_PER_M)
    rep.append("## Units of the moments\n")
    rep.append("The demagnetization files give the moments in a column labeled A/m, with NRMs of "
               f"{file_min:.1e} to {file_max:.1e} (flow medians); the Thellier files give no unit and have the "
               "same values flow by flow. Both are entered as volume-normalized magnetization (`magn_volume`) "
               f"after multiplying by {pub.EMU_PER_CM3_TO_A_PER_M:g}, that is, reading the numbers as emu/cm³:\n")
    rep.append("\n".join([
        "- emu/cm³ is the volume-normalized unit of the 2G magnetometer software, and 1 emu/cm³ is 1000 A/m.",
        "- The rock-magnetic table of the same study (Table S1) is related to its archived curves by the same "
        "factor of 1000 (section above).",
        f"- The NRMs become {nrm_by_flow.min():.2f} to {nrm_by_flow.max():.2f} A/m (`rs3`), "
        f"{units['rem'].min():.2f} to {units['rem'].max():.2f} percent of the saturation remanence of the IRM "
        f"curves at {pub.DENSITY:.0f} kg/m³ (`rem`). The multispecimen pellets, measured on a JR6 and scaled "
        "from one eighth of a core to a whole one, give values of the same order (`pellets`).",
        f"- If the numbers were per gram instead (emu/g), the NRMs would be {pub.DENSITY / 1000:.1f} times "
        "higher (`as_mass`). The comparisons do not separate the two readings, so the magnetization is known "
        "to about that factor.",
        "- The paleointensities and directions do not depend on the unit. The multispecimen moments are JR6 "
        "values in A/m of pellet, and the rock-magnetic curves are in emu/g in the files.",
        "- `build/converted_directions/` and `build/converted_thellier/` hold the converter output with the "
        "values as in the files."]) + "\n")
    rep.append(md_table(units, ["flow", "rs3", "tdt", "sirm", "rem", "pellets", "as_mass"],
                        {"rs3": ".2f", "tdt": ".2f", "sirm": ".3f", "rem": ".2f", "pellets": ".1f",
                         "as_mass": ".1f"}))
    rep.append("\n`rs3`, `tdt`: median NRM of the demagnetization and Thellier specimens as entered (A/m). "
               "`sirm`: largest IRM of the flow's `.irm` file (Am²/kg). `rem`: NRM as a percentage of it. "
               "`pellets`: eight times the median JR6 NRM of the flow's multispecimen pellets (A/m). `as_mass`: "
               "the NRM in A/m if the file values were emu/g.\n")

    # ---- gaps
    rep.append("## Information that would complete the contribution\n")
    rep.append("\n".join([
        "- The coordinates of each flow (now one position for all 11, georeferenced from the star of Figure 1b).",
        "- Bedding, if any applies (the flows are taken as untilted).",
        "- The compass used for each core and any declination correction (all cores carry SO-SUN:SO-MAG).",
        "- The unit of the moments in the demagnetization and Thellier files, and specimen volumes or masses.",
        "- The stratigraphic height of each flow (the order, PRG1 at the base, is entered).",
        "- The multispecimen heating temperature of each flow and the core used."]) + "\n")
    (STUDY_DIR / "report.md").write_text("\n".join(rep) + "\n")
    print(f"{len(problems)} validation problems")
    for p in problems[:40]:
        print("  ", p)
    print("wrote", STUDY_DIR / "magic_contribution.txt")
    print({name: len(table) for name, table in tables.items()})


if __name__ == "__main__":
    main()
