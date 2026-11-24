# Jiabula Formation, Zhangda section, eastern Tethyan Himalaya

MagIC contribution for Yuan et al. (2025), built from the specimen directions the authors published in their supplement and from the paper.

> Yuan, J., Hao, W., & Qiu, R. (2025). New paleomagnetic and geochronologic results from the eastern Tethyan Himalaya refine the size of Greater India in the Early Cretaceous. *Journal of Asian Earth Sciences*, 278, 106428. https://doi.org/10.1016/j.jseaes.2024.106428
>
> Data: Yuan, J., Hao, W., & Qiu, R. (2024). Science Data Bank. https://doi.org/10.57760/sciencedb.15244 (CC BY 4.0)

The study sampled grey limestones of the Lower Cretaceous Jiabula Formation at 27 sites of the Zhangda section (28.9°N, 91.1°E). It reports a high-temperature component in 204 specimens, which passes fold tests, and from their mean a pole at 11.2°N, 300.5°E (A95 2.6°), a paleolatitude of 40.9 ± 2.6°S at about 126 Ma.

The authors published the direction of the high-temperature component of every specimen, with its bedding, so the mean directions and the pole can be recalculated. The demagnetization measurements are not public, so this is a contribution of the `specimens` tier: the specimens table is the most detailed one the data fill. There are no laboratory files, and no converter of `pmagpy.convert_2_magic` applies.

## Status

