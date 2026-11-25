"""Build the MagIC contribution for the La Garrotxa lava flows (Vernet et al., 2026).

Inputs: the archive of the Zenodo record (data/), unmodified, and the values
transcribed from the paper (published.py). report.md gives the source of each
part of the contribution:

    files      the archived laboratory files, read with PmagPy converters
    table      Tables 1 to 4 of the paper and Tables I to IV of its appendix (table_iii.csv and
               table_iv.csv, made from the PDF by extract_tables.py)
    text       lithology, laboratories, sampling, methods
    inferred   from recalculation, where neither the files nor the paper give it

Outputs, next to this script:
    magic_contribution.txt   the contribution
    report.md                contents, checks against the paper, and what is missing
    study.json               its "build" entry (common.studies.write_build_summary)
    build/                   extracted archive and converter output (not kept in the repository)

Sections:
    reading                  convert_2_magic.rs3 (all 134 specimens) and convert_2_magic._2g_bin
                             (the 99 GTX specimens); the two compared
    the stored fits          recalculated from the measurements (pmag.domean), and compared with Table I
    Thellier-Coe (.TDT)      convert_2_magic.tdt; the corrected copies; Table III recalculated
                             (pmag.sortarai, pmag.PintPars), Tables 2 and 4 from it, VADMs (pmag.b_vdm)
    VFTB                     convert_2_magic.vftb; rock-magnetic parameters for the report (rockmag);
                             Table IV recalculated
    site means and VGPs      hierarchical means of pmag.fisher_mean, against Tables 2 and 3 (pmag.dia_vgp)
    the contribution         samples, sites, locations, ages, criteria; validation; report.md

Usage:
    python convert.py

Requires numpy, pandas and PmagPy master with the branches listed in README.md ("PmagPy").
"""

import contextlib
import io
import re
import shutil
import sys
import warnings
import zipfile
from collections import OrderedDict, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from pmagpy import convert_2_magic
from pmagpy import ipmag
from pmagpy import pmag
from pmagpy import rockmag

import published as pub

STUDY_DIR = Path(__file__).resolve().parent
REPO_DIR = STUDY_DIR.parents[1]
sys.path.insert(0, str(REPO_DIR))
from common.magic_tools import md_table, validate_upload_file, whole_numbers, write_upload_file  # noqa: E402
from common.studies import write_build_summary  # noqa: E402

DATA_DIR = STUDY_DIR / "data"
BUILD_DIR = STUDY_DIR / "build"
ARCHIVE = "LA GARROTXA_rev1.zip"
DIRECTIONS_FOLDER = "LA GARROTXA/PALEOMAGNETIC DIRECTIONS"

REPRODUCED = 0.15  # degrees: a recalculated direction agrees with a stored or published one
MAD_TOLERANCE = 0.11  # degrees: MADs are printed to 0.1°


# ---------------------------------------------------------------- names and directions

def site_of(name):
    """The site (lava flow) of a specimen or sample name: GTX0101B -> GTX01, OL01-2B -> OL01, LTD_OL0106Bt -> OL01."""
    return re.match(r"(?:LTD_)?(GTX\d\d|OL\d\d)", name).group(1)


def core_of(specimen):
    """The core a specimen was cut from: GTX0202A -> GTX0202, GTX080102A -> GTX08010, OL01-2B -> OL01-2."""
    return specimen[:-1]


def block_of(specimen):
    """The hand block of a specimen of GTX08 or GTX10: GTX080102A -> GTX0801."""
    return specimen[:7]


def mean_unit(specimen):
    """The unit averaged first in a site mean: the block for GTX08 and GTX10, otherwise the core."""
    return block_of(specimen) if site_of(specimen) in pub.BLOCK_SITES else core_of(specimen)


def table_i_name(specimen):
    """The name in Table I: OL01-2B -> OL0102B; GTX names are the same."""
    m = re.fullmatch(r"(OL\d\d)-(\d+)([A-Z])", specimen)
    return f"{m.group(1)}{int(m.group(2)):02d}{m.group(3)}" if m else specimen


def angle(d1, i1, d2, i2):
    """Angle in degrees between two directions."""
    return float(pmag.angle([d1, i1], [d2, i2])[0])


def fisher(directions):
    """Fisher mean of a list of (dec, inc)."""
    if len(directions) == 1:
        return dict(dec=directions[0][0], inc=directions[0][1], n=1, k=np.nan, alpha95=np.nan)
    return pmag.fisher_mean([[d, i] for d, i in directions])


LINE_CODES = OrderedDict([("free", "DE-BFL"), ("anchored", "DE-BFL-A"), ("origin", "DE-BFL-O")])


def fit_line(block, rows, mode):
    """Principal component line (Kirschvink, 1980) through some steps of a specimen, with pmag.domean:
    dec, inc and MAD.

    Args:
        block: the steps of the specimen, as rows [step, dec, inc, moment, 1, "g"] (specimen_vectors).
        rows: the indices of the steps in the fit, in order.
        mode: "free" (DE-BFL), "anchored" (DE-BFL-A, through the origin) or "origin" (DE-BFL-O, the
            origin added as a point).
    """
    data = [list(block[k]) for k in rows]
    fit = pmag.domean(data, 0, len(data) - 1, LINE_CODES[mode])
    return float(fit["specimen_dec"]), float(fit["specimen_inc"]), float(fit["specimen_mad"])


def join(names):
    return ":".join(names)


def append(df, rows, text):
    """Append a sentence to the description of the given rows."""
    old = df.loc[rows, "description"].fillna("")
    df.loc[rows, "description"] = np.where(old == "", text, old + " " + text)


# ================================================================ reading

def extract_archive():
    """Unzip the archive into build/extracted and return the folder of the direction files (its parent is
    the folder of the archive)."""
    target = BUILD_DIR / "extracted"
    if target.exists():
        shutil.rmtree(target)
    with zipfile.ZipFile(DATA_DIR / ARCHIVE) as archive:
        archive.extractall(target)
    return target / DIRECTIONS_FOLDER


def gather(folder, suffix, name):
    """Copy the files with a suffix from the site folders into one folder (the converters read one folder)."""
    target = BUILD_DIR / name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for path in sorted(folder.rglob(f"*{suffix}")):
        shutil.copy(path, target / path.name)
    return target


def read_table(path):
    return pd.read_csv(path, sep="\t", skiprows=1)


def convert_rs3(folder):
    """Convert the .rs3 files with PmagPy; return the tables and the converter's warnings."""
    out = BUILD_DIR / "rs3"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        ok, message = convert_2_magic.rs3(input_dir_path=str(folder), dir_path=str(out), specname=True,
                                          m_rows=pub.OL_STEP_TYPE, location=pub.LOCATION)
    if not ok:
        raise RuntimeError(f"convert_2_magic.rs3: {message}")
    warnings = [line for line in log.getvalue().splitlines() if line.startswith("-W-")]
    return {t: read_table(out / f"{t}.txt") for t in ("measurements", "specimens", "samples")}, warnings


def convert_2g(folder):
    """Convert each 2G binary file with PmagPy (one file per call); return measurements and samples."""
    meas, samples, warnings = [], [], []
    for path in sorted(folder.glob("*.dat")):
        out = BUILD_DIR / "2g" / path.stem
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            ok, message = convert_2_magic._2g_bin(dir_path=str(out), mag_file=str(path), specname=True,
                                                  location=pub.LOCATION)
        if not ok:
            raise RuntimeError(f"convert_2_magic._2g_bin, {path.name}: {message}")
        warnings += [f"{path.name}: {line}" for line in log.getvalue().splitlines() if line.startswith("-W-")]
        meas.append(read_table(out / "measurements.txt"))
        samples.append(read_table(out / "samples.txt").assign(specimen=path.stem))
    return pd.concat(meas, ignore_index=True), pd.concat(samples, ignore_index=True), warnings


def read_rs3_raw(folder):
    """The header, steps and fits of each .rs3 file, with the reader of the PmagPy converter."""
    return {path.stem: convert_2_magic._rs3_read_file(str(path)) for path in sorted(folder.glob("*.rs3"))}


def step_values(meas):
    """Step of each measurement row in the units of the specimens table (K or T; 0 for the NRM)."""
    af = meas["method_codes"].str.contains("LT-AF")
    nrm = meas["method_codes"].str.contains("LT-NO")
    values = np.where(af, meas["treat_ac_field"], meas["treat_temp"])
    values = np.where(nrm, 0.0, values)
    units = np.where(af, "T", np.where(nrm, "", "K"))
    return pd.Series(values, index=meas.index), pd.Series(units, index=meas.index)


def compare_2g_rs3(meas_2g, samples_2g, raw):
    """Compare the steps, directions, moments and orientation of the two kinds of files."""
    rows = []
    for specimen, g in meas_2g.groupby("specimen", sort=True):
        head, steps, _ = raw[specimen]
        labels_2g = [(round(v, 4), u) for v, u in zip(*step_values(g))]
        labels_rs3 = []
        for s in steps:
            if s["ID"] == "N":
                labels_rs3.append((0.0, ""))
            elif s["ID"] == "A":
                labels_rs3.append((round(float(s["Step"]) * 1e-3, 4), "T"))
            else:
                labels_rs3.append((round(float(s["Step"]) + 273, 4), "K"))
        common = [k for k in range(min(len(g), len(steps))) if labels_2g[k] == labels_rs3[k]]
        same_steps = labels_2g == labels_rs3
        extra = sorted(set(labels_2g) - set(labels_rs3)) if not same_steps else []
        repeats = len(labels_2g) - len(set(labels_2g))
        d_angle = max(angle(g["dir_dec"].iloc[k], g["dir_inc"].iloc[k], steps[k]["Dsp"], steps[k]["Isp"])
                      for k in common) if same_steps else np.nan
        moment = g["magn_moment"].to_numpy() / (g["magn_volume"].to_numpy() if "magn_volume" in g else 1)
        ratio = (np.max(np.abs(g["magn_volume"].to_numpy() / np.array([float(s["M"]) for s in steps]) - 1))
                 if same_steps else np.nan)
        s2 = samples_2g[samples_2g["specimen"] == specimen].iloc[0]
        rows.append(dict(specimen=specimen, steps_2g=len(g), steps_rs3=len(steps), same_steps=same_steps,
                         repeats=repeats, extra=extra, max_angle=d_angle, max_moment_ratio=ratio,
                         azimuth_2g=s2["azimuth"], dip_2g=s2["dip"], sdec=float(head["SDec"]),
                         sinc=float(head["SInc"])))
    return pd.DataFrame(rows)


# ================================================================ the stored fits

def specimen_vectors(meas, specimen):
    """Measurement rows of a specimen in order, and their steps as the data block of pmag.domean.

    Returns:
        (m, block, values, units): the rows; [step number, dec, inc, moment, 1, "g"] for each
        (specimen coordinates); the step of each row and its unit (step_values).
    """
    m = meas[meas["specimen"] == specimen].reset_index(drop=True)
    size = m["magn_volume"] if "magn_volume" in m and m["magn_volume"].notna().all() else m["magn_moment"]
    block = [[k, float(d), float(i), float(s), 1, "g"] for k, (d, i, s) in enumerate(zip(m["dir_dec"], m["dir_inc"],
                                                                                          size))]
    values, units = step_values(m)
    return m, block, values, units


def limit_rows(values, units, low, high, unit):
    """First row at the lower limit and last row at the upper limit (0 for the NRM)."""
    first = [k for k in range(len(values)) if np.isclose(values[k], low) and (units[k] == unit or low == 0)]
    last = [k for k in range(len(values)) if np.isclose(values[k], high) and units[k] == unit]
    if not first or not last:
        return None
    return first[0], last[-1]


