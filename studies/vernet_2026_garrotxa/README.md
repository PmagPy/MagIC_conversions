# La Garrotxa Volcanic Field lava flows, NE Iberia

MagIC contribution for Vernet et al. (2026), converted from the laboratory files archived by the authors and from the paper.

> Vernet, E., Calvo-Rathert, M., Beamud, E., Bógalo, M.-F., Carrancho, Á., Planagumà, L., & Martí, J. (2026). Laschamp and Greenland-Norwegian Sea excursions recorded in NE Iberia lava flows: Late Quaternary geomagnetic data from La Garrotxa Volcanic Field. *Geologica Acta*, 24.15, 1–18, I–VII. https://doi.org/10.1344/GeologicaActa2026.24.15
>
> Data: Vernet Tarragó, E. (2026). Zenodo. https://doi.org/10.5281/zenodo.20326424 (CC BY 4.0)

The study sampled 15 lava flows of Late Pleistocene age (about 134 to 16 ka) with independent 40Ar/39Ar or thermoluminescence ages. It reports a mean direction and VGP for 13 of them, and Thellier-Coe paleointensities (some after low-temperature demagnetization) for 10.

The authors archived the measurements of every experiment (demagnetization, paleointensity, rock-magnetic and thermal-stability curves), so the published results can be recalculated from them.

## Status

| | |
| --- | --- |
| Converted | every experiment of the archive: the demagnetization data (99 2G binary and 134 Remasoft `.rs3` files) with the authors' line fits; the Thellier-Coe files (`.TDT`, 128 specimens, 46 with low-temperature demagnetization) with Table III; the VFTB rock-magnetic curves (21 powders) and thermal-stability cycles (46, Table IV); the site means, VGPs, paleointensities and VADMs of Tables 2 to 4, and the ages of Table 1 |
| Validation | no problems with `pmagpy.magic_validation` (the build runs it on the upload file) or with MagIC's server (`api.earthref.org/v1/MagIC/validate`, 2026-11-25) |
| PmagPy | PmagPy `master` after pull request #1059 (2026-11-25), not yet in a release (section "PmagPy") |
| MagIC | not uploaded; not in MagIC as of 2026-11-11 (no contribution with the paper DOI or the name Garrotxa) |
| Authors | not contacted |

## Files

| File | What it is |
| --- | --- |
| `magic_contribution.txt` | the upload file, written with `ipmag.upload_magic`: every table except the contribution table, which is made on MagIC at upload from the values listed in `report.md` |
| `report.md` | written by the build: contents and every comparison with the paper |
| `study.json` | the record of the study for `studies.md`; its `build` entry is written by `convert.py` |
| `convert.py` | the build; run `python convert.py` |
| `published.py` | values transcribed from the paper and its appendix, and the choices below as constants |
| `table_iii.csv`, `table_iv.csv` | Tables III and IV of the appendix, as printed |
| `extract_tables.py` | makes the two CSV files from the PDF of the paper (CC BY-SA 4.0), which it downloads and checks; the build does not need it |
| `data/` | the Zenodo archive, unmodified, with checksums |

## What the contribution holds