| | |
| --- | --- |
| Built | specimens, samples and sites from Table S3; the published means, pole and age from the paper |
| Validation | no problems with `pmagpy.magic_validation` (MagIC's own rules, PmagPy 4.6.0), which the build runs on the upload file, or with MagIC's server (`api.earthref.org/v1/MagIC/validate`, 2026-11-23) |
| MagIC | not yet uploaded; no contribution for the DOI of the paper on 2026-11-23 |
| Upload | from commit [b31aa31](https://github.com/PmagPy/MagIC_conversions/tree/b31aa31bde08793a0ed3bafc25b51b0b257e4ebb/studies/yuan_2025_jiabula); the description to enter on MagIC is that of `report.md` with this link as its `<permalink>` |
| Authors | to be contacted after upload, with an invitation to supersede the contribution with their own version |

## Files

| File | What it is |
| --- | --- |
| `magic_contribution.txt` | the upload file, written with `ipmag.upload_magic`: every table except the contribution table, which is made on MagIC at upload from the values listed in `report.md` |
| `report.md` | written by the build: contents and every comparison with the paper |
| `directions.png` | written by the build: the 204 directions and their means, in situ and tilt-corrected |
| `convert.py` | the build: tables, checks against the paper, validation; run `python convert.py` (several minutes, for the elongation/inclination bootstraps) |
| `published.py` | values transcribed from the paper, and the choices below as constants |
| `table_s3.csv` | Table S3 of the supplement, as printed: one row per specimen |
| `extract_table_s3.py` | makes `table_s3.csv` from the PDF with `pdftotext`; the build does not need it |
| `data/` | the supplement, unmodified, with its license and checksum |

## What the contribution holds

| Table | Rows | From |
| --- | --- | --- |
| specimens | 408: the high-temperature component of 204 specimens, in situ and tilt-corrected, with MAD | Table S3 |
| samples | 204: one for each specimen, with the bedding | Table S3; text |
| sites | 408: one for each specimen, in situ and tilt-corrected | Table S3; text |
| locations | 4: the section; the mean of the high-temperature component tilt-corrected, with the pole, and in situ; the mean of the low-temperature component | text |
| ages | 1 | text |

Every value comes from **Table S3**, from the **text** of the paper, or is **inferred** by recalculation. The row descriptions in the contribution say which, wherever it is not the plain reading of the table.

## Recalculation of the published results

`report.md` gives the recalculated and published values side by side. The calculations are those of PmagPy.

- **Tilt corrections.** Each printed tilt-corrected direction was recalculated from the printed in situ direction and bedding (`pmag.dotilt`). 203 of 204 are reproduced within 0.11°, which checks the digits of the table and the reading of the bedding as right-hand strike. The other is item 4 below.
- **Mean directions.** The Fisher means of the 204 directions are 131.56/5.84 (k 14.20, α95 2.71) in situ and 140.50/60.04 (k 25.74, α95 1.98) tilt-corrected, the published 131.6/5.8 (14.2, 2.7) and 140.5/60.0 (25.7, 2.0).
- **Pole.** The pole of the mean direction at the section is 11.2°N, 300.4°E with dp 2.3° and dm 3.0°, 0.08° from the published pole. The published A95 of 2.6° is √(dp·dm). The Fisher mean of the 204 specimen VGPs is 2.0° away, so the published pole is that of the mean direction.
- **The 45° cutoff.** The mean of the 197 directions that the authors keep for their second elongation/inclination analysis (140.6/59.3, k 29.3, α95 1.9) is reproduced exactly with a 45° cutoff on the tilt-corrected VGPs about their mean.
- **Fold tests.** The ratio of the precision parameters is 1.81, as published. Untilting in steps, k is largest at 100 percent unfolding, as published (25.7 here, 25.6 printed).
- **Elongation/inclination.** `ipmag.find_ei` on the 204 tilt-corrected directions, with 1000 bootstrap pseudo-samples, gives a corrected inclination of 62.7° (59.6 to 68.6°), which reproduces the published 63.0° (59.0 to 69.0°). As flattening factors these are 0.90 (1.02 to 0.68) and 0.88 (1.04 to 0.66). The bootstrap is random, so the comparison is loose (within 2.5°): with two other seeds the inclination was 62.3 and 62.9° and its upper bound 71.1 and 69.8°. The inclination is the median of the pseudo-samples that have a solution, about one in ten; the directions have an elongation of 1.72, more than the 1.43 that the TK03 model expects at their inclination, so the function gives no flattening factor for the data set itself.
- **Not recalculated.** The McFadden (1990) statistics, which are entered as published in the description of the pole.

## Choices and inferences

Choices are those of the conventions of this repository (`CONVERTING.md`) unless marked.

1. **Each specimen is its own site.** The authors average the 204 specimen directions directly; no site means are published. So that the mean and the pole follow from the sites table, each row of Table S3 is entered as a specimen, a sample and a site with the same name, with its direction on the specimen and the site. The field site (ZL01 to ZL27) is in each description.
2. **Cores.** The paper reports 242 cores cut into 280 specimens. A name is read as field site and core number (`zl01-2` is core 2 of site ZL01), so each row of Table S3 is taken as its own core. 25 names have a third part, always `-1` (for example `zl13-1-1`), 14 of them beside the name without it (`zl13-1`); these may be second specimens of a core, which the tables do not use.
3. **Position (text).** The paper gives one coordinate pair for the section, 28.9°N, 91.1°E, and its map has no graticule. Every site has this position, with a precision of 0.1°.
4. **Bedding of zl02-1 (inferred).** Table S3 prints strike 212, dip 46, the bedding of site ZL01, for the first specimen of ZL02. With it the in situ direction rotates to 7.2° from the printed tilt-corrected direction. With strike 203, dip 49, the bedding of the other six ZL02 specimens, it is reproduced within 0.06°, and that bedding is entered. The directions are entered as printed.
5. **Line fits (text).** The fits are entered as lines (`DE-BFL`) from thermal demagnetization. The steps of each fit, and whether a line was anchored to the origin, are not published; the paper gives the range of the component as about 350 to 525 °C.
6. **Age (text; choice).** 126 Ma is the age the authors use. The older bound, 126.7 Ma, is the oldest of the youngest zircon dates that the authors read as the maximum depositional age of the formation. The dated sandstone and andesite are from the upper part of the section and the sampled limestones from the lower part, which the descriptions say. The paper gives no younger numerical bound; the top of the Lower Cretaceous, 100.5 Ma, is used, because the paper assigns the formation to the Lower Cretaceous.
7. **Pole in tilt-corrected coordinates only.** The magnetization predates the folding, so the in situ mean is entered without a pole.
8. **Low-temperature component (text; choice).** Its published in situ mean (268 specimens) is a location row without sites, because the specimen directions are not published. The authors read it as an overprint of the present field, so its age is entered as 0 Ma with the age of the rocks as the older bound.
9. **The 45° cutoff (inferred).** The seven specimens outside the cutoff of the second elongation/inclination analysis are named in their descriptions. They are part of the published mean and pole and are flagged good.
10. **Reversed polarity.** All 204 directions are entered as reversed, as the authors interpret them.

## Questions for the authors

1. The demagnetization measurements, and the steps and line type of each fit.
2. The directions of the low-temperature component.
3. The coordinates of the 27 sites, and the core orientations.
4. The bedding of specimen zl02-1.

## PmagPy

The build uses `pmag.dotilt`, `pmag.fisher_mean`, `pmag.angle`, `pmag.dia_vgp`, `pmag.plat`, `ipmag.find_ei`, the `ipmag` equal-area plotting functions, `ipmag.upload_magic` and `pmagpy.magic_validation`. Nothing is calculated outside PmagPy.

The two runs of `ipmag.find_ei` take most of the build's several minutes. Its bootstrap is seeded (`random_seed`), so a rebuild gives the same numbers.