def refit_stored(spec, meas):
    """Recalculate each stored line from the measurements between its limits.

    Each fit is recalculated as a free line, a line anchored to the origin and
    a line with the origin added as a point, and the calculation that gives the
    stored direction (within REPRODUCED) and MAD (within MAD_TOLERANCE) is
    recorded. When none does over the stated limits, a range that starts at an
    earlier step is tried (a heating step before alternating field steps, as in
    one Praia Grande file).
    """
    rows = []
    for r in spec[spec["dir_tilt_correction"] == -1].itertuples():
        if "DE-BFP" in r.method_codes:
            continue
        m, block, values, units = specimen_vectors(meas, r.specimen)
        limits = limit_rows(values, units, r.meas_step_min, r.meas_step_max, r.meas_step_unit)
        stored_mad = r.dir_mad_anc if pd.notna(r.dir_mad_anc) else r.dir_mad_free
        row = dict(specimen=r.specimen, dir_comp=r.dir_comp, method_codes=r.method_codes,
                   stored_dec=r.dir_dec, stored_inc=r.dir_inc, stored_mad=stored_mad, n_rs3=r.dir_n_measurements,
                   calculation="", first=None, last=None, n=np.nan, angle=np.nan, mad=np.nan, earlier_start=False,
                   left_out="")
        if limits is None:
            rows.append(dict(row, calculation="limits not found"))
            continue
        a, b = limits
        best = None
        for start in [a] + list(range(a - 1, -1, -1)):
            for mode in ("free", "anchored", "origin"):
                dec, inc, mad = fit_line(block, range(start, b + 1), mode)
                ang = angle(dec, inc, r.dir_dec, r.dir_inc)
                if best is None or ang < best[1]:
                    best = (mode, ang, mad, start)
                if ang <= REPRODUCED and abs(mad - stored_mad) <= MAD_TOLERANCE:
                    break
            else:
                continue
            break
        mode, ang, mad, start = best
        good = ang <= REPRODUCED and abs(mad - stored_mad) <= MAD_TOLERANCE
        left_out = ""
        if not good:
            # a step measured twice (the 2G file keeps both): the fit may hold only one of the two
            labels = list(zip(values.round(6), units))
            for k in range(a, b + 1):
                if labels.count(labels[k]) < 2:
                    continue
                keep = [j for j in range(a, b + 1) if j != k]
                for mode_ in ("free", "anchored", "origin"):
                    dec, inc, mad_ = fit_line(block, keep, mode_)
                    ang_ = angle(dec, inc, r.dir_dec, r.dir_inc)
                    if ang_ <= REPRODUCED and abs(mad_ - stored_mad) <= MAD_TOLERANCE:
                        good, mode, ang, mad, start = True, mode_, ang_, mad_, a
                        left_out = (f"{m['treat_temp'][k] - 273:.0f} °C" if units[k] == "K"
                                    else f"{m['treat_ac_field'][k] * 1e3:g} mT")
                        left_out += " (first)" if labels.index(labels[k]) == k else " (second)"
                        break
                if left_out:
                    break
        rows.append(dict(row, calculation=mode if good else "not reproduced", first=start, last=b,
                         n=b - start + 1 - bool(left_out), angle=ang, mad=mad, earlier_start=good and start != a,
                         left_out=left_out,
                         first_step=f"{m['treat_temp'][start] - 273:.0f} °C" if units[start] == "K" else (
                             f"{m['treat_ac_field'][start] * 1e3:g} mT" if units[start] == "T" else "NRM")))
    return pd.DataFrame(rows)


def chrm_rows(spec_geo):
    """For each specimen of Table I, the stored geographic fit closest to the Table I direction."""
    rows = []
    for t in pub.TABLE_I.itertuples():
        fits = spec_geo[spec_geo["specimen"].map(table_i_name) == t.specimen]
        if fits.empty:
            raise RuntimeError(f"Table I specimen {t.specimen} has no stored fit")
        angles = [angle(f.dir_dec, f.dir_inc, t.dec, t.inc) for f in fits.itertuples()]
        k = int(np.argmin(angles))
        rows.append(dict(table_i=t.specimen, specimen=fits["specimen"].iloc[k], dir_comp=fits["dir_comp"].iloc[k],
                         index=fits.index[k], angle=angles[k]))
    return pd.DataFrame(rows)


def compare_table_i(spec_geo, chrm, refits):
    """The stored characteristic fit of each specimen against its row of Table I."""
    rows = []
    for c in chrm.itertuples():
        t = pub.TABLE_I[pub.TABLE_I["specimen"] == c.table_i].iloc[0]
        f = spec_geo.loc[c.index]
        rf = refits[(refits["specimen"] == c.specimen) & (refits["dir_comp"] == c.dir_comp)].iloc[0]
        line = "" if rf.flag == "none" else rf.flag
        unit = "°C" if f.meas_step_unit == "K" else "mT"

        def show(v):
            return "NRM" if v == 0 else (f"{v - 273:.0f}" if f.meas_step_unit == "K" else f"{v * 1e3:g}")
        rows.append(dict(specimen=c.table_i, file_range=f"{show(f.meas_step_min)}-{show(f.meas_step_max)} {unit}",
                         table_range=f"{t['min']}-{t['max']}", file_line=line, table_line=t["line"],
                         n_fit=rf["n"], n_table=t["n"], angle=c.angle,
                         mad_file=rf["stored_mad"], mad_table=t["mad"],
                         discarded=t["discarded"]))
    return pd.DataFrame(rows)


def choose_orientation(core, g, spec):
    """The orientation of a core: the one in its .rs3 files, or, when its specimens differ, the one with
    which the stored fits give the directions of Table I."""
    options = g[["azimuth", "dip"]].round(1).drop_duplicates()
    if len(options) == 1:
        return float(options["azimuth"].iloc[0]), float(options["dip"].iloc[0]), ""
    fits = spec[(spec["sample"] == core) & (spec["dir_tilt_correction"] == -1)]
    scores = []
    for o in options.itertuples():
        worst = 0.0
        for t in pub.TABLE_I[pub.TABLE_I["specimen"].str[:-1] == table_i_name(core + "A")[:-1]].itertuples():
            f = fits[fits["specimen"].map(table_i_name) == t.specimen]
            worst = max(worst, min(angle(*geographic(x.dir_dec, x.dir_inc, o.azimuth, o.dip), t.dec, t.inc)
                                   for x in f.itertuples()))
        scores.append((worst, o.azimuth, o.dip))
    worst, azimuth, dip = min(scores)
    if worst > REPRODUCED:
        raise RuntimeError(f"no orientation of core {core} gives the directions of Table I")
    others = ", ".join(f"{a:g}/{d:g}" for w, a, d in scores if (a, d) != (azimuth, dip))
    note = (f"The .rs3 files of the specimens of this core give different orientations; azimuth/dip {azimuth:g}/"
            f"{dip:g} is the one with which the stored fits give the directions of Table I (the other: {others}).")
    return float(azimuth), float(dip), note


def rotate_geographic(spec, samp):
    """Make the geographic fits follow the sample orientations; return the specimens changed."""
    orient = samp.set_index("sample")[["azimuth", "dip"]]
    changed = []
    for i in spec.index[spec["dir_tilt_correction"] == 0]:
        r = spec.loc[i]
        sp = spec[(spec["specimen"] == r["specimen"]) & (spec["dir_comp"] == r["dir_comp"]) &
                  (spec["dir_tilt_correction"] == -1)].iloc[0]
        o = orient.loc[r["sample"]]
        dec, inc = geographic(sp["dir_dec"], sp["dir_inc"], o["azimuth"], o["dip"])
        if angle(dec, inc, r["dir_dec"], r["dir_inc"]) > 0.2:
            append(spec, spec.index == i, f"The geographic direction stored in the .rs3 file "
                                          f"({r['dir_dec']:g}/{r['dir_inc']:g}) follows another orientation; the "
                                          "one entered follows the sample orientation.")
            spec.loc[i, ["dir_dec", "dir_inc"]] = round(dec, 1), round(inc, 1)
            changed.append(r["specimen"])
    return changed


def geographic(dec, inc, azimuth, dip):
    d, i = pmag.dogeo(dec, inc, azimuth, dip)
    return float(d), float(i)


def table_i_refits(meas, samples, spec):
    """New fits for the specimens whose Table I fit is not stored in the file (published.TABLE_I_REFIT)."""
    rows = []
    for name, (low, high) in pub.TABLE_I_REFIT.items():
        t = pub.TABLE_I[pub.TABLE_I["specimen"] == name].iloc[0]
        specimen = spec[spec["specimen"].map(table_i_name) == name]["specimen"].iloc[0]
        m, block, values, units = specimen_vectors(meas, specimen)
        unit = "K" if t["treatment"] == "TH" else "T"
        scale = (lambda v: float(v) + 273) if unit == "K" else (lambda v: float(v) * 1e-3)
        a, b = limit_rows(values, units, scale(low), scale(high), unit)
        mode = {"OA": "anchored", "O": "anchored", "": "free"}[t["line"]]
        dec, inc, mad = fit_line(block, range(a, b + 1), mode)
        s = samples[samples["sample"] == core_of(specimen)].iloc[0]
        gdec, ginc = geographic(dec, inc, s["azimuth"], s["dip"])
        stored = spec[(spec["specimen"] == specimen) & (spec["dir_tilt_correction"] == 0)].iloc[0]
        code = "DE-BFL-A" if mode == "anchored" else "DE-BFL"
        base = dict(specimen=specimen, sample=core_of(specimen), dir_comp=f"{stored['dir_comp']} (Table I)",
                    dir_n_measurements=b - a + 1, meas_step_min=scale(low), meas_step_max=scale(high),
                    meas_step_unit=unit, result_quality="g", software_packages="pmagpy convert.py",
                    citations="This study",
                    experiments=stored["experiments"])
        mad_column = "dir_mad_anc" if mode == "anchored" else "dir_mad_free"
        description = (f"Not stored in the archived file: recalculated here from the measurements as the fit of "
                       f"Table I ({low}-{high} °C, {t['line'] or 'free'}), which is the one in the site mean of "
                       f"Table 2. Table I gives {t['dec']}/{t['inc']}, MAD {t['mad']}; recalculated "
                       f"{gdec:.1f}/{ginc:.1f}, MAD {mad:.1f}.")
        rows.append(dict(base, dir_dec=round(dec, 1), dir_inc=round(inc, 1), dir_tilt_correction=-1,
                         method_codes=f"{code}:{stored['method_codes'].split(':', 1)[1].replace('DA-DIR-GEO', 'DA-DIR')}",
                         description=description, **{mad_column: round(mad, 1)}))
        rows.append(dict(base, dir_dec=round(gdec, 1), dir_inc=round(ginc, 1), dir_tilt_correction=0,
                         method_codes=f"{code}:{stored['method_codes'].split(':', 1)[1]}",
                         description=description, **{mad_column: round(mad, 1)}))
        rows[-1]["table_i"] = name
    return pd.DataFrame(rows)


# ================================================================ site means and VGPs

def site_directions(table):
    """The directions that enter each site mean: specimen name, mean unit, dec, inc (geographic)."""
    by_site = defaultdict(list)
    for r in table.itertuples():
        by_site[site_of(r.specimen)].append((r.specimen, mean_unit(r.specimen), r.dec, r.inc))
    return by_site


def hierarchical_mean(entries):
    """Fisher mean of the means of the units (cores or blocks), each the mean of its specimens."""
    units = defaultdict(list)
    for specimen, unit, dec, inc in entries:
        units[unit].append((dec, inc))
    means = [fisher(v) for v in units.values()]
    f = fisher([(m["dec"], m["inc"]) for m in means])
    return dict(dec=f["dec"], inc=f["inc"], alpha95=f["alpha95"], k=f["k"], n_units=len(units),
                n_specimens=len(entries), units=sorted(units))


def recalculate_sites(entries_by_site):
    rows = []
    for p in pub.TABLE2_DIRECTIONS.itertuples():
        m = hierarchical_mean(entries_by_site[p.site])
        rows.append(dict(site=p.site, dec_pub=p.dec, inc_pub=p.inc, a95_pub=p.a95, n_pub=p.n,
                         dec=m["dec"], inc=m["inc"], a95=m["alpha95"], k=m["k"], n=m["n_units"],
                         n_specimens=m["n_specimens"], angle=angle(m["dec"], m["inc"], p.dec, p.inc),
                         units=m["units"], specimens=[e[0] for e in entries_by_site[p.site]]))
    out = pd.DataFrame(rows)
    out["reproduced"] = (out["angle"] <= REPRODUCED) & ((out["a95"] - out["a95_pub"]).abs() <= 0.051) & (
        out["n"] == out["n_pub"])
    return out


