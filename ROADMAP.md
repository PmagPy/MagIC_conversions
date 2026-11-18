# Roadmap

Status of the studies and of the PmagPy converter work they depend on. Last updated 2026-11-18.

## Praia Grande (Calvo Rathert et al., 2022): ready for a private upload

The contribution validates with `pmagpy.magic_validation` and with the local validator, and unpacks with PmagPy. Before it is made public:

1. Upload `studies/calvo-rathert_2022_praia_grande/magic_contribution.txt` to a private MagIC workspace and resolve anything MagIC's validation reports.
2. At upload, enter the reference, both laboratories and the contribution description (with the link to this repository) as listed in the study's `report.md` under "Uploading to MagIC"; the upload file has no contribution table. Check in the workspace that the non-ASCII characters in descriptions (°, ±, ², ×, μ) display correctly.
3. Make it public, then write to the authors with the link, the questions in the study README and the invitation to supersede the contribution.
4. Record the MagIC contribution number and the date the authors were contacted in the README table and the study README.

The choice that most deserves a second look before upload is the unit of the moments (study README, Units): the magnetizations are known to a factor of about three.

## Vernet et al. (2026), La Garrotxa: in development

Directions from Remasoft `.rs3` and 2G binary files, Thellier-Coe paleointensity from ThellierTool `.tdt` files, and rock-magnetic and thermal-stability data from VFTB files. The stored directions of the 99 2G files reproduce. The 35 `.rs3` files of the OL sites have ID M rows with no unit, which PmagPy `rs3` does not yet read.

## PmagPy changes the studies depend on

In PmagPy 4.6.0 (released 2026-11-11), from pull request [#1010](https://github.com/PmagPy/PmagPy/pull/1010):

| Change | Files |
| --- | --- |
| New Remasoft converter `rs3` | `pmagpy/convert_2_magic.py`, tests in `pmagpy/test/test_convert_rs3.py` |
| `tdt`: headers with empty fields, blank lines, unreadable step labels, file-name option | same module, tests in `pmagpy/test/test_convert_tdt.py` |
| `vftb`: IRM acquisition, back-field and hysteresis files; weight; measurement names; units from the column names | same module, tests in `pmagpy/test/test_convert_vftb.py` |
| `pmag.sortarai`: skip a magnitude column that is empty for the specimen | `pmagpy/pmag.py`, tested in `pmagpy/test/test_convert_tdt.py` |

Merged since: a converter for Paleomagnetism.org `.col` files ([#1017](https://github.com/PmagPy/PmagPy/pull/1017)).

Proposed:

| PmagPy change | Status |
| --- | --- |
| `_2g_bin`: fixed-offset header reader, orientation, all measurements kept by default | [#1023](https://github.com/PmagPy/PmagPy/pull/1023) |
| `rs3`: ID M rows, fit limits with no unit, specimen-name option | pull request in preparation |
| `pmd`: step labels, header parsing, Latin-1 | not yet proposed |
| `tdt`: duplicate specimen names; tail checks kept as LT-PTRM-MD | not yet proposed |
| a reader for the 2G tab-delimited export | not yet proposed |

Further converter work that the first study pointed to:

- `rs3`: no real file with bedding, or with orientation parameters P1 = 3 or 9, has been run; the line flags `O` and `A` alone and a Fisher mean saved from the great-circle window have not been seen in a file.
- The sample naming test `"4" in samp_con` that `rs3` had (it reads `7-4` as convention 4) is still in about ten other converters of `convert_2_magic.py`.
- `jr6_jr6`: writes a temporary file into the input folder and prints each step label; it reads a multispecimen field label such as `A10` as an alternating field.
- A reader for multispecimen protocols (several files, one per step) would move the multispecimen section of the Praia Grande `convert.py` into PmagPy.

## Finding more studies

A study is a good candidate when the archive holds the measurements of every experiment, the license allows redistribution, the paper gives site-level results to recalculate, and no MagIC contribution exists. Places to look: Zenodo, figshare and PANGAEA searches for demagnetization data, and the data availability statements of recent paleomagnetic papers.
