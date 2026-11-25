# Praia Grande lava sequence, São Vicente, Cape Verde

MagIC contribution for Calvo Rathert et al. (2022), converted from the laboratory files archived by the authors and from the paper.

> Calvo Rathert, M., Carrancho, Á., Morales, J., Pérez-Rodríguez, N., Lebedev, V. A., Caccavari, A., Vegas, N., & Goguitchaichvili, A. (2022). Multimethod palaeointensity results from a rapidly emitted upper Miocene lava flow sequence in São Vicente (Cape Verde): new data for the African record. *Geophysical Journal International*, 231(1), 215–229. https://doi.org/10.1093/gji/ggac173
>
> Data: Calvo-Rathert, M., Carrancho, Á., Morales, J., Pérez, N., & Caccavari, A. (2021). Zenodo. https://doi.org/10.5281/zenodo.5553392 (CC BY 4.0)

The study sampled 11 nephelinite lava flows (PRG1 at the base to PRG11) dated at 6.07 ± 0.16 Ma. It reports a mean direction for each flow, Thellier-Coe and multispecimen paleointensities, and rock-magnetic results.

The authors archived the measurements of every experiment of the study (demagnetization, both paleointensity methods and the rock-magnetic curves), so the published results can be recalculated from them.

## Status

| | |
| --- | --- |
| Converted | all four archives of the Zenodo record, with the results of Tables 1 to 3 and S1, S3 and S4 |
| Validation | no problems with `pmagpy.magic_validation` (MagIC's own rules), which the build runs on the upload file, or with MagIC's server (`api.earthref.org/v1/MagIC/validate`, 2026-11-25) |
| MagIC | contribution [20941](https://earthref.org/MagIC/20941), public, uploaded 2026-11-23 from commit [71cf359](https://github.com/PmagPy/MagIC_conversions/tree/71cf359bea1fe0eb8257ea190fa08d60762135ec/studies/calvo-rathert_2022_praia_grande). Since 2026-11-25 the build writes the magnetization-temperature curves with their temperature and field in `meas_temp` and `meas_field_dc` (they were in `treat_temp` and `treat_dc_field`, see "PmagPy changes made for this study"); in all else the upload file is the same. To be uploaded as a new version. |
| Authors | to be contacted after upload, with an invitation to supersede the contribution with their own version |

## Files

| File | What it is |
| --- | --- |
| `magic_contribution.txt` | the upload file, written with `ipmag.upload_magic`: every table except the contribution table, which is made on MagIC at upload from the values listed in `report.md` |
| `report.md` | written by the build: contents and every comparison with the paper |
| `convert.py` | the build, with a section for each archive (conversion and checks against the paper); run `python convert.py` |
| `published.py` | values transcribed from the paper and its supporting information, and the choices below as constants |
| `data/` | the four Zenodo archives, unmodified, with checksums |

## What the contribution holds

| Table | Rows | From |
| --- | --- | --- |
| measurements | 9,291: 1,186 demagnetization steps, 1,750 Thellier-Coe steps, 385 multispecimen steps, 5,970 rock-magnetic points | the files |
| specimens | 359 rows for 242 specimens: 88 demagnetized (181 rows, with the authors' line fits in specimen and geographic coordinates), 66 Thellier (22 with a determination), 77 multispecimen, 11 rock-magnetic (35 rows: hysteresis parameters and 24 Curie temperatures) | the files; Tables 2 and S1 |
| samples | 92: 81 cores, 11 multispecimen samples | the files; text |
| sites | 20: a direction row and, for nine flows, a paleointensity row | Tables 1 to 3 |
| locations | 1: sequence-mean direction, pole and paleointensity | Tables 1 and 3 |
| ages | 2 | text; Table S4 |
| criteria | 10 | Tables 2 and 3 |

Every value comes from the archived **files**, from a **table** of the paper or its supporting information, from its **text**, from a **figure**, or is **inferred** by recalculation where the files and the paper leave something open. The row descriptions in the contribution say which, wherever it is not the plain reading of a file or a table.

## Recalculation of the published results

`report.md` gives the recalculated and published values side by side.

- **Line fits.** 86 of the 87 fits saved in the demagnetization files are recalculated from the measurements within 0.15° in direction and 0.07° in MAD.
- **Flow mean directions (Table 1).** All 11 recalculate from the contribution to their printed precision in direction, k and α95.
- **Sequence mean direction and pole.** Recalculated from the 11 flow means: 332.1/29.7, k 631, α95 1.8, and the mean VGP within 0.03°.
- **Thellier-Coe determinations (Table 2).** All 22 recalculate in N, B and standard error (within 0.1 μT), f (within 0.025) and q (within 3 percent); the archived moments have three significant figures. Two need these tolerances: PRG1-8 (q 34.1 against 35.1) and PRG3-6A (f 0.43 against 0.41).
- **Multispecimen determinations (Tables 2 and S3).** The standard determinations of Table S3 recalculate to their printed precision in B and R² for 9 of 10 flows. The determinations selected in Table 2 are mostly alignment corrected, which a plain calculation does not do. With the sub-specimens that come closest left out (item 22), it is within 0.3 μT of them (PRG4: 18.60 against 18.3).
- **Flow and sequence paleointensities (Table 3).** The means recalculate from the specimen and multispecimen results. The standard deviations and percentages differ from the recalculated ones by up to 0.5 percent. For PRG1 the printed σ (0.4 μT) does not agree with the printed 3.9 percent (0.7 μT) or with the values (0.79 μT); both are entered as printed, and the row says so.
- **Rock-magnetic results (Table S1).** Ms recalculated from the archived loops agrees within 1.1 percent, the saturation remanence within 5 percent, Bc within 7 percent and Bcr within 15 percent (PRG9-8).

In a few places the archived measurements give a slightly different value from the printed one, or two printed values disagree. The published value is entered in every case, `report.md` shows both, and the row's description notes the difference. Examples: β of PRG9-6A, and the bounds of the PRG7 multispecimen determination, which differ between Table 2 and Table S3.

## Choices and inferences

Choices marked NSH were made by Nicholas Swanson-Hysell on 2026-11-10.

### Site and geology

1. **Position (figure).** The section is marked by a single star on the map of Figure 1b, which has a 4′ graticule. The paper gives no coordinates, and the text describes no layout of the flows along the section, so one position is used for all 11 flows.
   - The figure was georeferenced from its graticule ticks (`published.py` gives the pixel values). The centroid of the star is at 16.864°N, 24.893°W.
   - One pixel is about 26 m. The Mindelo marker on the same map georeferences 0.35 km from Mindelo in OpenStreetMap, a measure of the accuracy of the map.
   - All ten published VGPs other than that of PRG5 (item 10) recalculate from this position exactly to their printed 0.1°.
2. **Tilt (assumption, NSH).** No bedding or structural correction is reported, and the flows are taken as untilted. Directions are in geographic coordinates, and the site and location descriptions say so.
3. **Orientation (text).** A solar and a magnetic compass were both used, so every core carries both method codes.
4. **Laboratories (text).** The measurements were made at the University of Burgos, and the multispecimen experiments at the Servicio Arqueomagnético Nacional of UNAM in Morelia (Section 7.2 of the paper). The contribution names both.
5. **Ages (text, Table S4).** The K-Ar age of flow PRG1 (6.07 ± 0.16 Ma at 2σ, entered as ± 0.08) is used for all flows, as the authors do. The location carries their combined K-Ar and polarity range, 6.03–6.23 Ma.

### Directions

6. **Fits in each flow mean (inferred).** The files hold the authors' fits; which of them enter each flow mean was identified from Table 1.
   - The components named `CA` or `CA1` are the characteristic ones (one per file).
   - For each flow there is exactly one set of N directions whose Fisher mean gives the published direction, k and α95, taken from the specimens or from the means of the specimens of each core.
   - Five fits are outside those sets (PRG1-6B, PRG4-8, PRG9-4, PRG9-4A, PRG10-1A). They are kept and flagged `result_quality` b, described as inferred.
   - For flows PRG6, PRG7 and PRG8 the two specimens of one core were averaged first, and the site rows say so.
7. **PRG5-4B (inferred).** The file holds a free line over 300–580 °C. The published mean of flow PRG5 is obtained with the same eight steps fitted as a line anchored to the origin, like nearly all other characteristic fits of the study. The anchored fit is entered as a row of its own, described as recalculated here, and the stored fit is kept and flagged b.
8. **PRG6-2A (inferred).** The stored direction and MAD are those of all 16 steps of the file, so `dir_n_measurements` is 16. The specimen was heated once to 480 °C and then demagnetized by alternating fields, so the fit has both protocol codes and `meas_step_min` is 0 T (the field of the heating step).
9. **MAD (files).** Remasoft stores one MAD per fit. For fits flagged `OA` it is the MAD of the anchored line and is entered in `dir_mad_anc`; otherwise it is in `dir_mad_free`.
10. **VGP of PRG5 (table).** Entered as printed (66.1°N, 243.6°E), which is the value that gives the published sequence-mean VGP. The VGP of the published direction is 1.1° away.

### Units

11. **Moments of the demagnetization and Thellier files (best guess, NSH).** The demagnetization files give the moments in a column labeled A/m, with NRMs near 10⁻³; the Thellier files give no unit and have the same values flow by flow. They are read as emu/cm³, the volume-normalized unit of the 2G magnetometer software, and entered in A/m after multiplying by 1000 (`magn_volume`).
    - The rock-magnetic table of the study is related to its archived curves by the same factor of 1000 (item 12).
    - The NRMs become 0.55–1.45 A/m, which is 0.04–0.30 percent of the saturation remanence of the IRM curves, and of the same order as the multispecimen pellets scaled to a whole core.
    - If the numbers were per gram instead, the NRMs would be 2.9 times higher. The comparisons do not separate the two readings.
    - The paleointensities and directions do not depend on the unit.
    - Every specimen row of the demagnetization and Thellier experiments says this in its description.
12. **Mrs and Ms of Table S1 (inferred).** Ms recalculated from the archived hysteresis loops, which are in emu/g, is 1000 times the printed value for all 11 powders (within 1.1 percent). The values are entered in Am²/kg at the scale of the curves, and the descriptions give the printed numbers.
13. **Other moments.** The multispecimen moments are JR6 values in A/m of pellet. The rock-magnetic curves are in emu/g in the files, which is numerically Am²/kg.

### Names

14. **Specimen names (NSH).** Distinct specimens need distinct names, and the archives use the same names for different pieces of a core.
    - Thellier specimens are fragments in vials. All 66 get the suffix `t` (PRG1-2A becomes PRG1-2At).
    - Multispecimen sub-specimens are numbered 1 to 7 within a flow. They get the suffix `m` and belong to a sample `<flow>-MS`.
    - Rock-magnetic powders are named after their core. They get the suffix `r`.
    - Each description gives the name used in the archive or the paper.
15. **Core names.** A core is the specimen name without its final letter (PRG1-2A and PRG1-2 are specimens of core PRG1-2).
16. **Names with an apostrophe (files).** Two demagnetization files give the specimen a name with an apostrophe: `PRG6-3A.rs3` holds PRG6-3A' and `PRG7-6Z.rs3` holds PRG7-6A'. The names are kept as in the files; their cores are PRG6-3 and PRG7-6.

### Thellier-Coe

17. **Files.** The archive has 82 `.tdt` files. Sixty-six carry ThellierTool step codes and are the 66 specimens of the paper. The other 16 are earlier copies of 16 of them, with the step labels of the measurement session, and are not converted.
18. **Names and one step.** Specimen names are taken from inside the files. One in-field step labeled 566 follows the zero-field step at 565 °C and is entered as 565, which gives the published N.
19. **Ranges.** A published range starting at 20 °C counts heating steps only, so `meas_step_min` is 293 K, above the NRM row.

### Multispecimen

20. **Rows.** The five JR6 files (one per step of the protocol) list the 77 sub-specimens in different orders. A row is identified by the flow in its name and the field in its step label; four rows are placed by the label or by the order of flows in the rest of the file.
21. **Fields and temperature.** The step label gives the laboratory field (`A10` is 10 μT). The heating temperature, 400 or 450 °C, is not given per flow, so `treat_temp` is empty.
22. **Sub-specimens not used (inferred).** Table 2 gives how many sub-specimens were left out of each determination.
    - For PRG1, PRG3, PRG4, PRG5 and PRG7 they are identified as those whose omission brings a plain recalculation closest to the published B, R² and alteration (PRG1-7, PRG3-6, PRG4-7, PRG5-2, PRG7-4). The recalculation has no alignment correction, so it comes within 0.3 μT and 0.4 percent, not exactly. In each case the next-best choice is at least 0.45 μT further off.
    - For PRG2 (PRG2-3, PRG2-6) they come from the standard determination of Table S3, which is reproduced without them. The alignment-corrected determination of Table 2 may leave out others.
    - The rows describe them as inferred.

### Results

23. **One paleointensity row per flow.** Table 3 lists up to three results for a flow (Thellier-Coe, multispecimen, both). The one to which Table 3 gives a class is entered, and its description gives the others. PRG9 (class 4, which the authors do not use further) is flagged b. For PRG11 the multispecimen result is entered, following the authors.
24. **Sequence paleointensity.** The location carries the mean of the eight flows of classes 1 to 3 (18.5 ± 1.9 μT), the value of the abstract. The mean of classes 1 and 2 and the VADMs are in its description.
25. **Criteria.** The class C2 thresholds of Table 2 are entered as the acceptance criteria; each description gives the C1 threshold. The multispecimen criterion on the number of specimens applies to the multispecimen determinations, not to the flow results that pool them with Thellier-Coe specimens.
26. **Number of specimens of a flow result.** `int_n_specimens` counts the Thellier-Coe specimens and multispecimen sub-specimens listed in `specimens`, and `int_n_samples` is the N of Table 3, in which a multispecimen determination counts as one.
27. **Rock-magnetic results (Table S1).** The hysteresis parameters and the S ratio are on the row of each powder, and each Curie temperature is a row of its own. The shape parameter and Brh/Bcr are in the description.
28. **Curie temperatures.** The higher of the two columns of Table S1 (H) is entered as the heating branch and the other (C) as the cooling branch, following the text of the paper and the archived curves.

## Questions for the authors

1. The coordinates of the section.
2. The unit of the moments in the `.rs3` and `.tdt` files.
3. The multispecimen heating temperature of each flow.

## PmagPy changes made for this study

The build needs these changes, merged with pull request [#1010](https://github.com/PmagPy/PmagPy/pull/1010) and in PmagPy 4.6.0 (released 2026-11-11) and later.

- `convert_2_magic.rs3`: new converter for Remasoft files, with the stored fits. Each measurement keeps its own treatment, so PRG6-2A (one heating, then alternating field steps) is a thermal and alternating field experiment.
- `convert_2_magic.tdt`: reads headers with empty fields and files with blank lines; names a specimen after its file correctly.
- `convert_2_magic.vftb`: recognizes IRM acquisition, back-field and hysteresis files as well as thermomagnetic curves, records the weight and names the measurements.
- `pmag.sortarai`: skips a magnitude column that is empty for the specimen, so a table with several experiments can be analyzed.

Since then, from PmagPy changes made for the La Garrotxa study, pull requests [#1058](https://github.com/PmagPy/PmagPy/pull/1058) and [#1059](https://github.com/PmagPy/PmagPy/pull/1059) (merged 2026-11-25, not yet in a release):

- `convert_2_magic.vftb` (#1058) writes a magnetization-temperature curve as measured at temperature in a field, in `meas_temp` and `meas_field_dc`, as the data model defines them and as `rockmag.plot_M_T` reads them; it wrote `treat_temp` and `treat_dc_field`. This moves the temperature and field of the 5,125 points of the 10 curves, with their values unchanged.
- `rockmag.process_backfield_data` (#1059) reads a back-field curve that starts at zero field (issue [#1049](https://github.com/PmagPy/PmagPy/issues/1049)), so the build no longer passes `drop_first=True`; Bcr is unchanged.

The later changes to `rs3` and `pmag.domean` ([#1053](https://github.com/PmagPy/PmagPy/pull/1053), [#1054](https://github.com/PmagPy/PmagPy/pull/1054)) and to `tdt` ([#1057](https://github.com/PmagPy/PmagPy/pull/1057)) do not change the contribution.

`convert_2_magic.jr6_jr6` reads the multispecimen step label `A10` as an alternating field of 10 mT, so the multispecimen files are read in the multispecimen section of `convert.py`.

## Calculations made with PmagPy

| Calculation | PmagPy function |
| --- | --- |
| Line fits (free, anchored, with the origin) | `pmag.domean` |
| Fisher means; angles between directions | `pmag.fisher_mean`; `pmag.angle` |
| VGPs; VADM | `pmag.dia_vgp`; `pmag.b_vdm` |
| Arai plot and its statistics (B, standard error, β, f, q) | `pmag.sortarai`, `pmag.find_dmag_rec`, `pmag.PintPars` |
| Remanent coercivity from the back-field curve | `rockmag.process_backfield_data` |
| Validation | `pmagpy.magic_validation.validate` |

The line fits and the Arai statistics were first written in `convert.py`. Replaced by the PmagPy functions, free and anchored lines agree to rounding, the Arai statistics to rounding, and the contribution is unchanged. The line with the origin as a point, which `pmag.domean` calculated with the origin left out of the centre of mass until [#1054](https://github.com/PmagPy/PmagPy/pull/1054) (issue [#1047](https://github.com/PmagPy/PmagPy/issues/1047)), is only tried as an explanation of a flow mean (Directions, above); with the corrected calculation no flow needs it either, and the contribution is unchanged.

## Calculations not yet made with PmagPy

Each is a candidate for PmagPy, and is calculated in `convert.py` until then.

- **Hysteresis parameters (Ms, Mrs, Bc) from the VFTB loops.** `rockmag.process_hyst_loop` gives Ms 5 to 8 percent and Mrs 11 to 31 percent below Table S1 for these 11 loops, where the simple calculation in `recalculate_rockmag` agrees within 1.1 and 5 percent. The VFTB loops have about 18 points a branch, closely spaced near zero field (1, 8, 19, 37, 74 mT, ...). For PRG1-2 the function resamples the loop on an even field grid of 28 points up to 0.70 T, whose points nearest zero field are at ±37 mT, so the remanence is interpolated across the steepest part of the loop. The grid step is the median field step of the branches, which is large for a loop measured this way; a synthetic loop sampled at these fields shows the same loss. The lower Ms is not explained by it. PmagPy issue [#1048](https://github.com/PmagPy/PmagPy/issues/1048); pull request #1059 lets the function read a loop file that begins with the initial magnetization curve, which it stopped on.
- **S ratio** from the back-field curve: no PmagPy function found.
- **Multispecimen protocol**: no reader for the step files and no calculation of the ratios in PmagPy.

What stays in `convert.py` by its nature: finding which specimens enter a published flow mean, pairing the 16 duplicate Thellier files with their coded copies, and the tables of this study.