def recalculate_vgps():
    rows = []
    for p in pub.TABLE2_DIRECTIONS.itertuples():
        t1 = pub.TABLE1[pub.TABLE1["site"] == p.site].iloc[0]
        t3 = pub.TABLE3[pub.TABLE3["site"] == p.site].iloc[0]
        plon, plat, dp, dm = pmag.dia_vgp(p.dec, p.inc, p.a95, t1["lat"], t1["lon"])
        rows.append(dict(site=p.site, lat_pub=t3["vgp_lat"], lon_pub=t3["vgp_lon"], dp_pub=t3["dp"], dm_pub=t3["dm"],
                         lat=plat, lon=plon, dp=dp, dm=dm,
                         angle=angle(plon, plat, t3["vgp_lon"], t3["vgp_lat"])))
    return pd.DataFrame(rows)


# ================================================================ Thellier-Coe (.tdt)
#
# 142 ThellierTool files (laboratory field 40 μT), one per specimen and experiment: 82 of standard
# Thellier-Coe experiments and 46 with a low-temperature demagnetization after each heating step
# (LTD_*.TDT), and 14 corrected copies of 13 of them (*_C.TDT, *_CC.TDT), the same file with some
# steps deleted. Table III gives one row for each of the 128 specimens and names the corrected copy
# where it is the one interpreted (GTX0308B_c). The files are converted with convert_2_magic.tdt;
# each specimen enters once, from its original file, and the measurements that the interpreted copy
# leaves out are flagged bad. Each determination of Table III is recalculated with pmag.sortarai
# and pmag.PintPars.

PALEOINTENSITY_FOLDER = "LA GARROTXA/PALEOINTENSITY"
COPY = re.compile(r"^(.+?)_(c{1,2})$", re.IGNORECASE)


def read_table_iii():
    """Table III as printed (table_iii.csv): one row per specimen, numbers as floats (NaN where none)."""
    table = pd.read_csv(STUDY_DIR / "table_iii.csv", dtype=str, keep_default_na=False)
    for column in ("t_min", "t_max", "n", "beta", "f", "q", "dck", "alpha95", "mad", "b", "db"):
        table[column] = pd.to_numeric(table[column].replace("", np.nan))
    return table.rename(columns={"class": "class_"})  # "class" is not a name itertuples can use


def convert_tdt(folder, name, rename=None):
    """Convert .TDT files with PmagPy, each specimen named after its file.

    Args:
        folder: the folder of the files.
        name: the name of the build folders (build/<name>_files and build/converted_<name>).
        rename: dict of file name to the specimen name to enter; the files are copied under
            that name (their content is not changed). None converts the files as named.

    Returns:
        DataFrame: the measurements table.
    """
    files, out = BUILD_DIR / f"{name}_files", BUILD_DIR / f"converted_{name}"
    for d in (files, out):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    for path in sorted(folder.rglob("*.TDT")):
        if rename is None or path.stem in rename:
            shutil.copy(path, files / (f"{rename[path.stem]}.TDT" if rename else path.name))
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        ok, message = convert_2_magic.tdt(str(files), output_dir_path=str(out), spec_name_con=2,
                                          moment_units="A/m", lab_dec=pub.THELLIER_LAB_DEC,
                                          lab_inc=pub.THELLIER_LAB_INC, location=pub.LOCATION)
    if not ok:
        raise RuntimeError(f"convert_2_magic.tdt: {message}")
    return read_table(out / "measurements.txt")


def removed_steps(original, copy):
    """Positions of the measurements of an original file that its corrected copy does not hold.

    The copy must be the original with some measurements deleted, the others in the same order
    and with the same values.
    """
    key = ["treat_temp", "dir_dec", "dir_inc", "magn_volume"]
    first = original["method_codes"].str.split(":").str[0]
    rows_o = list(zip(*(original[k] for k in key), first))
    rows_c = list(zip(*(copy[k] for k in key), copy["method_codes"].str.split(":").str[0]))
    removed, j = [], 0
    for row in rows_c:
        while j < len(rows_o) and rows_o[j] != row:
            removed.append(j)
            j += 1
        if j == len(rows_o):
            raise RuntimeError("a corrected copy holds a measurement that its original file does not")
        j += 1
    return removed + list(range(j, len(rows_o)))


def thellier_files(table, stems):
    """The file of each row of Table III, and the original file of each specimen.

    Returns:
        DataFrame with the Table III columns and file (as interpreted), original, copy (bool).
    """
    by_lower = {s.lower(): s for s in stems}
    rows = []
    for r in table.itertuples():
        stem = pub.TABLE_III_FILE_NAMES.get((r.ltd, r.specimen), ("LTD_" if r.ltd else "") + r.specimen)
        if stem.lower() not in by_lower:
            raise RuntimeError(f"Table III {r.ltd and 'LTD '}{r.specimen}: no file {stem}.TDT")
        stem = by_lower[stem.lower()]
        m = COPY.match(stem)
        original = by_lower[m.group(1).lower()] if m else stem
        rows.append(dict(r._asdict(), file=stem, original=original, copy=bool(m)))
    out = pd.DataFrame(rows).drop(columns="Index")
    if out["original"].duplicated().any():
        raise RuntimeError("two rows of Table III for one specimen")
    return out


def thellier_sample(original, direction_samples):
    """The sample of a Thellier specimen, from its file name (LTD_ removed).

    OL0102A -> OL01-2 (the core named OL01-2 in the demagnetization files); GTX0206B1 -> GTX0206;
    GTX080101 -> GTX080101, a core of the hand block GTX0801; LTD_GTX08021 -> GTX0802 and
    GTX10011 -> GTX1001, hand blocks; GTX11011 -> GTX1101, an unoriented hand block.
    """
    name = original.replace("LTD_", "")
    m = re.fullmatch(r"(OL\d\d)(\d\d)[A-Z]+", name)
    if m:
        return f"{m.group(1)}-{int(m.group(2))}"
    return name[:9] if name[:9] in direction_samples else name[:7]


def mark_ltd(meas):
    """Method codes of the experiments with a low-temperature demagnetization after each heating step."""
    ltd = meas["specimen"].str.startswith("LTD_")
    heated = ltd & ~meas["method_codes"].str.startswith("LT-NO")
    meas.loc[heated, "method_codes"] = meas.loc[heated, "method_codes"].str.replace(
        r"^(LT-[A-Z-]+?)(:|$)", r"\1:LT-LT-Z\2", regex=True)
    meas.loc[ltd, "method_codes"] = meas.loc[ltd, "method_codes"] + ":LP-LT"
    return meas


def lab_field_check(meas):
    """Angle between the laboratory field and the median direction of the pTRMs gained (in field minus
    zero field at the same step), for each specimen (a Series)."""
    angles = {}
    for specimen, g in meas.groupby("specimen"):
        z = g[g["method_codes"].str.startswith("LT-T-Z")].drop_duplicates("treat_temp").set_index("treat_temp")
        i = g[g["method_codes"].str.startswith("LT-T-I")].drop_duplicates("treat_temp").set_index("treat_temp")
        gained = [pmag.dir2cart([i.loc[t, "dir_dec"], i.loc[t, "dir_inc"], i.loc[t, "magn_volume"]])
                  - pmag.dir2cart([z.loc[t, "dir_dec"], z.loc[t, "dir_inc"], z.loc[t, "magn_volume"]])
                  for t in i.index.intersection(z.index)]
        if gained:
            median = np.median([v / np.linalg.norm(v) for v in gained], axis=0)
            angles[specimen] = angle(*pmag.cart2dir(median)[:2], pub.THELLIER_LAB_DEC, pub.THELLIER_LAB_INC)
    return pd.Series(angles)


def recalculate_thellier(meas, files):
    """Recalculate each determination of Table III from the measurements flagged good.

    The Arai plot is made with pmag.sortarai and the best-fit line and its statistics with
    pmag.PintPars, and the anchored MAD with pmag.domean on the same steps. A range from 20 °C starts
    at the NRM, which is one of the N points. δ(CK) and alpha are not recalculated (README.md).
    """
    rows = []
    for r in files[files["t_min"].notna()].itertuples():
        specimen = r.original + pub.THELLIER_SUFFIX
        block = meas[(meas["specimen"] == specimen) & (meas["quality"] == "g")]
        t_min, t_max = pub.TABLE_III_RANGE.get((r.ltd, r.specimen), (r.t_min, r.t_max))
        with contextlib.redirect_stdout(io.StringIO()):
            araiblock, lab_field = pmag.sortarai(block, specimen, 0, version=3)
            zijdblock, _ = pmag.find_dmag_rec(specimen, block, version=3)
        temperatures = [step[0] - 273 for step in araiblock[0]]
        start = 0 if t_min <= 50 else min(k for k, t in enumerate(temperatures) if t >= t_min)
        end = max(k for k, t in enumerate(temperatures) if t <= t_max)
        with contextlib.redirect_stdout(io.StringIO()):
            pars, _ = pmag.PintPars(block, araiblock, zijdblock, start, end, {}, version=3)
        zijd_t = [step[0] - 273 for step in zijdblock]
        z0 = 0 if t_min <= 50 else zijd_t.index(temperatures[start])
        z1 = zijd_t.index(temperatures[end])
        anchored = pmag.domean([list(s) for s in zijdblock], z0, z1, "DE-BFL-A")
        row = dict(specimen=("LTD " if r.ltd else "") + r.specimen, range=f"{t_min:.0f}-{t_max:.0f}",
                   cls=r.class_,
                   N_pub=int(r.n), N=int(pars["int_n_measurements"]), B_pub=r.b,
                   B=abs(pars["int_b"]) * lab_field * 1e6, dB_pub=r.db, dB=pars["int_b_sigma"] * lab_field * 1e6,
                   beta_pub=r.beta, beta=pars["int_b_beta"], f_pub=r.f, f=pars["int_f"], q_pub=r.q,
                   q=pars["int_q"], mad_pub=r.mad, mad=float(anchored["specimen_mad"]))
        # the archived moments have four significant figures, so the last printed digit can differ
        row["B_agrees"] = (row["N"] == row["N_pub"] and abs(row["B"] - r.b) <= max(0.05, 0.001 * r.b)
                           and abs(row["beta"] - r.beta) <= 0.0015)
        row["mad_agrees"] = abs(row["mad"] - r.mad) <= 0.051
        row["fq_agree"] = abs(row["f"] - r.f) <= 0.025 and abs(row["q"] - r.q) <= max(0.1, 0.03 * r.q)
        rows.append(row)
    return pd.DataFrame(rows)


