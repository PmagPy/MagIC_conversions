"""Shared helpers for the study conversions: reading MagIC tables, Markdown tables, and validation.

The upload file itself is written with ipmag.upload_magic.

The validation follows the rules stored in the MagIC data model itself
(required columns, controlled vocabularies, numeric ranges, references between
tables) plus the method codes and the links between the levels of the
hierarchy. It reads three files kept in `common/resources/`:

    magic_data_model_3.0_2026-10-22.json   https://earthref.org/MagIC/data-models/3.0.json
    magic_method_codes_2026-10-22.json     https://www2.earthref.org/MagIC/method-codes.json
    earthref_controlled_vocabularies.json  https://www2.earthref.org/vocabularies/controlled
                                           (downloaded 2026-10-17)

It is a local check. A contribution should also be run through MagIC's own
validation when it is uploaded to a private workspace.

Requires numpy and pandas.
"""

import json
import re
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd

RESOURCES = Path(__file__).resolve().parent / "resources"
DATA_MODEL_DATE = "2026-10-22"
DATA_MODEL_FILE = RESOURCES / f"magic_data_model_3.0_{DATA_MODEL_DATE}.json"
METHOD_CODES_FILE = RESOURCES / f"magic_method_codes_{DATA_MODEL_DATE}.json"
VOCABULARIES_FILE = RESOURCES / "earthref_controlled_vocabularies.json"


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


# ---------------------------------------------------------------- validation

def is_blank(value):
    return value is None or (isinstance(value, float) and np.isnan(value)) or str(value).strip() == ""


def filled(value):
    return not is_blank(value)


def num(value):
    """A value as a float, or None if it is blank or not a number."""
    if is_blank(value):
        return None
    try:
        return float(str(value).strip())
    except ValueError:
        return None


def load_resources():
    """Read the data model, the controlled vocabularies and the method codes.

    Returns:
        (data_model, vocabularies, method_codes): the data model as a dict;
        vocabularies as a dict of vocabulary name to set of items; method codes
        as a set.
    """
    dm = json.load(open(DATA_MODEL_FILE, encoding="utf-8-sig"))
    cv_raw = json.load(open(VOCABULARIES_FILE, encoding="utf-8-sig"))
    vocab = {}
    for key, value in cv_raw.items():
        items = value.get("items", value) if isinstance(value, dict) else value
        if isinstance(items, list):
            vocab[key] = {str(i["item"] if isinstance(i, dict) and "item" in i else i) for i in items}
    codes = set()

    def walk(obj):
        if isinstance(obj, dict):
            if isinstance(obj.get("code"), str):
                codes.add(obj["code"])
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)
    walk(json.load(open(METHOD_CODES_FILE, encoding="utf-8-sig")))
    return dm, vocab, codes


def validate(tables, dm, vocab, method_codes):
    """Check required fields, vocabularies, ranges, method codes and links.

    Args:
        tables: dict of table name to DataFrame.
        dm, vocab, method_codes: from load_resources.

    Returns:
        list of problems as strings; empty if none.
    """
    problems = []
    for table, df in tables.items():
        model = dm["tables"][table]["columns"]
        for col in df.columns:
            if col not in model:
                problems.append(f"{table}: column '{col}' is not in the data model.")
        for col, spec in model.items():
            for rule in spec.get("validations") or []:
                name, arg = re.match(r"(\w+)\((.*)\)", rule).groups()
                args = [a.strip().strip('"') for a in arg.split(",")] if arg else []
                for i, row in df.iterrows():
                    label = f"{table} row {i + 1} ({row.iloc[0]})"
                    value = row.get(col)
                    if name == "required" or name.startswith("requiredUnlessSynthetic"):
                        if not filled(value):
                            problems.append(f"{label}: required '{col}' is empty.")
                    elif name == "requiredUnless":
                        if not filled(value) and not all(filled(row.get(a)) for a in args):
                            problems.append(f"{label}: '{col}' is required unless {args} are given.")
                    elif name == "requiredUnlessTable":
                        if not filled(value) and args[0] not in tables:
                            problems.append(f"{label}: '{col}' is required without a {args[0]} table.")
                    elif name == "requiredIf":
                        if not filled(value) and filled(row.get(args[0])):
                            problems.append(f"{label}: '{col}' is required when '{args[0]}' is given.")
                    elif not filled(value):
                        continue
                    elif name == "cv" and args[0] in vocab:
                        for item in str(value).split(":"):
                            if item not in vocab[args[0]]:
                                problems.append(f"{label}: '{item}' is not in the '{args[0]}' "
                                                f"vocabulary ({col}).")
                    elif name in ("min", "max"):
                        x = num(value)
                        # limits are numbers or other columns, e.g. max("lat_n")
                        limit = num(args[0]) if num(args[0]) is not None else num(row.get(args[0]))
                        if x is not None and limit is not None and \
                                ((name == "min" and x < limit) or (name == "max" and x > limit)):
                            problems.append(f"{label}: {col} = {value} violates {rule}.")
                    elif name == "in":
                        ref_table, ref_col = args[0].split(".")
                        refs = set(tables[ref_table][ref_col]) if ref_table in tables else set()
                        for item in str(value).split(":"):
                            if item not in refs:
                                problems.append(f"{label}: '{item}' ({col}) not found in {args[0]}.")
        if "method_codes" in df.columns:
            for i, value in df["method_codes"].items():
                for code in str(value).split(":") if filled(value) else []:
                    if code not in method_codes:
                        problems.append(f"{table} row {i + 1}: unknown method code '{code}'.")
    # links between the levels of the hierarchy
    links = [("measurements", "specimen", "specimens", "specimen"),
             ("specimens", "sample", "samples", "sample"),
             ("samples", "site", "sites", "site"),
             ("sites", "location", "locations", "location")]
    for child, col, parent, pcol in links:
        if child in tables and parent in tables:
            missing = set(tables[child][col].dropna()) - set(tables[parent][pcol])
            for m in sorted(missing):
                problems.append(f"{child}: {col} '{m}' has no row in {parent}.")
    return list(OrderedDict.fromkeys(problems))
