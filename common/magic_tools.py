"""Shared helpers for the study conversions: reading a MagIC table, writing the upload
file, validating it, and writing a Markdown table for a report.

Conversion, calculation and validation are done with PmagPy
(pmagpy.convert_2_magic, pmagpy.pmag, pmagpy.ipmag, pmagpy.magic_validation);
the helpers here only call it the same way in every study. Anything else that
a second study would need belongs in PmagPy.

Requires numpy, pandas and pmagpy.
"""

import shutil
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------- reading

def read_magic_table(path):
    """Read one MagIC table file (a "tab delimited" line, then a header) as strings."""
    return pd.read_csv(path, sep="\t", header=1, dtype=object, keep_default_na=False, na_values=[""])


def md_table(df, columns, formats=None):
    """A DataFrame as a Markdown table; floats use formats[column], default one decimal."""
    formats = formats or {}
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for _, r in df.iterrows():
        cells = []
        for c in columns:
            v = r[c]
            if isinstance(v, (float, np.floating)):
                cells.append("" if np.isnan(v) else format(v, formats.get(c, ".1f")))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ---------------------------------------------------------------- writing and validating

def whole_numbers(df):
    """Write columns of whole numbers without a decimal point (6, not 6.0), keeping blanks."""
    for column in df.columns:
        values = df[column]
        if values.dtype.kind == "f" and values.notna().any() and (values.dropna() % 1 == 0).all():
            df[column] = values.astype("Int64")
    return df


def write_upload_file(tables, build_dir, path):
    """Write the tables as one MagIC upload file with ipmag.upload_magic.

    The contribution table (reference, laboratories, description) is not part
    of an upload file: it is made on MagIC when the file is uploaded, from the
    values that a study's report.md lists under "Uploading to MagIC".

    Args:
        tables (dict): MagIC table name to DataFrame.
        build_dir (Path): the study's build folder; the tables are written to build_dir/upload.
        path (Path): where to put the upload file.
    """
    from pmagpy import ipmag, pmag

    upload_dir = Path(build_dir) / "upload"
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


def validate_upload_file(path):
    """Validate an upload file with the rules MagIC applies (pmagpy.magic_validation).

    Returns:
        list of str: one line per problem (errors and warnings); empty if there are none.
    """
    from pmagpy import magic_validation

    found = magic_validation.validate(str(path))
    return [f"{r.level}: {r.table}.{r.column}: {r.message}" + (f" (rows {r.rows})" if len(str(r.rows)) else "")
            for r in found.itertuples()]