def thellier_specimen_rows(meas, files):
    """Specimens-table rows of the Thellier specimens: the result of Table III, or a bare record."""
    experiments = meas.groupby("specimen")["experiment"].first()
    codes = meas.groupby("specimen")["method_codes"].agg(
        lambda c: ":".join(sorted({x for code in c for x in code.split(":") if x.startswith("LP-")})))
    rows = []
    for r in files.itertuples():
        specimen = r.original + pub.THELLIER_SUFFIX
        cls = r.class_
        printed = ("LTD " if r.ltd else "") + r.specimen
        row = OrderedDict(specimen=specimen, experiments=experiments[specimen], method_codes=codes[specimen],
                          citations="This study")
        text = (f"Thellier-Coe microcore (laboratory field {pub.THELLIER_LAB_FIELD * 1e6:.0f} μT)"
                + (", with a low-temperature demagnetization in liquid nitrogen after each heating step (LTD)"
                   if r.ltd else "") + f"; file {r.original}.TDT; Table III: {printed}.")
        if r.copy:
            text += (f" The determination is that of the corrected copy {r.file}.TDT, which leaves out the "
                     "measurements flagged bad.")
        if pd.notna(r.t_min):
            t_min, t_max = pub.TABLE_III_RANGE.get((r.ltd, r.specimen), (r.t_min, r.t_max))
            row.update(method_codes=codes[specimen] + ":IE-TT", result_quality="b" if cls == "R" else "g",
                       int_abs=f"{r.b * 1e-6:.4e}", int_abs_sigma=f"{r.db * 1e-6:.3e}",
                       int_treat_dc_field=f"{pub.THELLIER_LAB_FIELD:.1e}", int_n_measurements=int(r.n),
                       int_b_beta=r.beta, int_f=r.f, int_q=r.q, int_dck=r.dck, int_mad_anc=r.mad,
                       int_alpha=r.alpha95, meas_step_min=t_min + 273, meas_step_max=t_max + 273,
                       meas_step_unit="K", software_packages=pub.THELLIER_SOFTWARE)
            text += f" Class {cls} (Table III)" + (f": rejected, {r.observations}." if cls == "R" else ".")
            if (r.ltd, r.specimen) in pub.TABLE_III_RANGE:
                text += (f" Table III prints the range {r.t_min:.0f}-{r.t_max:.0f} °C, which holds one step fewer "
                         f"than its N = {int(r.n)}; {t_min:.0f}-{t_max:.0f} °C gives N, B, β, f and q of the table "
                         "and is entered (inferred).")
            if t_min <= 50:
                text += " The range starts at the NRM, which is one of the N points."
        else:
            text += f" No determination: rejected in Table III ({r.observations})."
        if r.observations.startswith("(*)"):
            text += " It passes the numerical criteria but is discarded because of the observation (Table III)."
        row["description"] = text
        rows.append(row)
    return pd.DataFrame(rows)


def thellier_site_checks(files):
    """The site paleointensities of Tables 2 and 4 against the mean and standard deviation of the accepted
    determinations of Table III (all, without LTD, with LTD)."""
    accepted = files[files["class_"].isin(["A", "B", "C"])].assign(site=lambda d: d["original"].map(
        lambda s: site_of(s.replace("LTD_", ""))))
    rows = []
    for t4 in pub.TABLE4.itertuples():
        a = accepted[accepted["site"] == t4.site]
        out = dict(site=t4.site)
        for label, subset, b_pub, db_pub, n_pub in (
                ("all", a, t4.b, t4.db, t4.n), ("std", a[a["ltd"] == ""], t4.b_std, t4.db_std, t4.n_std),
                ("ltd", a[a["ltd"] == "yes"], t4.b_ltd, t4.db_ltd, t4.n_ltd)):
            values = subset["b"].to_numpy()
            out.update({f"n_{label}_pub": n_pub, f"n_{label}": len(values), f"B_{label}_pub": b_pub,
                        f"B_{label}": values.mean() if len(values) else np.nan, f"dB_{label}_pub": db_pub,
                        f"dB_{label}": values.std(ddof=1) if len(values) > 1 else np.nan})
        counts = a["class_"].value_counts()
        out.update(classes_pub=f"{t4.class_a}/{t4.class_b}/{t4.class_c}",
                   classes=f"{counts.get('A', 0)}/{counts.get('B', 0)}/{counts.get('C', 0)}")
        n_specimens = (files["original"].map(lambda s: site_of(s.replace("LTD_", ""))) == t4.site).sum()
        out.update(N_pub=t4.N, N=int(n_specimens))
        rows.append(out)
    return pd.DataFrame(rows), accepted


# ================================================================ rock magnetism and thermal stability (VFTB)
#
# ROCK MAG: 21 sets of four VFTB curves (.irm, .coe, .hys, .rmp), one powder per file name; the
# paper gives no values per sample, so the curves are entered and their parameters are only
# calculated for the report. THERMAL STABILITY: 46 partial magnetization-temperature cycles (.rmp),
# the experiments of Table IV, recalculated here. The .prm files are the measurement settings of the
# instrument (YAML), not data, and the .pdf, .png, .emf and .svg files are figures.

VFTB_CURVES = OrderedDict([("irm", "IRM acquisition"), ("coe", "back-field demagnetization of the IRM"),
                           ("hys", "hysteresis loop"),
                           ("rmp", "magnetization against temperature in a field, heated to 700 °C and cooled")])


def convert_vftb_file(path, specimen, stem):
    """Convert one VFTB file with PmagPy; return its measurements and the weight it gives (kg)."""
    out = BUILD_DIR / "converted_vftb"
    out.mkdir(parents=True, exist_ok=True)
    tables = {t: f"{stem}_{t}.txt" for t in ("measurements", "specimens", "samples", "sites", "locations")}
    with contextlib.redirect_stdout(io.StringIO()):
        ok, message = convert_2_magic.vftb(path.name, dir_path=str(out), input_dir_path=str(path.parent),
                                           meas_outfile=tables["measurements"], spec_outfile=tables["specimens"],
                                           samp_outfile=tables["samples"], site_outfile=tables["sites"],
                                           loc_outfile=tables["locations"], specimen=specimen,
                                           location=pub.LOCATION)
    if not ok:
        raise RuntimeError(f"convert_2_magic.vftb, {path.name}: {message}")
    return read_table(out / tables["measurements"]), read_table(out / tables["specimens"])["weight"].iloc[0]


def piece_sample(name, known_samples):
    """The sample of a rock-magnetic or thermal-stability piece: OL0102A, OL0106 -> OL01-2, OL01-6;
    GTX080103inf -> GTX080103 (a core); GTX0208B_MAL, GTX0102inf -> GTX0208, GTX0102."""
    m = re.fullmatch(r"(OL\d\d)(\d\d)[A-Z]*", name)
    if m:
        return f"{m.group(1)}-{int(m.group(2))}"
    return name[:9] if name[:9] in known_samples else name[:7]


def build_rockmag(folder, known_samples):
    """The 21 rock-magnetic powders: measurements and specimens rows."""
    measurements, rows = [], []
    for stem in sorted({p.stem for p in folder.iterdir() if p.suffix.lstrip(".") in VFTB_CURVES}):
        specimen, weights, curves = stem + pub.ROCKMAG_SUFFIX, set(), []
        for extension, curve in VFTB_CURVES.items():
            path = folder / f"{stem}.{extension}"
            if not path.exists():
                raise RuntimeError(f"no file {path.name}")
            meas, weight = convert_vftb_file(path, specimen, f"{stem}_{extension}")
            measurements.append(meas)
            weights.add(weight)
            curves.append(curve)
        if len(weights) != 1:
            raise RuntimeError(f"{stem}: the files give different weights")
        sample = piece_sample(stem.replace("_MAL", ""), known_samples)
        text = (f"Powder of {sample}, measured on a variable field translation balance at Burgos: "
                f"{'; '.join(curves)} (files {stem}.irm, .coe, .hys, .rmp). The paper gives no results per sample.")
        if stem.endswith("_MAL"):
            text += (f" A second set of curves, with the suffix _MAL, of the core of {stem[:-4]}; the paper does "
                     "not say what it is.")
        rows.append(OrderedDict(specimen=specimen, sample=sample, weight=weights.pop(),
                                experiments=join(sorted(m["experiment"].iloc[0] for m in measurements[-4:])),
                                method_codes=join(m["method_codes"].iloc[0].split(":")[0] for m in measurements[-4:]),
                                citations="This study", description=text))
    return pd.concat(measurements, ignore_index=True), pd.DataFrame(rows)


def rockmag_parameters(meas):
    """Bcr, and Ms, Mr, Bc two ways, of each powder, for the report.

    Bcr is the zero crossing of the back-field curve (rockmag.process_backfield_data). Ms, Mr and Bc
    are those of rockmag.process_hyst_loop, and those read from the measured branches (_branch) after
    removing the high-field slope fitted above 60 percent of the peak field: Ms the intercept, Mr the
    magnetization at zero field and Bc the zero crossing, by linear interpolation. The difference
    between the two is the subject of PmagPy issue #1048.
    """
    rows = []
    for specimen, g in meas.groupby("specimen"):
        out = dict(specimen=specimen)
        back = g[g["method_codes"].str.startswith("LP-IRM-DCD")]
        with contextlib.redirect_stdout(io.StringIO()):
            out["bcr"] = rockmag.process_backfield_data(back[["treat_dc_field", "magn_mass"]].astype(float))[1] * 1e3
        loop = g[g["method_codes"].str.startswith("LP-HYS")]
        H, M = loop["meas_field_dc"].astype(float).values, loop["magn_mass"].astype(float).values
        with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = rockmag.process_hyst_loop(H, M, specimen, show_results_table=False, show_plot=False, n_bootstrap=0)
            H, M, _ = rockmag.drop_hyst_initial_curve(H, M)
            upper, lower = rockmag.split_hyst_loop(H, M)
        out.update(ms=r["Ms"], mr=r["Mr"], bc=r["Bc"] * 1e3)
        hp, hn = H > 0.6 * H.max(), H < 0.6 * H.min()
        sp, ip = np.polyfit(H[hp], M[hp], 1)
        sn, i_n = np.polyfit(H[hn], M[hn], 1)
        slope = (sp + sn) / 2
        out["ms_branch"] = (ip - i_n) / 2
        mr, bc = [], []
        for f, m in (upper, lower):
            corrected = m - slope * f
            mr.append(abs(np.interp(0, f, corrected)))
            k = np.flatnonzero(np.diff(np.sign(corrected)) != 0)
            k = k[np.argmin(np.abs(f[k]))]
            bc.append(abs(f[k] - corrected[k] * (f[k + 1] - f[k]) / (corrected[k + 1] - corrected[k])))
        out.update(mr_branch=np.mean(mr), bc_branch=np.mean(bc) * 1e3, points=len(H))
        rows.append(out)
    out = pd.DataFrame(rows)
    out["bcr_bc"] = out["bcr"] / out["bc_branch"]
    out["mr_ms"] = out["mr_branch"] / out["ms_branch"]
    return out


def read_table_iv():
    """Table IV as printed (table_iv.csv)."""
    table = pd.read_csv(STUDY_DIR / "table_iv.csv", dtype=str, keep_default_na=False)
    for column in ("t_min", "t_max", "t1", "mag1f_mag1i", "t2", "mag2f_mag2i", "t3", "mag3f_mag3i", "mag2f_mag1i"):
        table[column] = pd.to_numeric(table[column].replace("", np.nan))
    return table


def magnetization_ratio(final, initial):
    """MAGF/MAGI of Table IV: the magnetization at the end of the cooling branch of one cycle over that of
    the heating branch of a cycle (the same, or the first) at the same temperature, interpolated linearly."""
    cooling = final[final["method_codes"].str.contains("LP-MC")]
    heating = initial[initial["method_codes"].str.contains("LP-MW")]
    t_end, m_end = float(cooling["meas_temp"].iloc[-1]), float(cooling["magn_mass"].iloc[-1])
    t, m = heating["meas_temp"].astype(float).values, heating["magn_mass"].astype(float).values
    k = int(np.argmax(t >= t_end))
    m_start = m[0] if k == 0 else m[k - 1] + (m[k] - m[k - 1]) * (t_end - t[k - 1]) / (t[k] - t[k - 1])
    return m_end / m_start


