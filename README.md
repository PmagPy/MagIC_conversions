# MagIC_conversions

Conversions of published paleomagnetic and rock-magnetic data from laboratory file formats into validated [MagIC](https://earthref.org/MagIC) contributions, using [PmagPy](https://github.com/PmagPy/PmagPy).

Many authors archive their measurements in a general repository, in the formats written by laboratory software, so the data are open and the published results can be recalculated. This repository converts such archives, together with the tables of the paper, into MagIC contributions, in which the data can be searched and combined with those of other studies. The documentation of each study gives the source of every value, the assumptions and inferences that were needed, and a recalculation of the published results from the archived measurements.

## Studies

| Study | Data | Formats | Recalculates | In MagIC | Authors contacted |
| --- | --- | --- | --- | --- | --- |
| [Calvo Rathert et al. (2022)](studies/calvo-rathert_2022_praia_grande/), Praia Grande lava sequence, Cape Verde. *Geophys. J. Int.* [10.1093/gji/ggac173](https://doi.org/10.1093/gji/ggac173) | [10.5281/zenodo.5553392](https://doi.org/10.5281/zenodo.5553392) | Remasoft `.rs3`, ThellierTool `.tdt`, JR6 `.jr6`, VFTB | 11 of 11 flow directions; 22 of 22 Thellier-Coe determinations; 9 of 10 standard multispecimen determinations; rock-magnetic parameters | no | no |

## Layout

```
common/
    magic_tools.py        reading and writing MagIC text; validation against the data model
    resources/            MagIC data model 3.0, method codes and controlled vocabularies used by the validation
studies/
    <first author>_<year>_<short name>/
        README.md         the study, its status, every decision and inference, questions for the authors
        convert.py        the build: archives and transcribed tables in, contribution and report out
        published.py      values transcribed from the paper; decisions as named constants
        data/             the archived files, unmodified, with source, license and checksums
        magic_contribution.txt   the upload file (ipmag.upload_magic): every table but the contribution table
        report.md         written by the build: contents, checks against the paper, what to enter at upload, what is missing
```

## Running a conversion

```
python studies/calvo-rathert_2022_praia_grande/convert.py
```

This rewrites `magic_contribution.txt` and `report.md` in the study folder and leaves converter output in `build/`, which is not kept in the repository.

Requirements: Python 3 with numpy, pandas and PmagPy 4.6.0 (released 2026-11-11) or later, which has the Remasoft converter `convert_2_magic.rs3` and the fixes to `tdt`, `vftb` and `pmag.sortarai` that the Praia Grande study needs (listed in the study README).

## Conventions

- **Sources.** Every value in a contribution is from the archived **files**, from a **table** of the paper, from its **text**, from a **figure**, or is **inferred** by recalculation. Anything other than the plain reading of a file or table is said in the `description` of the row and listed in the study README.
- **Published values are entered as published.** Where a recalculation gives a slightly different value, the published one is entered and the report shows both.
- **Nothing in an archive is edited.** Adjustments needed to read a file (a step label, a specimen name) are made in the build and listed.
- **Inferences are tested.** Something the files and the paper do not say (which specimens were left out of a mean, which line type was used) is inferred only when one choice reproduces the published numbers to their printed precision, and the report shows the reproduction.
- **Assumptions are named.** What cannot be tested (no tilt correction, the unit of unlabeled moments) is entered as an assumption, with the reason and who made it, in the study README and in the affected rows.
- **Format readers belong in PmagPy.** When PmagPy cannot read a format, or reads it incompletely, the converter is added or fixed there with tests, and the study script stays short.
- **Validation.** `common/magic_tools.py` checks a contribution against the rules in the MagIC data model. It is a local check; MagIC's own validation runs when a contribution is uploaded to a private workspace.
- **Tone.** The documentation is written for the authors, who made their measurements available, and for other users of the data. Differences between the tables and the files are recorded without comment.
- **Uploading.** A converted study is uploaded to MagIC from this repository once it validates. The upload file is written with `ipmag.upload_magic` and holds every table except the contribution table, which is made on MagIC at upload (reference, laboratories, description; `report.md` lists them). The authors are then contacted and pointed to the contribution and to the study README. They can correct or extend it and upload the result as a new version, which supersedes ours.

## Adding a study

1. Create `studies/<first author>_<year>_<short name>/` and put the archived files in `data/` with a README giving the source, license and checksums. Commit copies only where the license allows it; otherwise fetch them in the build.
2. Transcribe the tables and statements of the paper that the contribution needs into `published.py`.
3. Write `convert.py`: run the PmagPy converters, add the published results, recalculate them from the measurements, validate, and write the upload file with `ipmag.upload_magic` and `report.md`.
4. Write the study README: status, sources, each choice and inference with its reason, and a short list of questions for the authors.
5. Add a row to the table above.
6. Upload the contribution to MagIC, then write to the authors with the link, the questions from the study README and an invitation to supersede the contribution with their own version. Record both in the table and in the study README.
