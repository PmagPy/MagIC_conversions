# Converting a study

Working notes for a person or an agent converting a study. `README.md` gives the layout and the conventions; this file gives where things are and what has been learned. The worked examples are [studies/calvo-rathert_2022_praia_grande](studies/calvo-rathert_2022_praia_grande/) (laboratory files) and [studies/yuan_2025_jiabula](studies/yuan_2025_jiabula/) (a table of a supplement).

## The two principles

**1. Everything is reproducible.** A contribution is made by code from files kept in the study folder, so that anyone can rerun it and trace a value to its source.

- An AI assistant can do two things: extract tables from a paper into files, and write the code that converts the files to MagIC format. It does not write the upload file itself.
- Read a supplement table from the published file (`.xlsx`, `.csv`) where there is one. Transcribe from the PDF only when there is not, keep the transcription as a file, and check it by recalculating a published result from it (a site mean from its specimen rows, a pole from its site means).
- Never enter a value that is not in the files or the paper. Leave the column empty and list it under what is missing.
- No step is done by hand outside the build: no edited archive, no table adjusted after it is written.

**2. The work uses PmagPy, and improves it.** The converters and calculations of PmagPy are what its GUIs and the conversion tools hosted by MagIC run on, so every study is a test of them on real data.

- Read laboratory files with `pmagpy.convert_2_magic`, and calculate with `pmagpy.pmag` and `pmagpy.ipmag` (Fisher means, VGPs and poles, line and plane fits, paleointensity statistics), not with code written for the study.
- When PmagPy cannot do something, does it incompletely, or gives a wrong result, the fix goes into PmagPy with a test, in a pull request. A workaround in `convert.py` is temporary and is listed in the study README with the PmagPy issue.
- Code that a second study would need belongs in PmagPy, not in `convert.py` or `common/`.

## Tiers

The tier of a study is the most detailed MagIC table that the available data fill. The tables above it in the hierarchy are filled as well, and the published results at each level are recalculated from the level below.

| Tier | The data available | The build |
| --- | --- | --- |
| `measurements` | laboratory files are archived | runs the `pmagpy.convert_2_magic` converters, adds the published results, recalculates them from the measurements |
| `specimens` | specimen directions or results in a table of the paper or its supplement | builds the tables from the saved table, recalculates the means and poles |
| `samples` | sample directions or results in a table | the same, from the samples |
| `sites` | site means only | builds sites and locations, recalculates the pole from the site means |
| `locations` | a mean direction or pole only | builds the locations table |

A study is a good candidate when its data are public, the license allows redistribution, the paper gives site-level results to recalculate, and no MagIC contribution exists. The best ones archive the measurements of every experiment.

Look for archived measurements before settling on a tier below `measurements`: the data availability statement, the publisher's supplement, Zenodo, figshare, PANGAEA, EarthChem, Mendeley Data, and the Paleomagnetism.org library.

## Is the study already in MagIC?

```
https://api.earthref.org/v1/MagIC/search/contributions?query=%22<doi>%22
```

- The DOI must be in double quotes (`%22`). HTTP 204 means no result.
- A hit is a match only if its `reference` is the paper's DOI: the search also returns contributions that cite the DOI in a description. A contribution may carry a preprint DOI.
- Download a contribution: `https://api.earthref.org/v1/MagIC/data?id=<id>` with the header `Accept: text/plain`.

## Data model, method codes, vocabularies

| What | Where |
| --- | --- |
| Data model 3.0 | https://earthref.org/MagIC/data-models/3.0.json |
| Method codes | https://www2.earthref.org/MagIC/method-codes.json |
| Controlled vocabularies | https://www2.earthref.org/vocabularies/controlled |
| Copies in PmagPy | `pmagpy/data_model/`, refreshed by `pmagpy.magic_validation.update_cache()` |

Laboratories are the `lab_names` vocabulary. A lab can be listed under an older name than the paper uses. If it is not listed, say so in the study README; it has to be added by MagIC before upload.

## Validation

Run both before a study is called ready. The build must end with no errors.

1. **PmagPy**, a port of the validation of the MagIC website and the check to rely on:
   ```python
   from pmagpy import magic_validation
   problems = magic_validation.validate("magic_contribution.txt")  # DataFrame: level, table, column, message, rows
   ```
2. **MagIC's server**, which needs no login:
   ```python
   import requests
   r = requests.post("https://api.earthref.org/v1/MagIC/validate", data=open("magic_contribution.txt", "rb").read(),
                     headers={"Content-Type": "text/plain"}, timeout=600)
   errors = r.json()["validation"]["errors"]  # dicts with table, column, message
   ```
   An empty list means the file passes. The server's vocabulary can lag the published one, so a term can pass the first check and fail here.

