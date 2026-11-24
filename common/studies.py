"""The study records (`study.json`) and the table of studies built from them (`studies.md`).

Each study folder has a `study.json` with two kinds of entries:

    entered by hand     what the study is and where it stands: citation, DOIs, formats,
                        tier, status, MagIC contribution, date the authors were contacted
    "build"             written by the study's convert.py each time it runs (PmagPy version,
                        rows of each table, validation problems, what recalculates);
                        never edited by hand

Run from the repository root to rewrite `studies.md`:

    python common/studies.py

`python common/studies.py --check` writes nothing and exits with an error if `studies.md`
is not what the study records give (for use before a commit or in continuous integration).

`python common/studies.py --permalink <study folder>` prints the link to a study folder at
the current commit, for the description of its MagIC contribution.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parents[1]
STUDIES_DIR = REPO_DIR / "studies"
STUDIES_TABLE = REPO_DIR / "studies.md"
REPO_URL = "https://github.com/PmagPy/MagIC_conversions"

# Entries of study.json that are entered by hand; None is allowed where noted.
REQUIRED = ("citation", "year", "title", "journal", "paper_doi", "formats", "tier", "status",
            "magic_contribution_id", "authors_contacted")
# The tier of a study is the most detailed MagIC table that the available data fill; the tables above
# it in the hierarchy are filled as well.
#   measurements: laboratory files, converted with pmagpy.convert_2_magic
#   specimens:    specimen directions or results in a table of the paper or its supplement
#   samples:      sample directions or results in a table
#   sites:        site means only
#   locations:    a mean direction or pole only
TIERS = ("measurements", "specimens", "samples", "sites", "locations")


def write_build_summary(study_dir, tables, validation_problems, recalculates):
    """Write the "build" entry of a study's study.json, leaving the other entries as they are.

    Called at the end of a study's convert.py.

    Args:
        study_dir (Path): the study folder.
        tables (dict): MagIC table name to DataFrame, as written to the upload file.
        validation_problems (int): number of problems found by the validation.
        recalculates (list of str): one phrase per published result that was checked,
            e.g. "11 of 11 flow directions".
    """
    from pmagpy import version as pmagpy_version  # here, so that building studies.md does not need PmagPy

    path = Path(study_dir) / "study.json"
    study = json.loads(path.read_text(encoding="utf-8"))
    study["build"] = {
        "pmagpy_version": pmagpy_version.version.replace("pmagpy-", ""),
        "rows": {name: int(len(table)) for name, table in tables.items()},
        "validation_problems": int(validation_problems),
        "recalculates": list(recalculates),
    }
    path.write_text(json.dumps(study, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_studies():
    """Read every studies/*/study.json.

    Returns:
        list of (str, dict): folder name and study record, ordered by first author and year.

    Raises:
        ValueError: if a study folder has no study.json, or a record lacks a required entry.
    """
    studies = []
    for folder in sorted(p for p in STUDIES_DIR.iterdir() if p.is_dir()):
        path = folder / "study.json"
        if not path.exists():
            raise ValueError(f"{folder.name}: no study.json")
        study = json.loads(path.read_text(encoding="utf-8"))
        missing = [key for key in REQUIRED if key not in study]
        if missing:
            raise ValueError(f"{folder.name}/study.json lacks: {', '.join(missing)}")
        if study["tier"] not in TIERS:
            raise ValueError(f"{folder.name}/study.json: tier must be one of {', '.join(TIERS)}")
        studies.append((folder.name, study))
    return sorted(studies, key=lambda item: (item[1]["citation"].lower(), item[1]["year"], item[0]))


def doi_link(doi):
    return f"[{doi}](https://doi.org/{doi})" if doi else ""


def magic_link(study, folder):
    """Link to the MagIC contribution and, if recorded, to the commit it was uploaded from."""
    if not study["magic_contribution_id"]:
        return "no"
    link = f"[{study['magic_contribution_id']}](https://earthref.org/MagIC/{study['magic_contribution_id']})"
    if study.get("upload_commit"):
        link += f", from [{study['upload_commit'][:7]}]({REPO_URL}/tree/{study['upload_commit']}/studies/{folder})"
    return link


def git(*args):
    return subprocess.run(["git", "-C", str(REPO_DIR), *args], check=True, capture_output=True,
                          text=True).stdout.strip()


def permalink(folder):
    """Link to a study folder at the current commit, for the description of its MagIC contribution.

    The link names the commit, so it keeps pointing to the files that made the contribution
    whatever happens to the repository afterwards.

    Args:
        folder (str): name of the study folder in studies/.

    Returns:
        str: https://github.com/PmagPy/MagIC_conversions/tree/<commit>/studies/<folder>

    Raises:
        ValueError: if the folder does not exist, has changes that are not committed, or
            the current commit is not on GitHub (origin).
    """
    if not (STUDIES_DIR / folder / "study.json").exists():
        raise ValueError(f"no study folder studies/{folder}")
    changed = git("status", "--porcelain", "--", f"studies/{folder}", "common")
    if changed:
        raise ValueError(f"commit these changes first, so that the link shows what was uploaded:\n{changed}")
    commit = git("rev-parse", "HEAD")
    if not git("branch", "--remotes", "--contains", commit):
        raise ValueError(f"commit {commit[:7]} is not on GitHub yet: push it first")
    return f"{REPO_URL}/tree/{commit}/studies/{folder}"


def studies_markdown(studies):
    """The text of studies.md for a list of (folder, record) as returned by read_studies."""
    lines = ["# Studies", "",
             "Built from the `study.json` of each study folder by `python common/studies.py`; do not edit.",
             "",
             f"{len(studies)} {'study' if len(studies) == 1 else 'studies'}. The tier is the most detailed MagIC "
             "table that the available data fill (measurements, specimens, samples, sites or locations); the "
             "tables above it in the hierarchy are filled as well.",
             "",
             "| Study | Data | Tier | Formats | Recalculates | Status | In MagIC | Authors contacted |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for folder, study in studies:
        build = study.get("build", {})
        if not build:
            recalculates = "not yet built"
        elif build["validation_problems"]:
            recalculates = f"{build['validation_problems']} validation problems"
        else:
            recalculates = "; ".join(build["recalculates"])
        cells = [f"[{study['citation']} ({study['year']})](studies/{folder}/), {study['title']}. "
                 f"*{study['journal']}* {doi_link(study['paper_doi'])}",
                 doi_link(study.get("data_doi")),
                 study["tier"],
                 ", ".join(study["formats"]),
                 recalculates,
                 study["status"],
                 magic_link(study, folder),
                 study["authors_contacted"] or "no"]
        lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |")
    return "\n".join(lines) + "\n"


def main():
    if "--permalink" in sys.argv[1:]:
        try:
            print(permalink(sys.argv[sys.argv.index("--permalink") + 1].strip("/").split("/")[-1]))
        except (IndexError, ValueError) as error:
            sys.exit(str(error) if isinstance(error, ValueError) else "give a study folder after --permalink")
        return
    text = studies_markdown(read_studies())
    if "--check" in sys.argv[1:]:
        current = STUDIES_TABLE.read_text(encoding="utf-8") if STUDIES_TABLE.exists() else ""
        if current != text:
            sys.exit("studies.md is out of date: run python common/studies.py")
        print("studies.md is up to date")
        return
    STUDIES_TABLE.write_text(text, encoding="utf-8")
    print("wrote", STUDIES_TABLE)


if __name__ == "__main__":
    main()