def build_thermal_stability(folder, known_samples):
    """The cycles of Table IV: measurements, specimens rows and the recalculated ratios.

    The cycles of one row whose files give the same weight are taken to be one piece: Table IV gives
    MAG2F/MAG1I "only when the same specimen was analyzed for both experiments".
    """
    table = read_table_iv()
    paths = {p.stem: p for p in folder.rglob("*.rmp")}
    measurements, rows, checks = [], [], []
    for r in table.itertuples():
        name = r.specimen.replace("OLO", "OL0")
        runs = []
        for k, stem in enumerate(pub.TABLE_IV_FILES[r.specimen]):
            meas, weight = convert_vftb_file(paths[stem], name, f"ts_{stem}")
            runs.append(dict(stem=stem, meas=meas, weight=weight, peak=float(meas["meas_temp"].max()) - 273))
        pieces = list(OrderedDict.fromkeys(run["weight"] for run in runs))
        for run in runs:
            piece = pieces.index(run["weight"])
            run["specimen"] = name + pub.THERMAL_STABILITY_SUFFIX + ("" if piece == 0 else str(piece + 1))
            experiment = f"{run['specimen']}_LP-IMT-{run['peak']:.0f}C-{run['stem']}"
            run["meas"] = run["meas"].assign(specimen=run["specimen"], experiment=experiment,
                                             measurement=[f"{experiment}-{k + 1}" for k in range(len(run["meas"]))])
            measurements.append(run["meas"])
        temperatures = [t for t in (r.t1, r.t2, r.t3) if pd.notna(t)]
        published = [r.mag1f_mag1i, r.mag2f_mag2i, r.mag3f_mag3i]
        for k, run in enumerate(runs):
            # GTX0604: two cycles of one specimen to 560 °C, for the one T1 of the table
            t_pub = temperatures[min(k, len(temperatures) - 1)] if temperatures else np.nan
            p = published[min(k, len(temperatures) - 1)] if temperatures else np.nan
            checks.append(dict(row=r.specimen, file=run["stem"], specimen=run["specimen"], weight_mg=run["weight"] * 1e6,
                               T_pub=t_pub, T=run["peak"], ratio_pub=p,
                               ratio=magnetization_ratio(run["meas"], run["meas"])))
        if len(runs) > 1 and pd.notna(r.mag2f_mag1i):
            checks.append(dict(row=r.specimen, file=f"{runs[1]['stem']} / {runs[0]['stem']}", specimen=runs[0]["specimen"],
                               weight_mg=np.nan, T_pub=np.nan, T=np.nan, ratio_pub=r.mag2f_mag1i,
                               ratio=magnetization_ratio(runs[1]["meas"], runs[0]["meas"]), kind="MAG2F/MAG1I"))
        for specimen in OrderedDict.fromkeys(run["specimen"] for run in runs):
            own = [run for run in runs if run["specimen"] == specimen]
            text = (f"Thermal-stability cycles of Table IV ({r.specimen}): magnetization against temperature in a "
                    f"field of about 35 mT (the files; the text gives 38 mT), from a 1 T IRM, heated to "
                    + ", ".join(f"{run['peak']:.0f}" for run in own) + " °C and cooled (files "
                    + ", ".join(f"{run['stem']}.rmp" for run in own) + ").")
            values = [f"T{k + 1} {t:.0f} °C, phases {ph or '-'}, MAG{k + 1}F/MAG{k + 1}I {m:.3f}" for k, (t, ph, m) in
                      enumerate(zip((r.t1, r.t2, r.t3), (r.t1_phases, r.t2_phases, r.t3_phases), published))
                      if pd.notna(t) and pd.notna(m)]
            if values:
                text += " Table IV: " + "; ".join(values) + (f"; MAG2F/MAG1I {r.mag2f_mag1i:.3f}" if pd.notna(
                    r.mag2f_mag1i) else "") + "."
            if r.note:
                text += f" Table IV: {r.note}" + (", alteration." if r.note == "Rejected" else ".")
            if len(pieces) > 1:
                text += " The other cycles of this row of Table IV are of a piece of another weight."
            rows.append(OrderedDict(specimen=specimen, sample=piece_sample(name, known_samples),
                                    weight=own[0]["weight"],
                                    experiments=join(run["meas"]["experiment"].iloc[0] for run in own),
                                    method_codes="LP-IMT", citations="This study", description=text))
    checks = pd.DataFrame(checks)
    checks["kind"] = checks["kind"].fillna("MAGF/MAGI") if "kind" in checks else "MAGF/MAGI"
    checks["agrees"] = np.where(checks["ratio_pub"].isna(), "", np.where(
        (checks["ratio"] - checks["ratio_pub"]).abs() <= 0.0051, "yes", "no"))
    return pd.concat(measurements, ignore_index=True), pd.DataFrame(rows), checks, table


# ================================================================ the contribution

def geology(df):
    df["geologic_classes"], df["geologic_types"] = pub.GEOLOGIC_CLASSES, pub.GEOLOGIC_TYPES
    df["lithologies"] = pub.LITHOLOGIES
    return df


def site_info(site):
    return pub.TABLE1[pub.TABLE1["site"] == site].iloc[0]