## Converters

`pmagpy.convert_2_magic` has one function per format, among them `rs3` (Remasoft), `tdt` (ThellierTool), `vftb`, `jr6_jr6` and `jr6_txt` (AGICO JR6), `cit` (CIT/SAM), `col` (Paleomagnetism.org), `pmd`, `_2g_bin` and `_2g_asc` (2G), `sio`, `utrecht`, `ldeo`, `huji`, `agm`, `k15`, `kly4s`, `sufar4` and `generic`.

When a converter fails on a file or reads it incompletely (principle 2):

- Write the issue with the file, what happened, what was expected, and a minimal reproduction.
- PmagPy's issues and pull requests are the record of what is open: https://github.com/PmagPy/PmagPy/issues. A study README links the ones the study depends on or found.

Gaps noted in the studies so far and not yet written up as PmagPy issues:

- `rs3`: no real file with bedding, or with orientation parameters P1 = 3 or 9, has been run.
- `pmd`: step labels, header parsing, Latin-1.
- `tdt`: duplicate specimen names; tail checks kept as LT-PTRM-MD.
- `jr6_jr6`: writes a temporary file into the input folder and prints each step label; reads a multispecimen field label such as `A10` as an alternating field.
- The sample naming test `"4" in samp_con` (it reads `7-4` as convention 4) is in about ten converters.
- No reader for the 2G tab-delimited export, and none for multispecimen protocols (several files, one per step).
- No S-ratio function.

Check a conversion against the source: converted geographic and tilt-corrected directions against those stored in the files or printed in the paper, and fits re-made from the measurements against the stored fits.

## Building the tables

- **A table of a paper is a file.** A table that the contribution is built from is kept in the study folder as a CSV with the digits as printed (`table_s3.csv`), made by a script where the source allows it (`extract_table_s3.py` in the Jiabula study reads the PDF with `pdftotext`). The build reads the CSV and checks it by recalculation.
- **Hierarchy.** The site is the unit the authors average to get a pole or a field estimate: a cooling unit, a bed, a kiln. If the authors average samples or specimens directly, each of them is its own site, with the same name as sample and specimen and its direction on the site row; the field grouping goes in the description.
- **Locations.** One location name per study area. A row without a result describes the area and lists all its sites; each published mean or pole is a further row with the same location name, a `result_name`, and the sites it averages. A pole is entered only in the coordinates of the interpreted magnetization (tilt-corrected for a magnetization older than the folding).
- **Age columns.** Every row with an age has `age`, with either `age_sigma` or `age_low` and `age_high`. A bound given only as a chronostratigraphic name takes the boundary age of the International Chronostratigraphic Chart, and the description names the chart.
- **Ages.** An age must be independent of the result it dates. An archaeomagnetic or magnetostratigraphic date derived from the direction itself is not entered as the age of that direction; use the stratigraphic, typological or radiometric constraint.
- **Published against recalculated.** The published value is entered. Where a recalculation differs, the report shows both and the row's `description` says so.
- **Inferences.** Something the files and the paper do not say is inferred only when one choice reproduces the published numbers to their printed precision; the `description` says what was inferred and from what.
- **Descriptions cite only public information**: the paper, its supplement, public repositories. Never the files of this repository.
- **Geology.** The same `geologic_classes`, `geologic_types` and `lithologies` on the specimens, samples and sites of a unit. Dikes are "Volcanic Dike", sills "Sill".
- **Numbers.** Round to the precision of the source, so that no value is written as `6.840000000000001e-05`.
- **The upload file** is written with `ipmag.upload_magic` and has no contribution table.

## Finishing

1. `python studies/<folder>/convert.py` ends with no validation problems and writes `report.md` and the `build` entry of `study.json`.
2. `python common/studies.py` rebuilds `studies.md`.
3. The study README lists every choice and inference, what is missing, and the questions for the authors.
4. Upload follows `README.md` ("Adding a study", step 7): commit and push, then `python common/studies.py --permalink <folder>` for the description.

## Other things learned

- Wiley and Elsevier return HTTP 403 to scripts asking for supplements. GSA supplements on figshare and Oxford University Press supplements can be downloaded.
- `pdftotext -layout` loses minus signs and merges columns in some tables. Look at the rendered page where a value is in doubt.
- Most papers since about 2005 publish site means only, with measurements "on request". Record whom to ask and what for in the study README.
