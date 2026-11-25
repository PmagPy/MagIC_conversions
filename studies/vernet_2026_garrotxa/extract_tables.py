"""Extract Tables III and IV of the appendix of Vernet et al. (2026) from the PDF to CSV files.

Table III ("Thellier-Coe paleointensity results per specimen ordered by site") and Table IV
("Results of the thermal stability experiments on specimens with accepted paleointensity
estimations") are printed on pages IV to VII of the paper. The PDF is downloaded from the
journal into build/ and checked against its checksum, its text is taken with pdftotext
(poppler) in layout mode, and every line that is a row of a table is written to the CSV, in
the order and with the digits of the PDF:

    table_iii.csv   one row per specimen: LTD (yes or empty), specimen, Tmin, Tmax, N, beta,
                    f, q, dCK, alpha95, MAD', B, dB, class, observations; the numbers are
                    empty for the specimens the table gives none
    table_iv.csv    one row per specimen: specimen, Tmin, Tmax, then T, phases and MAGF/MAGI
                    of each of the three partial curves, MAG2F/MAG1I, and a note ("Rejected",
                    "No data"); empty where the table gives none

The paper is licensed CC BY-SA 4.0. The CSV files are kept in the repository: convert.py
reads them and does not need pdftotext. Run this script only to make them again:

    python extract_tables.py

Requires pdftotext (poppler-utils) and requests.
"""

import csv
import hashlib
import re
import subprocess
from pathlib import Path

import requests

STUDY_DIR = Path(__file__).resolve().parent
PDF_URL = "https://revistes.ub.edu/index.php/GEOACTA/article/download/52574/47873"
PDF_SHA256 = "43787a91083db460b6896065ac944dd3ece3522a92ec4eb797c88b48d7e1bf71"
PDF = STUDY_DIR / "build" / "Vernet2026_GeologicaActa.pdf"

TABLE_III_COLUMNS = ["ltd", "specimen", "t_min", "t_max", "n", "beta", "f", "q", "dck", "alpha95", "mad", "b",
                     "db", "class", "observations"]
NUMBER = r"(\d+(?:\.\d+)?)"
# [LTD] specimen  Tmin-Tmax  N  beta  f  q  dCK  alpha95  MAD'  B  dB  class  [observations]
TABLE_III_ROW = re.compile(r"^\s*(LTD\s+)?((?:GTX|OL)\w+)\s+(\d+)-(\d+)\s+" + r"\s+".join([NUMBER] * 9)
                           + r"\s+([ABCR])\b\s*(.*?)\s*$")
# [LTD] specimen  [-  -]  R  observations: no determination (B and dB printed as "-", or blank)
TABLE_III_EMPTY = re.compile(r"^\s*(LTD\s+)?((?:GTX|OL)\w+)\s+(?:-\s+-\s+)?(R)\s+(.*?)\s*$")

TABLE_IV_COLUMNS = ["specimen", "t_min", "t_max", "t1", "t1_phases", "mag1f_mag1i", "t2", "t2_phases",
                    "mag2f_mag2i", "t3", "t3_phases", "mag3f_mag3i", "mag2f_mag1i"]


def download_pdf():
    """The paper as published, downloaded once into build/ and checked against PDF_SHA256."""
    if not PDF.exists():
        PDF.parent.mkdir(exist_ok=True)
        response = requests.get(PDF_URL, timeout=120)
        response.raise_for_status()
        PDF.write_bytes(response.content)
    digest = hashlib.sha256(PDF.read_bytes()).hexdigest()
    if digest != PDF_SHA256:
        raise ValueError(f"{PDF.name}: SHA-256 {digest}, expected {PDF_SHA256}")
    return PDF


def table_lines(text, title, end):
    """The lines of the text from the caption of a table to the next caption (or the end)."""
    start = text.index(title)
    stop = text.find(end, start + len(title)) if end else -1
    return text[start:stop if stop > 0 else None].splitlines()


def read_table_iii(text):
    rows, skipped = [], []
    for line in table_lines(text, "TABLE III. Thellier-Coe", "TABLE IV."):
        match = TABLE_III_ROW.match(line)
        empty = TABLE_III_EMPTY.match(line)
        if match:
            g = match.groups()
            rows.append(["yes" if g[0] else "", g[1], *g[2:14], g[14]])
        elif empty:
            g = empty.groups()
            rows.append(["yes" if g[0] else "", g[1]] + [""] * 11 + [g[2], g[3]])
        elif re.match(r"^\s*(LTD\s+)?(GTX|OL)\d", line):
            skipped.append(line)
    if skipped:
        raise ValueError("lines that begin like a row of Table III but were not read:\n" + "\n".join(skipped))
    return rows


def read_table_iv(text):
    """Rows of Table IV. Its columns are often empty, so a value is assigned to the column under which it is
    printed: the left edge of each column on the printed line (pdftotext -layout) is in TABLE_IV_EDGES.

    Two lines are not rows of their own: a "Yes" printed alone on the line above GTX0505 is its T1 phases,
    and "Rejected" (GTX1003) and "No data" (OLO202, OLO401) are kept in the column `note`.
    """
    rows, pending = [], {}
    for line in table_lines(text, "TABLE IV. Results of the thermal", None):
        tokens = [(m.start(), m.group()) for m in re.finditer(r"No data|\S+", line.rstrip())]
        if [t for _, t in tokens] == ["Yes"]:
            pending = {TABLE_IV_COLUMNS[_column(tokens[0][0])]: "Yes"}
            continue
        if not re.match(r"^\s*(GTX|OL|OLO)\d", line):
            continue
        row = dict.fromkeys(TABLE_IV_COLUMNS + ["note"], "")
        row.update(pending)
        pending = {}
        for position, token in tokens:
            if token in ("Rejected", "No data"):
                row["note"] = token
            else:
                # a value printed close to the one before it (GTX1001: "320 520") goes to the next column
                k = _column(position)
                while row[TABLE_IV_COLUMNS[k]]:
                    k += 1
                row[TABLE_IV_COLUMNS[k]] = token
        rows.append([row[c] for c in TABLE_IV_COLUMNS + ["note"]])
    return rows


# the left edge of each column of Table IV on the line of pdftotext -layout, in the order of TABLE_IV_COLUMNS
TABLE_IV_EDGES = [0, 27, 33, 39, 45, 57, 66, 74, 86, 100, 109, 120, 134]


def _column(position):
    return max(k for k, edge in enumerate(TABLE_IV_EDGES) if position >= edge)


def main():
    text = subprocess.run(["pdftotext", "-layout", str(download_pdf()), "-"], check=True, capture_output=True,
                          text=True).stdout
    rows = read_table_iii(text)
    names = [(row[0], row[1]) for row in rows]
    if len(set(names)) != len(names):
        raise ValueError("a specimen occurs twice in Table III")
    with open(STUDY_DIR / "table_iii.csv", "w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(TABLE_III_COLUMNS)
        writer.writerows(rows)
    print(f"{len(rows)} rows written to table_iii.csv")
    rows = read_table_iv(text)
    with open(STUDY_DIR / "table_iv.csv", "w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(TABLE_IV_COLUMNS + ["note"])
        writer.writerows(rows)
    print(f"{len(rows)} rows written to table_iv.csv")


if __name__ == "__main__":
    main()
