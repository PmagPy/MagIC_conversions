"""Shared helpers for the study conversions: reading a MagIC table and writing a Markdown table.

Conversion, calculation and validation are done with PmagPy
(pmagpy.convert_2_magic, pmagpy.pmag, pmagpy.ipmag, pmagpy.magic_validation);
the upload file is written with ipmag.upload_magic. Anything a second study
would need beyond these two helpers belongs in PmagPy.

Requires numpy and pandas.
"""

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
