"""Extract Table S3 of the supplement of Yuan et al. (2025) from the PDF to table_s3.csv.

Table S3 ("High-temperature component directions of all specimens from the Zhangda
section") is printed over several pages of data/supplementary_materials.pdf. The text
of the PDF is taken with pdftotext (poppler) in layout mode, and every line that is a
row of the table (a specimen name, seven numbers and the demagnetization type) is
written to the CSV, in the order and with the digits of the PDF.

table_s3.csv is kept in the repository: convert.py reads it and does not need pdftotext.
Run this script only to make the CSV again:

    python extract_table_s3.py

Requires pdftotext (poppler-utils).
"""

import csv
import re
import subprocess
from pathlib import Path

STUDY_DIR = Path(__file__).resolve().parent
PDF = STUDY_DIR / "data" / "supplementary_materials.pdf"
CSV = STUDY_DIR / "table_s3.csv"

# Dg, Ig (in situ) and Ds, Is (tilt-corrected) of the table
COLUMNS = ["specimen", "strike", "dip", "dec_insitu", "inc_insitu", "dec_tilt", "inc_tilt", "mad", "demag"]
NUMBER = r"(-?\d+\.\d)"
ROW = re.compile(r"^\s*(zl\d+-[\d-]+)\s+" + r"\s+".join([NUMBER] * 7) + r"\s+(Th)\s*$")


def main():
    text = subprocess.run(["pdftotext", "-layout", str(PDF), "-"], check=True, capture_output=True,
                          text=True).stdout
    start = text.index("Table S3.")
    rows, skipped = [], []
    for line in text[start:].splitlines():
        match = ROW.match(line)
        if match:
            rows.append(match.groups())
        elif re.match(r"^\s*zl\d", line, flags=re.IGNORECASE):
            skipped.append(line)
    if skipped:
        raise ValueError("lines that begin like a row of Table S3 but were not read:\n" + "\n".join(skipped))
    names = [row[0] for row in rows]
    if len(set(names)) != len(names):
        raise ValueError("a specimen name occurs twice")
    with open(CSV, "w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(COLUMNS)
        writer.writerows(rows)
    print(f"{len(rows)} rows written to {CSV.name}")


if __name__ == "__main__":
    main()