def main():
    BUILD_DIR.mkdir(exist_ok=True)
    folder = extract_archive()
    rs3_dir, dat_dir = gather(folder, ".rs3", "rs3_files"), gather(folder, ".dat", "dat_files")

    # ---- reading
    rs3, rs3_warnings = convert_rs3(rs3_dir)
    meas_2g, samples_2g, warnings_2g = convert_2g(dat_dir)
    raw = read_rs3_raw(rs3_dir)
    files_check = compare_2g_rs3(meas_2g, samples_2g, raw)
    gtx = set(meas_2g["specimen"])
    if not gtx <= set(rs3["measurements"]["specimen"]):
        raise RuntimeError("a 2G file has no .rs3 file")
    if (files_check["same_steps"] & (files_check["max_angle"] > 0.1)).any():
        raise RuntimeError("the 2G and .rs3 files of a specimen differ in direction")

    # measurements: the 2G files where they exist (GTX), the .rs3 files otherwise (OL)
    meas_rs3 = rs3["measurements"]
    meas_rs3_ol = meas_rs3[~meas_rs3["specimen"].isin(gtx)]
    meas = pd.concat([meas_2g, meas_rs3_ol], ignore_index=True)
    meas["citations"] = "This study"

    # ---- specimens: the stored fits
    spec = rs3["specimens"].copy()
    spec["sample"] = spec["specimen"].map(core_of)
    # the converter writes its notes as clauses joined by "; ": each becomes a sentence
    spec["description"] = spec["description"].fillna("").map(
        lambda d: " ".join(c[0].upper() + c[1:] + ("" if c.endswith((".", "?", "!")) else ".") for c in d.split("; ") if c))
    refits = refit_stored(spec, meas)
    # the line flag in the file: rs3 writes a fit flagged O that is the anchored line as DE-BFL-A
    flags = {(name, fit["name"]): fit["flag"] for name, (_, _, fits) in raw.items() for fit in fits}
    refits["flag"] = [flags[(r.specimen, r.dir_comp)] or "none" for r in refits.itertuples()]
    for r in refits.itertuples():
        rows = (spec["specimen"] == r.specimen) & (spec["dir_comp"] == r.dir_comp)
        if r.calculation in ("free", "anchored", "origin"):
            spec.loc[rows, "dir_n_measurements"] = r.n
        if r.calculation in ("free", "anchored", "origin") and not r.earlier_start:
            # rs3 checks the steps of the .rs3 file; the measurements entered for the GTX sites are those
            # of the 2G file, which can hold a step that the .rs3 file lacks (README.md, item 1)
            checked = spec.loc[rows, "description"].str.contains(" is not reproduced from the steps between its limits")
            if checked.any():
                spec.loc[rows, "description"] = spec.loc[rows, "description"].str.replace(
                    r"The stored line \(flag \w+\) is not reproduced from the steps between its limits.*?\)\.",
                    "The stored line is not reproduced from the steps of the .rs3 file, but it is from the measurements "
                    "entered, those of the 2G file.", regex=True)
        if r.earlier_start:
            append(spec, rows, f"The stored direction and MAD are those of a fit that starts at the {r.first_step} "
                               f"step, before the stated first limit; LP-DIR-T is added and meas_step_min is 0 T, the "
                               f"field of that step (recalculated over {int(r.n)} measurements).")
            spec.loc[rows, "method_codes"] = spec.loc[rows, "method_codes"].str.replace(
                "LP-DIR-AF", "LP-DIR-T:LP-DIR-AF")
            spec.loc[rows, "meas_step_min"] = 0.0
        if r.left_out:
            append(spec, rows, f"The 2G file holds two measurements at {r.left_out.split(' (')[0]}; the stored line is "
                               f"reproduced without the {r.left_out.split('(')[1][:-1]} of them ({int(r.n)} "
                               "measurements).")
        if r.calculation == "not reproduced":
            append(spec, rows, f"The stored direction is not reproduced from the archived measurements between its "
                               f"limits (closest {r.angle:.1f}° away).")
    # samples: the orientation in the .rs3 files, which Table I follows
    samp_rs3 = rs3["samples"].copy()
    samp_rs3["core"] = samp_rs3["sample"].map(core_of)
    samples = []
    for core, g in samp_rs3.groupby("core", sort=False):
        azimuth, dip, chosen_note = choose_orientation(core, g, spec)
        site = site_of(core)
        t1 = site_info(site)
        row = OrderedDict(sample=core, site=site, azimuth=azimuth, dip=dip,
                          method_codes=pub.ORIENTATION_BLOCKS if site in pub.BLOCK_SITES else pub.ORIENTATION_CORES,
                          lat=t1["lat"], lon=t1["lon"], citations="This study", description="")
        if site in pub.BLOCK_SITES:
            row["description"] = (f"A core drilled in the laboratory from the oriented hand block {block_of(core + 'A')}; "
                                  "the orientation is that of the core in the .rs3 file.")
        diff = files_check[files_check["specimen"].map(core_of) == core]
        if not diff.empty:
            d = diff.iloc[0]
            if abs(d.azimuth_2g - row["azimuth"]) > 0.5 or abs(d.dip_2g - row["dip"]) > 0.5:
                row["description"] = (row["description"] + " " if row["description"] else "") + (
                    f"The 2G file gives another orientation (azimuth {d.azimuth_2g:g}, dip {d.dip_2g:g} as read by "
                    f"PmagPy); the .rs3 file, which the directions of Table I follow, is used.")
        if chosen_note:
            row["description"] = (row["description"] + " " if row["description"] else "") + chosen_note
        samples.append(row)
    samp = geology(pd.DataFrame(samples))
    regeo_notes = rotate_geographic(spec, samp)
    geo = spec[spec["dir_tilt_correction"] == 0]
    chrm = chrm_rows(geo)
    table_i_check = compare_table_i(geo, chrm, refits)

    # Table I differences, written to the rows of the characteristic fits (both coordinate systems)
    for c, t in zip(chrm.itertuples(), table_i_check.itertuples()):
        rows = (spec["specimen"] == c.specimen) & (spec["dir_comp"] == c.dir_comp)
        notes = []
        if t.discarded:
            spec.loc[rows, "result_quality"] = "b"
            notes.append("Discarded in Table I (*).")
        if c.table_i in pub.TABLE_I_FILE_DIRECTION:
            p = pub.TABLE_I[pub.TABLE_I["specimen"] == c.table_i].iloc[0]
            notes.append(f"Table I gives {p['dec']}/{p['inc']}, {c.angle:.1f}° from the stored direction; the site "
                         "mean of Table 2 recalculates with the stored direction, which is entered.")
        elif c.table_i in pub.TABLE_I_REFIT:
            spec.loc[rows, "result_quality"] = "b"
            notes.append("Not the fit of Table I, which is entered as a separate row.")
        elif c.angle > REPRODUCED:
            p = pub.TABLE_I[pub.TABLE_I["specimen"] == c.table_i].iloc[0]
            notes.append(f"Table I gives {p['dec']}/{p['inc']} (MAD {p['mad']}), {c.angle:.1f}° from the stored "
                         "direction.")
        if not np.isnan(t.n_fit) and int(t.n_fit) != int(t.n_table) and c.table_i not in pub.TABLE_I_REFIT:
            notes.append(f"Table I gives N = {t.n_table}; the stored line is reproduced with {int(t.n_fit)} "
                         "measurements.")
        if notes:
            append(spec, rows, " ".join(notes))
    other = ~spec.set_index(["specimen", "dir_comp"]).index.isin(list(zip(chrm["specimen"], chrm["dir_comp"])))
    append(spec, other, "Not the characteristic component of Table I.")

    spec = geology(spec)
    spec["citations"] = "This study"

    # the fits of Table I that are not stored in a file
    new_fits = table_i_refits(meas, samp, spec)
    spec = pd.concat([spec, geology(new_fits.drop(columns=["table_i"], errors="ignore"))], ignore_index=True)
    spec = spec.sort_values(["specimen", "dir_tilt_correction"], kind="stable").reset_index(drop=True)

    n_demag = spec["specimen"].nunique()

    # ---- Thellier-Coe (.tdt): Table III, and the site paleointensities of Tables 2 and 4
    pi_folder = folder.parent / "PALEOINTENSITY"
    table_iii = read_table_iii()
    # every file as named, so that the corrected copies can be compared with their originals
    tdt_all = convert_tdt(pi_folder, "tdt_all")
    stems = set(tdt_all["specimen"])
    pi_files = thellier_files(table_iii, stems)
    if set(pi_files["original"]) != {s for s in stems if not COPY.match(s)}:
        raise RuntimeError("the original .TDT files and the specimens of Table III differ")
    # the contribution: each specimen once, from its original file, under the name entered
    thellier_meas = convert_tdt(pi_folder, "thellier",
                                rename={s: s + pub.THELLIER_SUFFIX for s in pi_files["original"]})
    thellier_meas["description"] = pd.Series(dtype=object)
    used_copies = dict(zip(pi_files.loc[pi_files["copy"], "file"], pi_files.loc[pi_files["copy"], "original"]))
    copies = []
    for stem in sorted(s for s in stems if COPY.match(s)):
        original = next(s for s in stems if s.lower() == COPY.match(stem).group(1).lower())
        o_rows = tdt_all[tdt_all["specimen"] == original]
        removed = removed_steps(o_rows, tdt_all[tdt_all["specimen"] == stem])
        labels = [f"{t - 273:.0f} °C {c.split(':')[0]}" for t, c in
                  zip(o_rows["treat_temp"].iloc[removed], o_rows["method_codes"].iloc[removed])]
        copies.append(dict(copy=stem, original=original, rows=len(o_rows), removed=len(removed),
                           steps=", ".join(labels), interpreted=stem in used_copies))
        if stem in used_copies:
            index = thellier_meas.index[thellier_meas["specimen"] == original + pub.THELLIER_SUFFIX][removed]
            thellier_meas.loc[index, "quality"] = "b"
            thellier_meas.loc[index, "description"] = (
                f"Not in the corrected copy {stem}.TDT of the archive, whose determination Table III gives; "
                "flagged bad.")
    copies = pd.DataFrame(copies)
    thellier_meas = mark_ltd(thellier_meas)
    thellier_meas["citations"] = "This study"
    lab_angle = lab_field_check(thellier_meas)
    thellier_check = recalculate_thellier(thellier_meas, pi_files)
    thellier_spec = thellier_specimen_rows(thellier_meas, pi_files)
    thellier_spec["sample"] = [thellier_sample(s, set(samp["sample"])) for s in pi_files["original"]]
    pi_site_check, accepted = thellier_site_checks(pi_files)
    # samples of the Thellier specimens that have no demagnetized specimen
    new_samples = []
    for sample in sorted(set(thellier_spec["sample"]) - set(samp["sample"])):
        site, t1 = site_of(sample), site_info(site_of(sample))
        block = sample.startswith("GTX") and len(sample) == 7 and site in pub.BLOCK_SITES + pub.UNORIENTED_SITES
        text = ("Unoriented hand block (text)" if site in pub.UNORIENTED_SITES else
                "Hand block, oriented in the field (text)" if block else "Core")
        new_samples.append(OrderedDict(
            sample=sample, site=site, method_codes="FS-H" if block else "FS-FD", lat=t1["lat"], lon=t1["lon"],
            citations="This study",
            description=f"{text}; named in the paleointensity files, which give no orientation, and with no "
                        "demagnetization file."))
    samp = pd.concat([samp, geology(pd.DataFrame(new_samples))], ignore_index=True)
    spec = pd.concat([spec, geology(thellier_spec)], ignore_index=True)
    meas = pd.concat([meas, thellier_meas], ignore_index=True)

    # ---- rock magnetism and thermal stability (VFTB): Table IV
    known = set(samp["sample"])
    rock_meas, rock_spec = build_rockmag(folder.parent / "ROCK MAG", known)
    rock_check = rockmag_parameters(rock_meas)
    ts_meas, ts_spec, ts_check, table_iv = build_thermal_stability(folder.parent / "THERMAL STABILITY", known)
    missing = sorted((set(rock_spec["sample"]) | set(ts_spec["sample"])) - known)
    if missing:
        new = [OrderedDict(sample=x, site=site_of(x), method_codes="FS-FD", lat=site_info(site_of(x))["lat"],
                           lon=site_info(site_of(x))["lon"], citations="This study",
                           description="Core named in the rock-magnetic files, with no demagnetization file.")
               for x in missing]
        samp = pd.concat([samp, geology(pd.DataFrame(new))], ignore_index=True)
    spec = pd.concat([spec, geology(rock_spec), geology(ts_spec)], ignore_index=True)
    meas = pd.concat([meas, rock_meas, ts_meas], ignore_index=True)

    # ---- site means (Table 2) and VGPs (Table 3)
    entries = []
    for c in chrm.itertuples():
        t = pub.TABLE_I[pub.TABLE_I["specimen"] == c.table_i].iloc[0]
        if t["discarded"]:
            continue
        if c.table_i in pub.TABLE_I_REFIT:
            nf = new_fits[(new_fits["table_i"] == c.table_i) & (new_fits["dir_tilt_correction"] == 0)].iloc[0]
            entries.append(dict(specimen=c.specimen, dec=nf["dir_dec"], inc=nf["dir_inc"]))
        else:
            f = geo.loc[c.index]
            entries.append(dict(specimen=c.specimen, dec=f["dir_dec"], inc=f["dir_inc"]))
    site_check = recalculate_sites(site_directions(pd.DataFrame(entries)))
    vgp_check = recalculate_vgps()

    sites = []
    for t1 in pub.TABLE1.itertuples():
        row = OrderedDict(site=t1.site, location=pub.LOCATION, result_type="i", citations="This study",
                          lat=t1.lat, lon=t1.lon, age=t1.age, age_low=t1.age - t1.age_pm, age_high=t1.age + t1.age_pm,
                          age_unit="ka", method_codes="", description=f"Locality: {t1.locality} (Table 1).")
        p = pub.TABLE2_DIRECTIONS[pub.TABLE2_DIRECTIONS["site"] == t1.site]
        if not p.empty:
            p = p.iloc[0]
            c = site_check[site_check["site"] == t1.site].iloc[0]
            t3 = pub.TABLE3[pub.TABLE3["site"] == t1.site].iloc[0]
            level = "hand blocks" if t1.site in pub.BLOCK_SITES else "samples (cores)"
            codes = set(":".join(spec[spec["specimen"].isin(c.specimens)]["method_codes"]).split(":"))
            lp = [x for x in ("LP-DIR-T", "LP-DIR-AF") if x in codes]
            row.update(dir_dec=p.dec, dir_inc=p.inc, dir_alpha95=p.a95, dir_n_samples=int(p.n),
                       dir_n_specimens=c.n_specimens, dir_tilt_correction=0,
                       vgp_lat=t3["vgp_lat"], vgp_lon=t3["vgp_lon"], vgp_dp=t3["dp"], vgp_dm=t3["dm"],
                       result_quality="g", method_codes=join(["DE-BFL", "DE-FM", "DE-VGP"] + lp + ["DA-DIR-GEO"]),
                       specimens=join(c.specimens), samples=join(sorted({core_of(s) for s in c.specimens})))
            if c.reproduced:
                row["dir_k"] = round(c.k, 1)
            text = (f" Direction (Table 2): hierarchical mean of {int(p.n)} {level}, each the Fisher mean of its "
                    f"specimens; ΔD {p.dD}°, ΔI {p.dI}° (97.5%, Demarest, 1983); n/N {int(p.n)}/{int(p.N)}.")
            text += (" Recalculated from the specimen fits to the printed precision; dir_k is recalculated."
                     if c.reproduced else
                     f" Not reproduced from the specimen fits: the closest recalculation is {c.dec:.1f}/{c.inc:.1f}, "
                     f"α95 {c.a95:.1f}° ({c.angle:.1f}° away).")
            text += " VGP from Table 3."
            row["description"] += text
        elif t1.site == "GTX06":
            row.update(result_quality="b", specimens=join(sorted(
                s for s in geo["specimen"].unique() if site_of(s) == "GTX06")))
            row["description"] += (f" No site mean (Table 2: 0/{pub.GTX06_N}): the specimens give anomalous "
                                   "directions and very low intensities, and only three are of normal polarity "
                                   "(text).")
        elif t1.site in pub.UNORIENTED_SITES:
            row["description"] += " Unoriented hand blocks, for paleointensity and rock magnetism only (text)."
        row["description"] += f" Age: {pub.DATING[t1.dating][1]}; the ± of Table 1 is entered as age_low and age_high."
        sites.append(row)
    sites = geology(pd.DataFrame(sites))
    if (sites["method_codes"] == "").any():
        sites.loc[sites["method_codes"] == "", "method_codes"] = "FS-FD"

    # site paleointensities (Table 2), one row each, with the VADM of Table 3
    intensity_rows, vadm_check = [], []
    table4 = pub.TABLE4.set_index("site")
    for p in pub.TABLE2_INTENSITIES.itertuples():
        t1, t3, t4 = site_info(p.site), pub.TABLE3[pub.TABLE3["site"] == p.site].iloc[0], table4.loc[p.site]
        a = accepted[accepted["site"] == p.site]
        names = [s + pub.THELLIER_SUFFIX for s in a["original"]]
        codes = ["LP-PI-TRM", "LP-PI-TRM-ZI", "LP-PI-ALT-PTRM", "IE-TT"] + (["LP-LT"] if (a["ltd"] == "yes").any()
                                                                           else [])
        check = pi_site_check[pi_site_check["site"] == p.site].iloc[0]
        vadm = pmag.b_vdm(p.B * 1e-6, t1["lat"]) / 1e22
        vadm_check.append(dict(site=p.site, B=p.B, lat=t1["lat"], vadm_pub=t3["vadm"], vadm=vadm,
                               sigma_pub=t3["vadm_sigma"], sigma=vadm * p.dB / p.B))

        def mean(label, b, db, n, N):
            n, N = int(n), int(N)
            return (f"{b:.1f}" + (f" ± {db:.1f}" if pd.notna(db) else "") + f" μT ({n}/{N} {label})"
                    if pd.notna(b) else f"none ({n}/{N} {label})")
        text = (f"Locality: {t1['locality']} (Table 1). Paleointensity (Table 2): mean and standard deviation of "
                f"the {int(p.n)} accepted Thellier-Coe determinations of Table III, n/N {int(p.n)}/{int(p.N)}. "
                f"Table 4: {mean('without LTD', t4.b_std, t4.db_std, t4.n_std, t4.N_std)}, "
                f"{mean('with LTD', t4.b_ltd, t4.db_ltd, t4.n_ltd, t4.N_ltd)}; classes A/B/C "
                f"{int(t4.class_a)}/{int(t4.class_b)}/{int(t4.class_c)}. VADM from Table 3.")
        if abs(check["B_all"] - p.B) > 0.051 or (pd.notna(p.dB) and abs(check["dB_all"] - p.dB) > 0.051):
            text += (f" From the determinations of Table III: {check['B_all']:.2f} ± {check['dB_all']:.2f} μT.")
        text += f" Age: {pub.DATING[t1['dating']][1]}; the ± of Table 1 is entered as age_low and age_high."
        intensity_rows.append(OrderedDict(
            site=p.site, location=pub.LOCATION, result_type="i", result_quality="g", citations="This study",
            lat=t1["lat"], lon=t1["lon"], age=t1["age"], age_low=t1["age"] - t1["age_pm"],
            age_high=t1["age"] + t1["age_pm"], age_unit="ka", method_codes=join(codes),
            int_abs=f"{p.B * 1e-6:.3e}", int_abs_sigma=f"{p.dB * 1e-6:.2e}", int_n_specimens=int(p.n),
            vadm=f"{t3['vadm'] * 1e22:.3e}", vadm_sigma=f"{t3['vadm_sigma'] * 1e22:.2e}",
            specimens=join(names), samples=join(sorted(set(thellier_spec.set_index("specimen").loc[names, "sample"]))),
            software_packages=pub.THELLIER_SOFTWARE, description=text))
    vadm_check = pd.DataFrame(vadm_check)
    sites = pd.concat([sites, geology(pd.DataFrame(intensity_rows))], ignore_index=True)

    # ---- selection criteria (Table II): class C, the threshold for acceptance
    criteria = pd.DataFrame([OrderedDict(
        criterion="IE-SPEC", table_column=f"specimens.{column}", criterion_operation=operation,
        criterion_value=pub.TABLE_II.set_index("class").loc["C", key], citations="This study",
        description=(f"Thellier-Coe determinations, {key}: class C, the threshold for acceptance (Table II); class A "
                     f"requires {operation} {pub.TABLE_II.set_index('class').loc['A', key]:g}, class B "
                     f"{operation} {pub.TABLE_II.set_index('class').loc['B', key]:g} (Paterson et al., 2014)."))
        for key, (column, operation) in pub.TABLE_II_COLUMNS.items()])

    # ---- ages (Table 1)
    ages = pd.DataFrame([OrderedDict(
        site=t.site, age=t.age, age_low=t.age - t.age_pm, age_high=t.age + t.age_pm, age_unit="ka",
        method_codes=pub.DATING[t.dating][0],
        citations="10.1016/j.qsa.2025.100267" if t.dating == "Ar" else "This study",
        description=f"{pub.DATING[t.dating][1]}, as given in Table 1 ({t.age} ± {t.age_pm} ka BP; the table does "
                    "not say what the uncertainty is).") for t in pub.TABLE1.itertuples()])

    # ---- location
    lats, lons = pub.TABLE1["lat"], pub.TABLE1["lon"]
    groups = "; ".join(f"{g.group} ({g.sites.replace(':', ', ')}): {g.pole_lat}°N, {g.pole_lon}°E, A95 {g.A95}°"
                       for g in pub.MEAN_POLES.itertuples())
    locations = pd.DataFrame([OrderedDict(
        location=pub.LOCATION, location_type="Region", result_type="i", citations="This study",
        geologic_classes=pub.GEOLOGIC_CLASSES, lithologies=pub.LITHOLOGIES,
        country="Spain", continent_ocean="Europe", lat_s=lats.min(), lat_n=lats.max(), lon_w=lons.min(),
        lon_e=lons.max(), age_low=float((pub.TABLE1["age"] - pub.TABLE1["age_pm"]).min()),
        age_high=float((pub.TABLE1["age"] + pub.TABLE1["age_pm"]).max()), age_unit="ka",
        sites=join(pub.TABLE1["site"]),
        description=("Fifteen Late Pleistocene lava flows of La Garrotxa Volcanic Field, NE Iberia. The paper gives "
                     "no mean direction for the field. Mean poles of sites with the same isotopic age (Table 3): "
                     f"{groups}; the authors use only the VGPs of single flows in the discussion."))])

    # ---- assemble, validate, write
    meas["sequence"] = range(1, len(meas) + 1)
    for table in (spec, samp, sites, ages, locations, criteria):
        whole_numbers(table)
    spec["description"] = spec["description"].replace("", np.nan)
    tables = OrderedDict(locations=locations, sites=sites, samples=samp, specimens=spec, measurements=meas,
                         ages=ages, criteria=criteria)
    with contextlib.redirect_stdout(io.StringIO()):
        write_upload_file(tables, BUILD_DIR, STUDY_DIR / "magic_contribution.txt")
    # the rules MagIC applies, on the upload file as written
    problems = validate_upload_file(STUDY_DIR / "magic_contribution.txt")

    # ================================================================ report
    rep = write_report(locals())
    (STUDY_DIR / "report.md").write_text("\n".join(rep) + "\n")
    # the "build" entry of study.json, from which the table of studies (studies.md) is made
    write_build_summary(STUDY_DIR, tables, len(problems), recalculated(locals()))
    print(f"{len(problems)} validation problems")
    for p in problems[:20]:
        print("  ", p)
    return 0 if not problems else 1