| Table | Rows | From |
| --- | --- | --- |
| measurements | 21,022: 1,531 demagnetization steps from the 2G files of the GTX sites and 436 from the `.rs3` files of the OL sites; 4,035 Thellier-Coe steps; 6,730 points of rock-magnetic curves and 8,290 of thermal-stability cycles | the files |
| specimens | 467 rows for 317 specimens: 134 demagnetized (284 rows: the authors' 141 fits in specimen and geographic coordinates, and one fit of Table I recalculated here); 128 Thellier-Coe, 105 with the determination of Table III; 21 rock-magnetic powders; 34 thermal-stability pieces | the files; Tables I, III and IV |
| samples | 129 cores and hand blocks | the files; text |
| sites | 25: one row for each of the 15 flows (13 with a direction and VGP), and 10 paleointensity rows with the VADM | Tables 1 to 4 |
| locations | 1, with the grouped mean poles of Table 3 in its description | Tables 1 and 3 |
| ages | 15 | Table 1 |
| criteria | 7: the thresholds of class C of Table II | Table II |

## Recalculation of the published results

`report.md` gives the recalculated and published values side by side. The calculations are those of PmagPy (section "PmagPy").

- **Stored fits.** All 141 fits saved in the `.rs3` files are recalculated from the measurements entered, to 0.15° in direction and 0.1° in MAD.
- **Table I.** For 130 of the 134 specimens the stored fit is the one printed, in range and to 0.15° in direction. Three of the others are explained in items 9 to 11. The fourth is OL0302A, 0.17° away, which is within the printed precision of its declination.
- **Site means (Table 2).** 12 of the 13 recalculate to their printed precision in direction, α95 and n as hierarchical Fisher means, with the specimens of each core averaged first (each hand block for GTX08 and GTX10). GTX09 does not (item 12).
- **VGPs (Table 3).** All 13, with dp and dm, recalculate from the site means and the coordinates of Table 1.
- **Thellier-Coe determinations (Table III).** 103 of the 105 with values recalculate in N, B (within 0.05 μT, or 0.1 percent above 50 μT) and β (within 0.0015), among them all 51 accepted. 86 also agree in f (within 0.025) and q (within 3 percent), 46 of them accepted; the anchored MAD agrees for 102. Two ranges are inferred (item 24). The two that do not recalculate are rejected determinations: GTX080101 (58.51 μT against 58.80) and LTD GTX0110C (β 0.062 against 0.060).
- **Site paleointensities (Tables 2 and 4).** All 10 site means and standard deviations of Table 2 recalculate from the accepted determinations of Table III, and so do those without and with LTD and the numbers of each class in Table 4, except OL01 (item 27).
- **VADMs (Table 3).** All 10, with their uncertainties, from the site paleointensities and the latitudes of Table 1.
- **Thermal stability (Table IV).** 46 of the 55 printed ratios recalculate within 0.005 from the cycles (item 32).
- **Not recalculated.** δ(CK) and α of Table III, which are entered as printed. The paper gives no rock-magnetic values per sample.

## Choices and inferences

### Files of the directions

1. **Measurements (files).** The 99 specimens of the GTX sites, measured at Burgos, have a 2G binary file and a `.rs3` file. Read with PmagPy, 93 pairs have the same steps, with the same directions and moments to 0.1 percent.
   - The other six 2G files hold steps that the `.rs3` files lack: a second measurement at one temperature (GTX0101B, GTX0208A, GTX080202A) or a last step at 100 mT (GTX0607A, GTX0710A, GTX080301B).
   - The stored fit of GTX0101B is reproduced only with the measurements of the 2G file, which include both measurements at 360 °C. That of GTX080202A is reproduced with the second of its two measurements at 300 °C, the one kept in the `.rs3` file; its row says so.
   - The measurements of the GTX sites are therefore taken from the 2G files. The OL sites, measured in Barcelona, have only `.rs3` files.
2. **Orientation (files).** The orientation and the fits are taken from the `.rs3` files, which Table I follows.
   - For the 19 specimens of GTX08 and GTX10 the 2G header gives the orientation of the hand block and the `.rs3` file that of the core drilled from it in the laboratory.
   - The two specimens of core GTX0401 have different orientations in their `.rs3` files. The one entered (azimuth 62, dip −78) is the one with which the stored fits give the directions of Table I, and also the one in both 2G files. The geographic direction of GTX0401A is recalculated with it, and its row says so.
3. **Steps with ID M (files, text).** The `.rs3` files of the OL sites mark the steps with ID M, and the heading of their step column has no unit. The text says that these sites were demagnetized thermally, so the steps are read as °C (`m_rows='T'` in PmagPy).
4. **Specimen names (files).** Remasoft keeps 8 characters of a name read from a 2G file, so GTX080101A and GTX080102A both hold the name GTX08010. The specimens are named after their files (`specname=True` in PmagPy).

### Samples and sites

5. **Samples.** A sample is a core: the specimen name without its final letter (GTX0202A and GTX0202B are specimens of GTX0202, OL01-2B of OL01-2). The cores of GTX08 and GTX10 were drilled in the laboratory from three oriented hand blocks per site (GTX080102A is a specimen of core GTX080102 of block GTX0801).
6. **Positions and ages (table).** Each site has the coordinates of Table 1. The ± of the ages is entered as `age_low` and `age_high`, because Table 1 does not say whether it is one or two standard deviations.
7. **Laboratories (text).** Burgos for the GTX sites, and the CCiTUB-Geo3BCN laboratory in Barcelona for the OL sites. Geo3BCN is the former ICTJA, so its MagIC vocabulary name is "Laboratory of Paleomagnetism (CSIC-ICTJA and Universitat de Barcelona, Spain)".

### Directions

8. **Line flag O (inferred).** Table I marks the flags as "OA: direction calculated anchored to the origin" and "O: direction calculated including the origin". All 38 stored fits flagged O are recalculated exactly as lines anchored to the origin, and not as free lines with the origin added. In another archive (Svalbard, figshare 21641594) the 13 fits flagged O are free lines with the origin added, so the flag alone does not tell which calculation Remasoft made. `convert_2_magic.rs3` recalculates each stored line with `pmag.domean` and writes it as the calculation that reproduces it: these fits are entered as `DE-BFL-A`, with the MAD in `dir_mad_anc`, and each row says so. For GTX0101B the converter, which checks the steps of the `.rs3` file, does not reproduce the stored line, which the measurements of the 2G file do (item 1); its row says so.
9. **GTX0108A (inferred).** Table I gives 339.5/83.9, 4.2° from the stored direction (298.7/84.0), with the same range and MAD. The site mean of GTX01 in Table 2 recalculates with the stored direction and not with the printed one, so the stored direction is entered.
10. **GTX0702A (inferred).** The file holds a fit over 390–520 °C. Table I gives one over 100–390 °C, which is reproduced from the measurements, and the site mean of GTX07 recalculates with it. That fit is entered as a row of its own, described as recalculated here, and the stored fit is kept and flagged b.
11. **GTX0103A (inferred).** The specimen was heated to 420 °C and then demagnetized by alternating fields. The stored direction and MAD are those of a fit from the heating step to 100 mT (23 measurements), not of the stated 35–100 mT (Table I: N = 9). The fit has both protocol codes, and `meas_step_min` is 0 T, the field of the heating step.
12. **GTX09 (table).** The site mean does not recalculate. The specimens that Table I does not discard give 35.4/47.4, α95 17.7°, n = 6, which is 1.3° from the printed 36.0/46.2, α95 18.8°. No subset of the specimens comes closer. The printed values are entered, and the row says so.
13. **N of Table I.** For 17 specimens the printed N differs from the number of measurements with which the stored line is reproduced. For most it differs by one; GTX0502A, GTX0905A, GTX100101A and GTX0103A (item 11) differ by more. The number of measurements is entered as `dir_n_measurements`, and each row gives the printed N.
14. **Discarded specimens (table).** The 23 specimens marked * in Table I keep their fits, flagged b.
15. **GTX06 (text).** No site mean: Table 2 gives 0/9, and the text describes anomalous directions and very low intensities. The site row has no direction and is flagged b.
16. **Number of samples.** `dir_n_samples` is the n of Table 2: cores for most sites, hand blocks for GTX08 and GTX10. `dir_k`, which the paper does not give, is entered from the recalculation where the mean is reproduced.
17. **Mean poles.** Table 3 gives mean poles for groups of sites with the same age (P1, P2, P3). The authors use only the VGPs of single flows in their discussion, so the groups are in the location description, not in the location results.

### Paleointensity

18. **Files (files).** The 142 `.TDT` files are 128 specimens, the 128 rows of Table III: 82 standard Thellier-Coe experiments and 46 with a low-temperature demagnetization (LTD) after each heating step, whose files are named `LTD_*.TDT`. The other 14 files (`*_C.TDT`, `*_CC.TDT`) are copies of 12 of them with some measurements deleted. The text speaks of 129 specimens, 83 without LTD (item 27).
19. **Names (NSH, files).** The specimen names inside the files are not unique: an LTD file has the name of the standard specimen of the same core with a number in front (`45. GTX02061`), a corrected copy has the name of its original, and `LTD_GTX0405B.TDT` holds the name `T`. The specimens are named after their files, with the suffix `t` (`GTX0206B1t`, `LTD_GTX02061t`): the microcores are distinct from the demagnetized specimens, and `GTX0204B.TDT` has the name of a demagnetized specimen. Each description gives the file and the name of Table III. Table III names the specimens of GTX10 without the 0 of the block (GTX1011 is `GTX10011.TDT`).
20. **Samples (files).** A microcore belongs to the core in its name (GTX0206B1 to GTX0206, OL0102A to OL01-2), or to the hand block where its name gives no core: the LTD specimens of GTX08 (GTX08021 to block GTX0802), and those of GTX10 and GTX11 (GTX10011 to GTX1001, GTX11011 to GTX1101). Eight blocks are entered as samples of their own.
21. **Moments (inferred).** The files give no unit. The values are read as A/m (`magn_volume`): the NRMs of the GTX microcores agree with the volume-normalized NRMs of the 2G files of the same cores within a factor of 0.9 to 1.3. The paleointensities do not depend on the unit.
22. **Laboratory field (files, text).** 40 μT, along −Z in specimen coordinates: the median direction of the pTRMs gained is within 10° of −Z for 121 of the 128 specimens.
23. **Corrected copies (table, files).** Each copy is its original file with whole steps or pTRM checks deleted. Where Table III names a copy (nine specimens, among them GTX0308B_c, GTX0503B_cc and OL0204C_c), the specimen is entered from its original file and the measurements that the copy lacks are flagged bad, with a description. The other five copies (GTX0503B_C, GTX0504B_c and _cc, GTX0609B1_C, GTX11032_C) are not entered: for GTX0504B, GTX0609B1 and GTX11032 Table III gives the original, and for GTX0503B the copy _cc.
24. **Two ranges (inferred).** For two determinations the printed range holds a different number of steps from the printed N, and one other range gives N, B, β, f and q of Table III: LTD GTX08022 (390–540 °C printed, 390–560 °C entered) and GTX1011 (20–500 °C printed, 200–500 °C entered). The rows say so.
25. **Ranges from 20 °C.** In Table III a range from 20 °C starts at the NRM, which is one of the N points (in Praia Grande, processed with ThellierTool 4.22, it is not).
26. **LTD (text).** "A LTD after each heating step and before each measurement": the heating steps of the LTD experiments carry LT-LT-Z, and the experiments LP-LT. Whether the NRM was measured after an LTD is not said, so the NRM step does not carry it.
27. **Counts of Tables 2 and 4 (table).** Table 4 counts one accepted LTD determination for OL01 (38.8 μT, class C), which is LTD OL0106B, rejected in Table III ("(*) Low temp."); Table 2 gives OL01 no paleointensity. The determination is entered as rejected, as in Table III, and OL01 has no paleointensity row. Tables 2 and 4 count 9 Thellier-Coe specimens for OL03 (7 without LTD); Table III and the archive have 8 (6).
28. **Results (table).** Every determination of Table III is entered on its specimen row as printed (B, ΔB, N, β, f, q, δ(CK), MAD′, α), with `result_quality` g for classes A to C and b for R, and the class and observation in the description. Rejected specimens without values have a row without a result. The site rows give B and ΔB of Table 2 and the VADM of Table 3, with the means of Table 4 in the description. The criteria table holds the thresholds of class C, the lowest accepted; the descriptions give those of A and B.

### Rock magnetism and thermal stability

29. **Powders (files, text).** "One grinded representative sample per lava flow": 21 sets of four curves (IRM acquisition, back field, hysteresis loop, magnetization against temperature), two for each OL site. Each powder is a specimen with the suffix `r`, in the sample of its core, with the weight of the files. GTX0208B and GTX0307inf have a second set of curves with the suffix `_MAL`, entered as specimens of their own; the paper does not say what they are.
30. **No values (table).** The paper plots the hysteresis ratios (Fig. 2C) but lists no values, so the specimen rows carry none. `report.md` gives Bcr, Ms, Mr and Bc calculated from the curves, as a check of PmagPy (section "PmagPy").
31. **Thermal-stability pieces (inferred).** Table IV gives MAG2F/MAG1I "only when the same specimen was analyzed for both experiments". The cycles of a row whose files give the same weight are entered as one specimen (suffix `s`), and a cycle of another weight as a second one (`s2`): GTX0505 (T2), GTX1102, OLO106, OLO404 and OLO407 (406 and 407 mg). Of the rows with two cycles, those without MAG2F/MAG1I are those of two weights; GTX0505, whose T2 cycle has another weight, has one.
32. **Table IV (table, inferred).** The ratios are recalculated as the magnetization at the end of a cycle over that at the start, at the same temperature. For GTX0505 the cycle to 500 °C gives the ratio printed for T3 and the cycle to 600 °C that printed for T1, and MAG2F/MAG1I (1.003) is not reproduced. GTX0501 (0.990 and 1.042 against 0.966 and 1.035), GTX0803 at 250 °C, GTX1003 (rejected for alteration) and OLO407 at 450 °C differ by more than 0.005. The printed values are in the descriptions. GTX0604 has two cycles of one specimen to 560 °C, for the one T1 of the table; both give it. OLO202 and OLO401: "No data".
33. **Field of the cycles (files).** The files give 347 to 362 Oe (about 35 mT); the text gives 38 mT.

## Questions for the authors

1. What the ± of the ages in Table 1 is.
2. For the fits flagged O: was the line anchored to the origin?
3. GTX0108A and GTX0702A: are the direction (GTX0108A) and range (GTX0702A) of Table I the ones intended?
4. GTX09: which specimens enter the site mean of Table 2?
5. The unit of the moments in the `.TDT` files, and the volumes of the microcores.
6. LTD GTX08022 and GTX1011: are the ranges 390–560 °C and 200–500 °C?
7. OL01 and OL03: is LTD OL0106B accepted (Table 4) or rejected (Table III), and which is the ninth specimen of OL03?
8. What the `_MAL` curves of GTX0208B and GTX0307inf are, and the hysteresis parameters of Fig. 2C.
9. GTX0505 in Table IV: which cycle is T1 and which T3?

## PmagPy

### Changes the build needs

Merged into PmagPy `master` and not yet in a release:

- [#1023](https://github.com/PmagPy/PmagPy/pull/1023): 2G binary files.
- [#1025](https://github.com/PmagPy/PmagPy/pull/1025): `rs3` reads rows with ID M, and names specimens after their files (`specname`).
- [#1053](https://github.com/PmagPy/PmagPy/pull/1053): `rs3` recalculates each stored line with `pmag.domean` and writes it as the calculation that reproduces it, so the fits flagged O that are anchored lines are written as `DE-BFL-A` (item 8). Made for this study and the Svalbard archive.
- [#1054](https://github.com/PmagPy/PmagPy/pull/1054): `pmag.domean` counts the origin in the centre of mass of a line with the origin (`DE-BFL-O`), and not in its number of measurements (issue [#1047](https://github.com/PmagPy/PmagPy/issues/1047)).
- [#1055](https://github.com/PmagPy/PmagPy/pull/1055): `pmag.domean` gives a MAD of 0, not NaN, for a free line through two steps.
- [#1057](https://github.com/PmagPy/PmagPy/pull/1057): `convert_2_magic.tdt` reads `.TDT` files (it read only `.tdt`, and none of the 142 files of this archive), keeps a specimen name with a space as one field (`45. GTX02061`), and takes `moment_units="A/m"` (written to `magn_volume`, with no assumed volume); it also stops on a field that holds two values, and `pmag.measurements_methods3` keeps tail checks that do not follow their in-field step (this archive has none). Tested on 488 ThellierTool files from seven archives; the tests use `GTX0206B1.TDT` and `LTD_GTX02061.TDT` and check N, B, β, f and q of Table III.

- [#1058](https://github.com/PmagPy/PmagPy/pull/1058): `convert_2_magic.vftb` writes a thermomagnetic curve as measured at temperature in the field (`meas_temp`, `meas_field_dc`; it wrote `treat_temp`, `treat_dc_field`). Test with `GTX0308B_500.rmp`.
- [#1059](https://github.com/PmagPy/PmagPy/pull/1059): `rockmag.process_backfield_data` accepts a curve whose first step is at zero field (issue [#1049](https://github.com/PmagPy/PmagPy/issues/1049): all 21 back-field curves of the archive failed); `rockmag.process_hyst_loop` leaves out the initial magnetization curve at the start of a loop file (the second point of issue [#1048](https://github.com/PmagPy/PmagPy/issues/1048): all 21 loops failed). Tests with `GTX0208B.coe` and `GTX0208B.hys`.

### Calculations made with PmagPy

| Calculation | PmagPy function |
| --- | --- |
| Line fits: free, anchored, with the origin as a point | `pmag.domean` |
| Fisher means (the site means are means of the core or block means); angles; geographic directions | `pmag.fisher_mean`; `pmag.angle`; `pmag.dogeo` |
| VGPs; VADMs | `pmag.dia_vgp`; `pmag.b_vdm` |
| Arai plot and its statistics (B, standard error, β, f, q); anchored MAD | `pmag.sortarai`, `pmag.find_dmag_rec`, `pmag.PintPars`; `pmag.domean` |
| Bcr; Ms, Mr, Bc (report only) | `rockmag.process_backfield_data`; `rockmag.process_hyst_loop` |
| Validation | `pmagpy.magic_validation.validate` |

The line fits were first written in `convert.py`. With `pmag.domean` for the free and anchored lines the contribution was unchanged, byte for byte, and so it was when the line with the origin and the recoding of the flag O moved to PmagPy (#1053, #1054), except for the wording of the descriptions of 40 fits.

### Calculations not made with PmagPy

- **Hysteresis parameters from loops measured at uneven fields.** `process_hyst_loop` resamples a loop on an even grid of the median field step. These loops are measured at about 50 mT steps near zero field, and the function gives Mr 94 percent below to 55 percent above, and Bc 89 percent below to 41 percent above, the values read from the measured branches (`report.md`), which is the first point of issue #1048. As no values are entered, the contribution does not depend on it.
- **Thermal-stability ratios** (Table IV): a ratio of two magnetizations, calculated in `magnetization_ratio`.
- **Matching the corrected copies with their originals**, and the table of the paper: by their nature in `convert.py`.
