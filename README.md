# MagIC_conversions

Conversions of published paleomagnetic and rock-magnetic data from laboratory file formats into validated [MagIC](https://earthref.org/MagIC) contributions, using [PmagPy](https://github.com/PmagPy/PmagPy).

Many authors archive their measurements in a general repository, in the formats written by laboratory software, so the data are open and the published results can be recalculated. This repository converts such archives, together with the tables of the paper, into MagIC contributions, in which the data can be searched and combined with those of other studies. The documentation of each study gives the source of every value, the assumptions and inferences that were needed, and a recalculation of the published results from the archived measurements.

## Studies

The studies are listed in [studies.md](studies.md), with the data and formats of each, what recalculates, and whether it is in MagIC. That table is built from the `study.json` of each study folder and is not edited by hand:

```
python common/studies.py
```

## Layout

```
common/
    magic_tools.py        reading a MagIC table; writing and validating the upload file; Markdown tables for the reports
    studies.py            builds studies.md from the study.json files
CONVERTING.md             working notes for converting a study: resources, validation, converters, lessons
studies.md                the table of studies, written by common/studies.py
studies/
    <first author>_<year>_<short name>/
        README.md         the study, its status, every decision and inference, questions for the authors
        study.json        the record of the study that studies.md is built from (see below)
        convert.py        the build: archives and transcribed tables in, contribution and report out
        published.py      values transcribed from the paper; decisions as named constants
        table_*.csv       a table of the paper or its supplement, as printed, where the contribution is built from one
        data/             the archived files, unmodified, with source, license and checksums
        magic_contribution.txt   the upload file (ipmag.upload_magic): every table but the contribution table
        report.md         written by the build: contents, checks against the paper, what to enter at upload, what is missing
```

## Running a conversion

```
python studies/calvo-rathert_2022_praia_grande/convert.py
```

This rewrites `magic_contribution.txt`, `report.md` and the `build` entry of `study.json` in the study folder and leaves converter output in `build/`, which is not kept in the repository.

Requirements: Python 3 with numpy, pandas and PmagPy 4.6.0 (released 2026-11-11) or later, which has the Remasoft converter `convert_2_magic.rs3` and the fixes to `tdt`, `vftb` and `pmag.sortarai` that the Praia Grande study needs (listed in the study README).

## The study record

`study.json` holds what the table of studies needs. Its entries are entered by hand, except `build`, which the study's `convert.py` rewrites each time it runs (`common.studies.write_build_summary`).

| Entry | Value |
| --- | --- |
| `citation`, `year`, `title`, `journal`, `paper_doi` | the paper, e.g. "Calvo Rathert et al.", 2022 |
| `data_doi`, `data_license` | the archive of the data, if there is one |
| `formats` | the file formats converted |
| `tier` | `measurements`: converted from laboratory files with `pmagpy.convert_2_magic`, with the published results recalculated. `results`: built from the tables of the paper or its supplement, where no measurement files are available |
| `status` | where the study stands, in a few words |
| `magic_contribution_id` | the MagIC contribution number once uploaded, otherwise `null` |
| `upload_commit` | the commit of this repository the upload was made from, otherwise `null` |
| `authors_contacted` | the date the authors were written to, otherwise `null` |
| `build` | written by `convert.py`: PmagPy version, rows of each table, number of validation problems, and what recalculates |

## Conventions

- **Sources.** Every value in a contribution is from the archived **files**, from a **table** of the paper, from its **text**, from a **figure**, or is **inferred** by recalculation. Anything other than the plain reading of a file or table is said in the `description` of the row and listed in the study README.
- **Published values are entered as published.** Where a recalculation gives a slightly different value, the published one is entered and the report shows both.
- **Nothing in an archive is edited.** Adjustments needed to read a file (a step label, a specimen name) are made in the build and listed.
- **Inferences are tested.** Something the files and the paper do not say (which specimens were left out of a mean, which line type was used) is inferred only when one choice reproduces the published numbers to their printed precision, and the report shows the reproduction.
- **Assumptions are named.** What cannot be tested (no tilt correction, the unit of unlabeled moments) is entered as an assumption, with the reason and who made it, in the study README and in the affected rows.
- **Format readers belong in PmagPy.** When PmagPy cannot read a format, or reads it incompletely, the converter is added or fixed there with tests, and the study script stays short.
- **Calculations belong in PmagPy too.** Line fits, Fisher means, poles, paleointensity statistics and rock-magnetic parameters are calculated with PmagPy functions. Where a study has to calculate something itself, its README says what and why, with the PmagPy issue.
- **Validation.** The build validates the upload file with `pmagpy.magic_validation`, a port of the validation of the MagIC website. MagIC's own validation runs when a contribution is uploaded to a private workspace.
- **Tone.** The documentation is written for the authors, who made their measurements available, and for other users of the data. Differences between the tables and the files are recorded without comment.
- **Uploading.** A converted study is uploaded to MagIC from this repository once it validates. The upload file is written with `ipmag.upload_magic` and holds every table except the contribution table, which is made on MagIC at upload (reference, laboratories, description; `report.md` lists them). The description entered on MagIC links to the study folder at the commit the upload was made from (`python common/studies.py --permalink <study folder>`), so the link keeps pointing to the files that made the contribution. For the same reason this repository stays in place: if later studies go to other repositories, the studies here and their history remain. The authors are then contacted and pointed to the contribution and to the study README. They can correct or extend it and upload the result as a new version, which supersedes ours.

## Adding a study

[CONVERTING.md](CONVERTING.md) has the working notes for a conversion: where the data model and vocabularies are, how to validate, the converters, and what has been learned. Read it first.

1. Create `studies/<first author>_<year>_<short name>/` and put the archived files in `data/` with a README giving the source, license and checksums. Commit copies only where the license allows it; otherwise fetch them in the build.
2. Transcribe the tables and statements of the paper that the contribution needs into `published.py`.
3. Write `convert.py`: run the PmagPy converters, add the published results, recalculate them from the measurements, validate, and write the upload file with `ipmag.upload_magic` and `report.md`.
4. Write `study.json` (the entries entered by hand) and end `convert.py` with a call to `common.studies.write_build_summary`.
5. Write the study README: status, sources, each choice and inference with its reason, and a short list of questions for the authors.
6. Run `python common/studies.py` to rebuild `studies.md`.
7. Commit and push, then upload the contribution to MagIC with the description from `report.md`, its `<permalink>` replaced by the output of `python common/studies.py --permalink <study folder>`. Then write to the authors with the link, the questions from the study README and an invitation to supersede the contribution with their own version. Record the contribution number, the commit of the permalink and the date the authors were contacted in `study.json` and in the study README, and rebuild `studies.md`.

## License

- **Code** (`convert.py`, `published.py`, `common/magic_tools.py` and other scripts): BSD 3-Clause, in `LICENSE`, the license of PmagPy.
- **Documentation, reports and contributions** (the READMEs, `report.md`, `magic_contribution.txt`): [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). A contribution is adapted from the authors' archived data and paper; cite them as well as this repository.
- **Archived data** (`studies/*/data/`): the license of the original record, unchanged. The README in each `data/` folder gives the source and license.