def recalculated(v):
    """One phrase per published result checked, for the "build" entry of study.json."""
    refits, table_i, sites, vgps = v["refits"], v["table_i_check"], v["site_check"], v["vgp_check"]
    th, ts = v["thellier_check"], v["ts_check"]
    t2 = v["pi_site_check"][v["pi_site_check"]["n_all_pub"] > 0]
    t2 = t2[t2["site"].isin(pub.TABLE2_INTENSITIES["site"])]
    pi_sites = (t2["n_all"] == t2["n_all_pub"]) & ((t2["B_all"] - t2["B_all_pub"]).abs() <= 0.051) & (
        (t2["dB_all"] - t2["dB_all_pub"]).abs() <= 0.051)
    vadm = ((v["vadm_check"]["vadm"] - v["vadm_check"]["vadm_pub"]).abs() <= 0.0051) & (
        (v["vadm_check"]["sigma"] - v["vadm_check"]["sigma_pub"]).abs() <= 0.0051)
    same_range = table_i["file_range"].str.replace(r" (°C|mT)$", "", regex=True) == table_i["table_range"]
    return [f"{int(refits['calculation'].isin(['free', 'anchored', 'origin']).sum())} of {len(refits)} stored fits",
            f"{int(((table_i['angle'] <= REPRODUCED) & same_range).sum())} of {len(table_i)} specimen fits of "
            "Table I",
            f"{int(sites['reproduced'].sum())} of {len(sites)} site directions",
            f"{int((vgps['angle'] <= 0.1).sum())} of {len(vgps)} VGPs",
            f"{int(th['B_agrees'].sum())} of {len(th)} Thellier-Coe determinations (Table III)",
            f"{int(pi_sites.sum())} of {len(pi_sites)} site paleointensities",
            f"{int(vadm.sum())} of {len(vadm)} VADMs",
            f"{int((ts['agrees'] == 'yes').sum())} of {int((ts['agrees'] != '').sum())} thermal-stability ratios "
            "(Table IV)"]


def write_report(v):
    """report.md: contents, checks against the paper, and what is missing."""
    spec, meas, refits, chrm = v["spec"], v["meas"], v["refits"], v["chrm"]
    files_check, table_i_check, site_check, vgp_check = (v["files_check"], v["table_i_check"], v["site_check"],
                                                         v["vgp_check"])
    rep = ["# La Garrotxa: build report\n",
           "Written by `convert.py`; do not edit. Study: Vernet et al. (2026), "
           f"doi:{pub.PAPER_DOI}; data doi:{pub.DATA_DOI}. `README.md` explains the sources and the decisions.\n",
           "## Contents of the contribution\n",
           "| Table | Rows | Source |", "| --- | --- | --- |",
           f"| measurements | {len(meas)}: {len(v['meas_2g'])} demagnetization steps from the 99 2G files (GTX sites), "
           f"{len(v['meas_rs3_ol'])} from the 35 `.rs3` files of the OL sites, {len(v['thellier_meas'])} Thellier-Coe "
           f"steps (`.TDT`), {len(v['rock_meas'])} points of rock-magnetic curves and {len(v['ts_meas'])} of "
           "thermal-stability cycles (VFTB) | files |",
           f"| specimens | {len(spec)} rows for {spec['specimen'].nunique()} specimens: {v['n_demag']} demagnetized "
           f"(the stored fits in specimen and geographic coordinates, and {len(v['new_fits'])} rows of a Table I fit "
           f"recalculated here), {len(v['thellier_spec'])} Thellier-Coe "
           f"({int(v['thellier_spec']['int_abs'].notna().sum())} with a determination of Table III), "
           f"{len(v['rock_spec'])} rock-magnetic powders, {len(v['ts_spec'])} thermal-stability pieces | files; Tables "
           "I, III and IV |",
           f"| samples | {len(v['samp'])} cores and hand blocks | files; text |",
           f"| sites | {len(v['sites'])}: {len(pub.TABLE1)} with the direction and VGP (13) or a description, and "
           f"{len(v['intensity_rows'])} paleointensities | Tables 1 to 4 |",
           "| locations | 1 | Tables 1 and 3 |",
           f"| ages | {len(v['ages'])} | Table 1 |",
           f"| criteria | {len(v['criteria'])} | Table II |", "",
           "## Validation with the rules of MagIC (`pmagpy.magic_validation`)\n",
           ("No problems.\n" if not v["problems"] else "\n".join(f"- {p}" for p in v["problems"]) + "\n"),
           "## Uploading to MagIC\n",
           "`magic_contribution.txt` holds every table except the contribution table, which is made on MagIC when "
           "the file is uploaded (the file is written with `ipmag.upload_magic`). Enter there:\n",
           f"- Reference: {pub.PAPER_DOI}",
           "- Laboratories: " + "; ".join(pub.LABORATORIES.split(":")),
           f"- Description: {pub.CONTRIBUTION_DESCRIPTION}\n",
           "`<permalink>` is the link to this study folder at the commit the upload is made from, so that it keeps "
           "pointing to the files that made the contribution. After committing and pushing, "
           f"`python common/studies.py --permalink {STUDY_DIR.name}` prints it; enter that commit as "
           "`upload_commit` in `study.json`.\n",
           "## The two kinds of direction files\n"]
    same = files_check["same_steps"]
    rep.append(f"The 99 GTX specimens have both a 2G binary file and a `.rs3` file. Read with "
               f"`convert_2_magic._2g_bin` and `convert_2_magic.rs3`, {int(same.sum())} have the same steps, "
               f"with directions within {files_check.loc[same, 'max_angle'].max():.2f}° and moments within "
               f"{100 * files_check.loc[same, 'max_moment_ratio'].max():.2f} percent. The others:\n")
    other = files_check[~same]
    rep.append(md_table(other.assign(extra=other["extra"].map(
        lambda e: ", ".join(f"{x[0] - 273:.0f} °C" if x[1] == "K" else f"{x[0] * 1e3:g} mT" for x in e))),
        ["specimen", "steps_2g", "steps_rs3", "repeats", "extra"]))
    orient = v["samp"].set_index("sample")[["azimuth", "dip"]]
    entered = files_check["specimen"].map(core_of).map(lambda c: tuple(orient.loc[c]))
    moved = files_check[[abs(a - e[0]) > 0.5 or abs(d - e[1]) > 0.5
                         for a, d, e in zip(files_check["azimuth_2g"], files_check["dip_2g"], entered)]]
    rep.append(f"\nThe orientation in the 2G header differs from the one entered for {len(moved)} specimens "
               f"({', '.join(moved['specimen'])}): all the specimens of GTX08 and GTX10, cores drilled in the "
               "laboratory from oriented blocks, whose `.rs3` files hold the orientation of each core. The "
               "directions of Table I follow the `.rs3` files. For core GTX0401 the `.rs3` files of its two "
               "specimens differ, and the orientation entered is the one with which Table I is reproduced, also "
               "that of the 2G files.\n")
    kinds = pd.Series([re.sub(r"\bfits? [\w, ]+? (is|are|has) ", r"fit \1 ", re.sub(r"^-W- [^:]+: (\d+ )?", "", w))
                       for w in v["rs3_warnings"]]).value_counts()
    rep.append(f"Warnings of the converters: {len(v['rs3_warnings'])} from `rs3` ("
               + "; ".join(f"{n} × \"{k}\"" for k, n in kinds.items())
               + f"), {len(v['warnings_2g'])} from `_2g_bin`.\n")
    rep.append("## Stored fits recalculated\n")
    counts = refits["calculation"].value_counts()
    rep.append(f"{len(refits)} stored line fits, recalculated from the measurements entered between their stated "
               f"limits: " + ", ".join(f"{n} as a {k} line" if k in ("free", "anchored") else
                                       (f"{n} with the origin added as a point" if k == "origin" else f"{n} {k}")
                                       for k, n in counts.items()) + ".\n")
    rep.append(md_table(refits.groupby(["flag", "calculation"]).size().reset_index(name="fits"),
                        ["flag", "calculation", "fits"]))
    rep.append("\n`flag` is the Remasoft line flag in the file. `convert_2_magic.rs3` recalculates each stored line "
               "with `pmag.domean` and writes it as the calculation that reproduces it: the fits flagged O are "
               "anchored lines, entered as DE-BFL-A (README.md, item 8).\n")
    odd = refits[(refits["calculation"] == "not reproduced") | refits["earlier_start"]]
    rep.append(md_table(odd, ["specimen", "dir_comp", "calculation", "earlier_start", "angle", "stored_mad", "mad"],
                        {"angle": ".2f"}))
    rep.append("\n## Table I against the stored fits\n")
    rep.append(f"For each of the {len(table_i_check)} specimens of Table I, the stored geographic fit closest to "
               f"the printed direction. {int((table_i_check['angle'] <= REPRODUCED).sum())} agree within "
               f"{REPRODUCED}°. Differences:\n")
    diff = table_i_check[(table_i_check["angle"] > REPRODUCED) | (table_i_check["n_fit"] != table_i_check["n_table"])
                         | (table_i_check["file_line"] != table_i_check["table_line"])
                         | ((table_i_check["mad_file"] - table_i_check["mad_table"]).abs() > MAD_TOLERANCE)]
    rep.append(md_table(diff, ["specimen", "file_range", "table_range", "file_line", "table_line", "n_fit", "n_table",
                               "angle", "mad_file", "mad_table", "discarded"], {"angle": ".2f", "n_fit": ".0f"}))
    rep.append("\n`n_fit` is the number of measurements between the limits, with which the stored line is "
               "reproduced. `file_line` is the flag in the file.\n")
    rep.append("## Site means (Table 2)\n")
    rep.append("Hierarchical Fisher means of the characteristic fits that Table I does not discard: the specimens "
               "of each core (each hand block for GTX08 and GTX10) averaged first.\n")
    rep.append(md_table(site_check, ["site", "dec_pub", "inc_pub", "a95_pub", "n_pub", "dec", "inc", "a95", "k", "n",
                                     "n_specimens", "angle", "reproduced"], {"angle": ".2f"}))
    rep.append("\n## VGPs (Table 3)\n")
    rep.append("From the published site mean and the site coordinates of Table 1 (`pmag.dia_vgp`):\n")
    rep.append(md_table(vgp_check, ["site", "lat_pub", "lon_pub", "dp_pub", "dm_pub", "lat", "lon", "dp", "dm",
                                    "angle"], {"dp": ".2f", "dm": ".2f", "angle": ".2f", "dp_pub": ".2f",
                                               "dm_pub": ".2f"}))
    # ---- paleointensity
    th, copies, pi_files = v["thellier_check"], v["copies"], v["pi_files"]
    rep.append("\n## Thellier-Coe files\n")
    n_ltd = int((pi_files["ltd"] == "yes").sum())
    rep.append(f"The archive holds {len(pi_files) + len(copies)} `.TDT` files: {len(pi_files)} specimens "
               f"({len(pi_files) - n_ltd} standard Thellier-Coe experiments, {n_ltd} with a low-temperature "
               f"demagnetization after each heating step, `LTD_*.TDT`), the {len(pi_files)} rows of Table III, and "
               f"{len(copies)} corrected copies (`*_C.TDT`, `*_CC.TDT`) of {copies['original'].nunique()} of them. "
               "They are converted with `convert_2_magic.tdt` (each specimen named after its file, moments in A/m, "
               f"laboratory field along −Z). The median direction of the pTRMs gained by a specimen is within 10° of "
               f"−Z for {int((v['lab_angle'] <= 10).sum())} of the {len(v['lab_angle'])} specimens, and at most "
               f"{v['lab_angle'].max():.1f}° from it ({v['lab_angle'].idxmax()}).\n")
    rep.append("Each corrected copy is its original file with the measurements listed deleted, and the others "
               "unchanged. Where Table III names the copy (`interpreted`), the specimen is entered from its "
               "original file and those measurements are flagged bad; the other copies are not entered.\n")
    rep.append(md_table(copies, ["copy", "original", "rows", "removed", "steps", "interpreted"]))
    rep.append("\nTable III against the converted measurements: best-fit line of the Arai plot over the printed "
               "range (`pmag.sortarai`, `pmag.PintPars`), from the measurements flagged good, and the anchored MAD "
               "of the same steps (`pmag.domean`). δ(CK) and α are entered as printed and not recalculated. "
               "`B_agrees`: N, B within 0.05 μT (0.1 percent above 50 μT) and β within 0.0015; `fq_agree`: f within "
               "0.025 and q within 3 percent; `mad_agrees`: MAD within 0.05°. The rows where all agree are not "
               "shown.\n")
    rep.append(md_table(th[~(th["B_agrees"] & th["fq_agree"] & th["mad_agrees"])],
                        ["specimen", "cls", "range", "N_pub", "N", "B_pub", "B", "dB_pub", "dB", "beta_pub", "beta",
                         "f_pub", "f", "q_pub", "q", "mad_pub", "mad", "B_agrees", "fq_agree", "mad_agrees"],
                        {"B": ".2f", "dB": ".2f", "beta_pub": ".3f", "beta": ".3f", "f_pub": ".2f", "f": ".2f",
                         "q_pub": ".2f", "q": ".2f", "mad_pub": ".2f", "mad": ".2f", "B_pub": ".2f",
                         "dB_pub": ".2f"}))
    good = th[th["cls"] != "R"]
    rep.append(f"\n{int(th['B_agrees'].sum())} of {len(th)} determinations recalculate in N, B and β "
               f"({int(good['B_agrees'].sum())} of the {len(good)} accepted); {int((th['B_agrees'] & th['fq_agree']).sum())} "
               f"also in f and q ({int((good['B_agrees'] & good['fq_agree']).sum())} of the accepted). The anchored "
               f"MAD agrees for {int(th['mad_agrees'].sum())}.\n")
    rep.append("## Site paleointensities (Tables 2 and 4)\n")
    rep.append("Mean and standard deviation of the published B of the accepted determinations of Table III (classes "
               "A to C), all together (`all`), without LTD (`std`) and with LTD (`ltd`), against Table 4 (`_pub`; "
               "the `all` columns are also those of Table 2). `N`: specimens in Table III and the files.\n")
    rep.append(md_table(v["pi_site_check"], ["site", "n_all_pub", "n_all", "B_all_pub", "B_all", "dB_all_pub", "dB_all",
                                             "n_std_pub", "n_std", "B_std_pub", "B_std", "dB_std_pub", "dB_std",
                                             "n_ltd_pub", "n_ltd", "B_ltd_pub", "B_ltd", "dB_ltd_pub", "dB_ltd",
                                             "classes_pub", "classes", "N_pub", "N"],
                        {c: ".2f" for c in ("B_all", "dB_all", "B_std", "dB_std", "B_ltd", "dB_ltd")}))
    rep.append("\nVADMs (Table 3) from the published site paleointensity and the site latitude (`pmag.b_vdm`), in "
               "10²² Am²; `sigma` is the VADM times ΔB/B:\n")
    rep.append(md_table(v["vadm_check"], ["site", "B", "lat", "vadm_pub", "vadm", "sigma_pub", "sigma"],
                        {"lat": ".4f", "vadm": ".2f", "sigma": ".2f", "vadm_pub": ".2f", "sigma_pub": ".2f"}))
    # ---- rock magnetism
    rock, ts = v["rock_check"], v["ts_check"]
    counts = v["rock_meas"].groupby(v["rock_meas"]["method_codes"].str.split(":").str[0]).agg(
        curves=("experiment", "nunique"), points=("experiment", "size"))
    rep.append("\n## Rock-magnetic files\n")
    rep.append(f"{len(v['rock_spec'])} powders, each with four VFTB curves, converted with `convert_2_magic.vftb`: "
               + "; ".join(f"{code} {r.curves} curves, {r.points} points" for code, r in counts.iterrows())
               + f". Each powder is entered with the suffix `{pub.ROCKMAG_SUFFIX}`, in the sample of its core. The "
               "paper gives no rock-magnetic values per sample (only the Day plot of Fig. 2C), so none is entered. For "
               "the record, and as a check of PmagPy on these curves:\n")
    rep.append(md_table(rock, ["specimen", "points", "bcr", "ms", "ms_branch", "mr", "mr_branch", "bc", "bc_branch",
                               "mr_ms", "bcr_bc"],
                        {"bcr": ".1f", "ms": ".3f", "ms_branch": ".3f", "mr": ".3f", "mr_branch": ".3f", "bc": ".1f",
                         "bc_branch": ".1f", "mr_ms": ".3f", "bcr_bc": ".2f"}))
    rep.append(f"\nMoments in Am²/kg, fields in mT. `bcr`: zero crossing of the back-field curve "
               "(`rockmag.process_backfield_data`, which needs the fix of PmagPy issue #1049 for curves that start at "
               "zero field). `ms`, `mr`, `bc`: `rockmag.process_hyst_loop` (which needs the initial curve of the "
               "file to be left out, the second point of issue #1048); `_branch`: read from the measured branches "
               "after removing the high-field slope above 60 percent of the peak field. `process_hyst_loop` gives "
               f"Mr {100 * (rock['mr'] / rock['mr_branch'] - 1).min():.0f} to "
               f"{100 * (rock['mr'] / rock['mr_branch'] - 1).max():.0f} percent and Bc "
               f"{100 * (rock['bc'] / rock['bc_branch'] - 1).min():.0f} to "
               f"{100 * (rock['bc'] / rock['bc_branch'] - 1).max():.0f} percent from the branch values, and Ms "
               f"{100 * (rock['ms'] / rock['ms_branch'] - 1).min():.1f} to "
               f"{100 * (rock['ms'] / rock['ms_branch'] - 1).max():.1f} percent: the loops have "
               f"{rock['points'].min()} to {rock['points'].max()} points, unevenly spaced, which the function "
               "resamples on an even grid (the first point of issue #1048). `mr_ms` and `bcr_bc` are from the "
               "branch values.\n")
    rep.append("## Thermal stability (Table IV)\n")
    rep.append(f"{ts['file'].str.contains('/').__invert__().sum()} magnetization-temperature cycles, converted with "
               "`convert_2_magic.vftb`, for the rows of Table IV. MAGF/MAGI is recalculated as the magnetization at "
               "the end of the cooling branch over that of the heating branch at the same temperature, linearly "
               "interpolated; MAG2F/MAG1I the same with the end of the second cycle and the start of the first. "
               "`agrees`: within 0.005.\n")
    rep.append(md_table(ts, ["row", "kind", "file", "specimen", "weight_mg", "T_pub", "T", "ratio_pub", "ratio",
                             "agrees"], {"weight_mg": ".0f", "T_pub": ".0f", "T": ".0f", "ratio_pub": ".3f",
                                         "ratio": ".3f"}))
    has_pub = ts[ts["ratio_pub"].notna()]
    rep.append(f"\n{int((has_pub['agrees'] == 'yes').sum())} of {len(has_pub)} printed ratios recalculate within 0.005. "
               "For GTX0505 the cycle to 500 °C gives the ratio printed for T3 (600 °C) and the cycle to 600 °C the "
               "one printed for T1 (500 °C). Table IV prints no ratio for OLO106.\n")
    rep.append("\n## Information that would complete the contribution\n")
    rep.append("- What the ± of the ages in Table 1 is (one or two standard deviations).")
    rep.append("- The unit of the moments of the `.TDT` files (entered as A/m) and the volumes of the microcores.")
    rep.append("- Whether the NRM of the LTD specimens was measured after a low-temperature demagnetization.")
    rep.append("- The ninth Thellier-Coe specimen of OL03 (Tables 2 and 4 count 9; Table III and the archive have 8).")
    rep.append("- What the second sets of rock-magnetic curves (`_MAL`) of GTX0208B and GTX0307inf are.")
    rep.append("- The rock-magnetic parameters of each powder, which the paper plots (Fig. 2C) but does not list.")
    return rep


if __name__ == "__main__":
    sys.exit(main())
