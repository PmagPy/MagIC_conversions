# La Garrotxa: build report

Written by `convert.py`; do not edit. Study: Vernet et al. (2026), doi:10.1344/GeologicaActa2026.24.15; data doi:10.5281/zenodo.20326424. `README.md` explains the sources and the decisions.

## Contents of the contribution

| Table | Rows | Source |
| --- | --- | --- |
| measurements | 21022: 1531 demagnetization steps from the 99 2G files (GTX sites), 436 from the 35 `.rs3` files of the OL sites, 4035 Thellier-Coe steps (`.TDT`), 6730 points of rock-magnetic curves and 8290 of thermal-stability cycles (VFTB) | files |
| specimens | 467 rows for 317 specimens: 134 demagnetized (the stored fits in specimen and geographic coordinates, and 2 rows of a Table I fit recalculated here), 128 Thellier-Coe (105 with a determination of Table III), 21 rock-magnetic powders, 34 thermal-stability pieces | files; Tables I, III and IV |
| samples | 129 cores and hand blocks | files; text |
| sites | 25: 15 with the direction and VGP (13) or a description, and 10 paleointensities | Tables 1 to 4 |
| locations | 4: the volcanic field, and the mean poles of Table 3 | Tables 1 and 3 |
| ages | 15 | Table 1 |
| criteria | 7 | Table II |

## Validation with the rules of MagIC (`pmagpy.magic_validation`)

No problems.

## Uploading to MagIC

`magic_contribution.txt` holds every table except the contribution table, which is made on MagIC when the file is uploaded (the file is written with `ipmag.upload_magic`). Enter there:

- Reference: 10.1344/GeologicaActa2026.24.15
- Laboratories: Paleomagnetic and Rock Magnetic Laboratory (Universidad de Burgos, Spain); Laboratory of Paleomagnetism (CSIC-ICTJA and Universitat de Barcelona, Spain)
- Description: Converted from the laboratory files archived by the authors (https://doi.org/10.5281/zenodo.20326424) and from the paper and its appendix. Sources, choices and checks are documented at <permalink>.

`<permalink>` is the link to this study folder at the commit the upload is made from, so that it keeps pointing to the files that made the contribution. After committing and pushing, `python common/studies.py --permalink vernet_2026_garrotxa` prints it; enter that commit as `upload_commit` in `study.json`.

## The two kinds of direction files

The 99 GTX specimens have both a 2G binary file and a `.rs3` file. Read with `convert_2_magic._2g_bin` and `convert_2_magic.rs3`, 93 have the same steps, with directions within 0.00° and moments within 0.10 percent. The others:

| specimen | steps_2g | steps_rs3 | repeats | extra |
| --- | --- | --- | --- | --- |
| GTX0101B | 18 | 17 | 1 |  |
| GTX0208A | 18 | 17 | 1 |  |
| GTX0607A | 16 | 15 | 0 | 100 mT |
| GTX0710A | 16 | 15 | 0 | 100 mT |
| GTX080202A | 11 | 10 | 1 |  |
| GTX080301B | 16 | 15 | 0 | 100 mT |

The orientation in the 2G header differs from that of the `.rs3` files for 19 specimens (GTX080101A, GTX080102A, GTX080102B, GTX080103A, GTX080201A, GTX080202A, GTX080203A, GTX080301A, GTX080301B, GTX080303A, GTX100101A, GTX100101B, GTX100102A, GTX100103A, GTX100201A, GTX100202A, GTX100203A, GTX100301A, GTX100302A): all the specimens of GTX08 and GTX10, cores drilled in the laboratory from hand blocks oriented in the field. The 2G header gives one orientation for all the cores of a block, and the `.rs3` files the orientation of each core, which the directions of Table I follow and which is entered: the cores are the samples, and the site means average the blocks. For core GTX0401 the `.rs3` files of its two specimens differ, and the orientation entered is the one with which Table I is reproduced, also that of the 2G files.

Warnings of the converters: 75 from `rs3` (38 × "fit is flagged O (origin included) but is the line anchored to the origin; written as DE-BFL-A"; 35 × "rows with ID M read as thermal (degrees C) steps"; 2 × "fit is not reproduced by the calculation its flag names (see the description)"), 0 from `_2g_bin`.

## Stored fits recalculated

141 stored line fits, recalculated from the measurements entered between their stated limits: 133 as an anchored line, 8 as a free line.

| flag | calculation | fits |
| --- | --- | --- |
| O | anchored | 38 |
| OA | anchored | 95 |
| none | free | 8 |

`flag` is the Remasoft line flag in the file. `convert_2_magic.rs3` recalculates each stored line with `pmag.domean` and writes it as the calculation that reproduces it: the fits flagged O are anchored lines, entered as DE-BFL-A (README.md, item 8).

| specimen | dir_comp | calculation | earlier_start | angle | stored_mad | mad |
| --- | --- | --- | --- | --- | --- | --- |
| GTX0103A | C1 | anchored | True | 0.04 | 9.8 | 9.8 |

## Table I against the stored fits

For each of the 134 specimens of Table I, the stored geographic fit closest to the printed direction. 131 agree within 0.15°. Differences:

| specimen | file_range | table_range | file_line | table_line | n_fit | n_table | angle | mad_file | mad_table | discarded |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTX0101B | 360-580 °C | 360-580 | OA | OA | 11 | 10 | 0.00 | 17.6 | 17.6 | False |
| GTX0102A | 420-560 °C | 420-560 | O | OA | 7 | 7 | 0.00 | 15.0 | 15.0 | False |
| GTX0103A | NRM-100 mT | 35-100 | OA | OA | 23 | 9 | 0.00 | 9.8 | 9.8 | False |
| GTX0108A | 330-540 °C | 330-540 | OA | OA | 9 | 9 | 4.21 | 14.7 | 14.7 | False |
| GTX0406A | 330-540 °C | 330-540 | OA | OA | 9 | 8 | 0.00 | 8.6 | 8.6 | False |
| GTX0407A | 330-540 °C | 330-540 | OA | OA | 9 | 8 | 0.00 | 6.9 | 6.9 | False |
| GTX0408A | 200-540 °C | 200-540 | OA | OA | 12 | 11 | 0.00 | 8.0 | 8.0 | False |
| GTX0501A | 200-580 °C | 200-580 | OA | OA | 14 | 13 | 0.00 | 0.8 | 0.8 | False |
| GTX0502A | 6-100 mT | 6-100 | OA | OA | 19 | 14 | 0.00 | 0.6 | 0.6 | False |
| GTX0502B | 330-580 °C | 330-580 | OA | OA | 11 | 10 | 0.00 | 1.3 | 1.3 | False |
| GTX0503A | 330-580 °C | 330-580 | OA | OA | 11 | 10 | 0.00 | 2.1 | 2.1 | False |
| GTX0505A | 250-580 °C | 250-580 | OA | OA | 13 | 12 | 0.00 | 2.3 | 2.3 | False |
| GTX0506A | 15-100 mT | 15-100 | OA | OA | 13 | 12 | 0.00 | 0.6 | 0.6 | False |
| GTX0702A | 390-520 °C | 100-390 | OA | OA | 6 | 8 | 26.96 | 9.9 | 17.0 | False |
| GTX0901B | 20-100 mT | 20-100 | O | O | 12 | 11 | 0.00 | 1.1 | 1.1 | False |
| GTX0904A | 300-520 °C | 300-520 | O | O | 10 | 9 | 0.00 | 1.6 | 1.6 | True |
| GTX0905A | 10-100 mT | 10-100 | O | O | 14 | 17 | 0.00 | 0.7 | 0.7 | False |
| GTX100101A | 5-100 mT | 5-100 | O | O | 15 | 18 | 0.00 | 1.0 | 1.0 | False |
| GTX100301A | 360-560 °C | 360-560 | O | O | 9 | 11 | 0.00 | 4.5 | 4.5 | False |
| GTX100302A | 360-560 °C | 360-560 | O | O | 9 | 11 | 0.00 | 4.9 | 4.9 | True |
| OL0302A | 350-560 °C | 350-560 | OA | OA | 6 | 6 | 0.17 | 1.7 | 1.7 | False |

`n_fit` is the number of measurements between the limits, with which the stored line is reproduced. `file_line` is the flag in the file.

## Site means (Table 2)

Hierarchical Fisher means of the characteristic fits that Table I does not discard: the specimens of each core (each hand block for GTX08 and GTX10) averaged first.

| site | dec_pub | inc_pub | a95_pub | n_pub | dec | inc | a95 | k | n | n_specimens | angle | reproduced | specimen_mean_reproduced |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTX03 | 10.8 | 42.8 | 2.9 | 9 | 10.8 | 42.8 | 2.9 | 311.8 | 9 | 10 | 0.05 | True | False |
| OL03 | 356.8 | 55.7 | 7.1 | 6 | 356.8 | 55.7 | 7.1 | 90.9 | 6 | 6 | 0.05 | True | True |
| OL04 | 2.8 | 53.8 | 4.4 | 9 | 2.8 | 53.8 | 4.4 | 137.6 | 9 | 9 | 0.01 | True | True |
| GTX08 | 19.2 | 18.3 | 10.8 | 3 | 19.2 | 18.3 | 10.8 | 132.1 | 3 | 10 | 0.04 | True | False |
| GTX09 | 36.0 | 46.2 | 18.8 | 6 | 35.4 | 47.4 | 17.7 | 15.2 | 6 | 8 | 1.27 | False | False |
| OL01 | 18.9 | 53.4 | 13.7 | 7 | 18.9 | 53.4 | 13.7 | 20.3 | 7 | 7 | 0.03 | True | True |
| GTX02 | 7.4 | 51.2 | 4.2 | 6 | 7.4 | 51.2 | 4.2 | 253.6 | 6 | 8 | 0.01 | True | False |
| GTX05 | 9.5 | 65.8 | 3.4 | 9 | 9.5 | 65.8 | 3.4 | 232.9 | 9 | 10 | 0.03 | True | False |
| GTX01 | 155.7 | 78.2 | 5.5 | 10 | 155.7 | 78.2 | 5.5 | 77.1 | 10 | 10 | 0.03 | True | True |
| GTX04 | 31.0 | 57.7 | 5.9 | 7 | 31.0 | 57.7 | 5.9 | 105.2 | 7 | 7 | 0.04 | True | True |
| OL02 | 1.8 | 65.6 | 2.1 | 10 | 1.8 | 65.6 | 2.1 | 529.4 | 10 | 10 | 0.05 | True | True |
| GTX07 | 1.8 | 52.0 | 5.3 | 9 | 1.8 | 52.0 | 5.3 | 96.3 | 9 | 10 | 0.03 | True | False |
| GTX10 | 29.1 | 58.6 | 8.6 | 3 | 29.1 | 58.6 | 8.6 | 206.6 | 3 | 6 | 0.02 | True | False |

`specimen_mean_reproduced`: the Fisher mean of the specimens, without averaging each sample first, gives the printed mean for 6 of the 13 sites (in direction within 0.15° and α95 within 0.05°).

GTX09: of the 1010 subsets of the specimens of the site (with those Table I discards), 0 give the printed mean (within 0.15° in direction, 0.05° in α95, the same n). The closest in direction: 36.9/46.4, α95 26.7°, n = 4, 0.62° away (GTX0901A, GTX0903A, GTX0906B, GTX0907A); the closest with n = 6: 36.2/46.9, α95 17.6°, 0.73° away (GTX0901A, GTX0902A, GTX0903A, GTX0905A, GTX0906B, GTX0907A).

## VGPs (Table 3)

From the published site mean and the site coordinates of Table 1 (`pmag.dia_vgp`):

| site | lat_pub | lon_pub | dp_pub | dm_pub | lat | lon | dp | dm | angle |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTX03 | 70.5 | 151.8 | 2.22 | 3.59 | 70.5 | 151.8 | 2.22 | 3.59 | 0.02 |
| OL03 | 83.6 | 206.3 | 7.27 | 10.16 | 83.6 | 206.3 | 7.27 | 10.16 | 0.02 |
| OL04 | 81.9 | 165.9 | 4.30 | 6.15 | 81.9 | 165.9 | 4.30 | 6.15 | 0.02 |
| GTX08 | 53.1 | 149.7 | 5.83 | 11.22 | 53.1 | 149.7 | 5.83 | 11.22 | 0.05 |
| GTX09 | 57.4 | 107.4 | 15.43 | 24.08 | 57.4 | 107.4 | 15.43 | 24.08 | 0.04 |
| OL01 | 73.1 | 115.3 | 13.25 | 19.06 | 73.1 | 115.3 | 13.26 | 19.06 | 0.05 |
| GTX02 | 78.1 | 150.3 | 3.86 | 5.69 | 78.1 | 150.3 | 3.86 | 5.69 | 0.05 |
| GTX05 | 81.0 | 47.5 | 4.52 | 5.54 | 81.0 | 47.5 | 4.52 | 5.54 | 0.03 |
| GTX01 | 21.1 | 12.3 | 9.77 | 10.36 | 21.1 | 12.3 | 9.77 | 10.37 | 0.06 |
| GTX04 | 66.2 | 91.1 | 6.36 | 8.66 | 66.2 | 91.1 | 6.36 | 8.66 | 0.03 |
| OL02 | 84.2 | 14.7 | 2.78 | 3.42 | 84.2 | 14.7 | 2.78 | 3.42 | 0.02 |
| GTX07 | 80.4 | 173.5 | 4.96 | 7.25 | 80.4 | 173.5 | 4.96 | 7.25 | 0.05 |
| GTX10 | 67.9 | 90.2 | 9.48 | 12.77 | 67.9 | 90.2 | 9.48 | 12.77 | 0.03 |

The poles of all 13 agree within 0.06°; dp and dm agree to the printed digit for 11, and differ in the last digit for OL01 (dp 13.26, dm 19.06), GTX01 (dp 9.77, dm 10.37).

## Mean poles (Table 3)

The mean poles of groups of sites with the same 40Ar/39Ar age, against the Fisher mean of the VGPs of Table 3 of their sites (`pmag.fisher_mean`); `angle_of_mean_direction_pole` is the angle to the pole of the Fisher mean of their site directions (Table 2), which the published poles are not. The mean VADM of P1 is recalculated as the mean and standard deviation of the VADMs of its sites.

| group | sites | lat_pub | lon_pub | A95_pub | lat | lon | A95 | angle | angle_of_mean_direction_pole | vadm_pub | vadm | vadm_sigma_pub | vadm_sigma | reproduced |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | GTX03:OL03:OL04 | 79.4 | 165.0 | 13.1 | 79.4 | 165.0 | 13.1 | 0.04 | 0.49 | 6.54 | 6.54 | 0.21 | 0.21 | True |
| P2 | GTX08:GTX09:OL01 | 62.6 | 126.7 | 24.0 | 62.6 | 126.7 | 24.0 | 0.03 | 1.34 |  |  |  |  | True |
| P3 | GTX04:OL02 | 77.1 | 78.2 | 52.6 | 77.1 | 78.2 | 52.6 | 0.03 | 0.64 |  |  |  |  | True |

## Thellier-Coe files

The archive holds 142 `.TDT` files: 128 specimens (82 standard Thellier-Coe experiments, 46 with a low-temperature demagnetization after each heating step, `LTD_*.TDT`), the 128 rows of Table III, and 14 corrected copies (`*_C.TDT`, `*_CC.TDT`) of 12 of them. They are converted with `convert_2_magic.tdt` (each specimen named after its file, moments in A/m, laboratory field along −Z). The median direction of the pTRMs gained by a specimen is within 10° of −Z for 121 of the 128 specimens, and at most 33.5° from it (LTD_GTX0902St).

The unit of the moments of the `.TDT` files: the NRM of a microcore, read as A/m, over the median NRM of the demagnetized specimens of the same core (2G and `.rs3` files, A/m), where the name of the microcore gives the core: 70 microcores, median 1.04, 10th to 90th percentile 0.33 to 1.78, range 0.11 to 4.38 without LTD, and 36 microcores, median 0.74, 10th to 90th percentile 0.28 to 2.96, range 0.16 to 5.48 with LTD. In mA/m the ratios would be a thousand times smaller.

Each corrected copy is its original file with the measurements listed deleted, and the others unchanged. Where Table III names the copy (`interpreted`), the specimen is entered from its original file and those measurements are flagged bad; the other copies are not entered.

| copy | original | rows | removed | steps | interpreted |
| --- | --- | --- | --- | --- | --- |
| GTX0308B_C | GTX0308B | 39 | 1 | 480 °C LT-PTRM-I | True |
| GTX0309B_C | GTX0309B | 39 | 1 | 480 °C LT-PTRM-I | True |
| GTX0503B_C | GTX0503B | 39 | 5 | 420 °C LT-PTRM-I, 520 °C LT-T-Z, 480 °C LT-PTRM-I, 520 °C LT-T-I, 520 °C LT-PTRM-I | False |
| GTX0503B_CC | GTX0503B | 39 | 5 | 420 °C LT-PTRM-I, 520 °C LT-T-Z, 480 °C LT-PTRM-I, 520 °C LT-T-I, 520 °C LT-PTRM-I | True |
| GTX0504B_c | GTX0504B | 34 | 2 | 540 °C LT-T-Z, 540 °C LT-T-I | False |
| GTX0504B_cc | GTX0504B | 34 | 4 | 450 °C LT-T-Z, 450 °C LT-T-I, 540 °C LT-T-Z, 540 °C LT-T-I | False |
| GTX0505_C | GTX0505 | 34 | 1 | 480 °C LT-PTRM-I | True |
| GTX0605A1_C | GTX0605A1 | 43 | 4 | 360 °C LT-T-Z, 300 °C LT-PTRM-I, 360 °C LT-T-I, 360 °C LT-PTRM-I | True |
| GTX0609B1_C | GTX0609B1 | 24 | 3 | 420 °C LT-T-Z, 360 °C LT-PTRM-I, 420 °C LT-T-I | False |
| GTX10022_C | GTX10022 | 43 | 16 | 420 °C LT-T-Z, 360 °C LT-PTRM-I, 420 °C LT-T-I, 420 °C LT-PTRM-I, 560 °C LT-T-Z, 520 °C LT-PTRM-I, 560 °C LT-T-I, 580 °C LT-T-Z, 580 °C LT-T-I, 600 °C LT-T-Z, 560 °C LT-PTRM-I, 600 °C LT-T-I, 620 °C LT-T-Z, 620 °C LT-T-I, 640 °C LT-T-Z, 640 °C LT-T-I | True |
| GTX11032_C | GTX11032 | 39 | 4 | 520 °C LT-T-Z, 480 °C LT-PTRM-I, 520 °C LT-T-I, 520 °C LT-PTRM-I | False |
| OL0108A_c | OL0108A | 43 | 2 | 540 °C LT-T-Z, 540 °C LT-T-I | True |
| OL0204C_C | OL0204C | 34 | 4 | 480 °C LT-T-Z, 420 °C LT-PTRM-I, 480 °C LT-T-I, 480 °C LT-PTRM-I | True |
| OL0410B_C | OL0410B | 39 | 4 | 420 °C LT-T-Z, 360 °C LT-PTRM-I, 420 °C LT-T-I, 420 °C LT-PTRM-I | True |

Table III against the converted measurements: best-fit line of the Arai plot over the printed range (`pmag.sortarai`, `pmag.PintPars`), from the measurements flagged good, and the anchored MAD of the same steps (`pmag.domean`). δ(CK) and α are entered as printed and not recalculated. `B_agrees`: N, B within 0.05 μT (0.1 percent above 50 μT) and β within 0.0015; `fq_agree`: f within 0.025 and q within 3 percent; `mad_agrees`: MAD within 0.05°. The rows where all agree are not shown.

| specimen | cls | range | N_pub | N | B_pub | B | dB_pub | dB | beta_pub | beta | f_pub | f | q_pub | q | mad_pub | mad | B_agrees | fq_agree | mad_agrees |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LTD GTX0110C | R | 150-320 | 5 | 5 | 11.74 | 11.74 | 0.73 | 0.73 | 0.060 | 0.062 | 0.58 | 0.58 | 6.40 | 6.40 | 24.12 | 24.12 | False | True | True |
| GTX0201B | R | 100-390 | 7 | 7 | 30.60 | 30.61 | 6.55 | 6.55 | 0.214 | 0.214 | 0.61 | 0.56 | 1.52 | 1.23 | 10.72 | 10.72 | True | False | True |
| GTX0204B | R | 20-640 | 19 | 19 | 10.19 | 10.20 | 1.44 | 1.44 | 0.141 | 0.141 | 0.83 | 0.62 | 3.19 | 0.76 | 28.35 | 28.35 | True | False | True |
| GTX0306B | R | 390-600 | 10 | 10 | 53.29 | 53.29 | 7.93 | 7.93 | 0.149 | 0.149 | 0.71 | 0.62 | 3.88 | 3.00 | 10.82 | 10.82 | True | False | True |
| GTX0307B | R | 390-580 | 9 | 9 | 61.09 | 61.10 | 6.54 | 6.54 | 0.107 | 0.107 | 0.65 | 0.70 | 5.17 | 5.50 | 10.44 | 10.44 | True | False | True |
| GTX0405B | R | 100-330 | 5 | 5 | 31.40 | 31.40 | 5.21 | 5.21 | 0.166 | 0.166 | 0.77 | 0.70 | 1.17 | 0.39 | 5.08 | 5.08 | True | False | True |
| LTD GTX0405B | R | 100-320 | 6 | 6 | 9.64 | 9.64 | 0.90 | 0.90 | 0.094 | 0.094 | 0.75 | 0.69 | 5.76 | 4.87 | 15.42 | 15.42 | True | False | True |
| GTX0406B | R | 100-330 | 5 | 5 | 26.49 | 26.50 | 3.20 | 3.20 | 0.121 | 0.121 | 0.79 | 0.73 | 2.31 | 1.46 | 5.53 | 5.53 | True | False | True |
| LTD GTX0406B | R | 150-320 | 5 | 5 | 16.41 | 16.41 | 1.86 | 1.86 | 0.113 | 0.113 | 0.61 | 0.56 | 2.58 | 1.86 | 5.72 | 5.72 | True | False | True |
| GTX0407B | R | 100-330 | 5 | 5 | 30.15 | 30.16 | 3.37 | 3.37 | 0.112 | 0.112 | 0.67 | 0.63 | 2.23 | 1.21 | 7.04 | 7.04 | True | False | True |
| GTX0408B | R | 100-330 | 5 | 5 | 24.86 | 24.87 | 3.59 | 3.59 | 0.144 | 0.144 | 0.70 | 0.63 | 1.32 | 0.36 | 7.09 | 7.09 | True | False | True |
| GTX0503B_cc | A | 360-600 | 10 | 10 | 13.27 | 13.28 | 0.55 | 0.55 | 0.042 | 0.042 | 0.84 | 0.82 | 16.35 | 15.85 | 3.70 | 3.70 | True | False | True |
| GTX0505_c | C | 300-560 | 11 | 11 | 13.54 | 13.55 | 0.67 | 0.67 | 0.049 | 0.049 | 0.89 | 0.86 | 14.29 | 13.68 | 5.43 | 5.43 | True | False | True |
| LTD GTX0604B | B | 450-560 | 6 | 6 | 3.17 | 3.17 | 0.19 | 0.19 | 0.060 | 0.060 | 0.70 | 0.70 | 8.60 | 8.60 | 9.96 | 5.24 | True | True | False |
| GTX080101 | R | 420-600 | 9 | 9 | 58.80 | 58.51 | 1.86 | 1.86 | 0.032 | 0.032 | 0.62 | 0.62 | 15.70 | 15.69 | 4.49 | 4.49 | False | True | True |
| LTD GTX08031 | B | 20-280 | 6 | 6 | 36.38 | 36.38 | 2.66 | 2.66 | 0.073 | 0.073 | 0.66 | 0.68 | 6.82 | 7.05 | 2.55 | 2.55 | True | False | True |
| GTX1011 | R | 200-500 | 10 | 10 | 15.22 | 15.22 | 2.33 | 2.33 | 0.153 | 0.153 | 0.69 | 0.69 | 3.49 | 3.49 | 20.08 | 8.40 | True | True | False |
| LTD GTX1014 | B | 390-520 | 6 | 6 | 29.34 | 29.34 | 0.85 | 0.85 | 0.029 | 0.029 | 0.85 | 0.77 | 20.86 | 20.86 | 3.88 | 3.88 | True | False | True |
| OL0102A | R | 100-450 | 9 | 9 | 20.03 | 20.04 | 6.18 | 6.18 | 0.308 | 0.308 | 0.70 | 0.62 | 0.36 | -0.15 | 18.70 | 18.70 | True | False | True |
| OL0104A | R | 100-300 | 4 | 4 | 15.65 | 15.65 | 1.17 | 1.17 | 0.075 | 0.075 | 0.78 | 0.77 | 1.77 | 1.47 | 8.68 | 8.68 | True | False | True |
| LTD OL0404A | B | 20-520 | 14 | 14 | 29.41 | 29.42 | 1.34 | 1.34 | 0.046 | 0.046 | 0.90 | 0.93 | 17.88 | 18.66 | 3.94 | 3.94 | True | False | True |
| OL0409C | B | 300-600 | 13 | 13 | 44.76 | 44.76 | 1.62 | 1.62 | 0.036 | 0.036 | 0.92 | 0.91 | 22.00 | 21.84 | 8.38 | 4.72 | True | True | False |

103 of 105 determinations recalculate in N, B and β (51 of the 51 accepted); 86 also in f and q (46 of the accepted). The anchored MAD agrees for 102.

## Site paleointensities (Tables 2 and 4)

Mean and standard deviation of the published B of the accepted determinations of Table III (classes A to C), all together (`all`), without LTD (`std`) and with LTD (`ltd`), against Table 4 (`_pub`; the `all` columns are also those of Table 2). `N`: specimens in Table III and the files.

| site | n_all_pub | n_all | B_all_pub | B_all | dB_all_pub | dB_all | n_std_pub | n_std | B_std_pub | B_std | dB_std_pub | dB_std | n_ltd_pub | n_ltd | B_ltd_pub | B_ltd | dB_ltd_pub | dB_ltd | classes_pub | classes | N_pub | N |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTX01 | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0/0/0 | 0/0/0 | 7 | 7 |
| GTX02 | 6 | 6 | 27.6 | 27.61 | 4.5 | 4.50 | 3 | 3 | 27.8 | 27.77 | 2.8 | 2.78 | 3 | 3 | 27.4 | 27.44 | 6.5 | 6.54 | 1/2/3 | 1/2/3 | 10 | 10 |
| GTX03 | 4 | 4 | 37.9 | 37.85 | 4.7 | 4.71 | 2 | 2 | 41.4 | 41.36 | 4.0 | 4.02 | 2 | 2 | 34.3 | 34.34 | 1.1 | 1.07 | 1/1/2 | 1/1/2 | 10 | 10 |
| GTX04 | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0/0/0 | 0/0/0 | 6 | 6 |
| GTX05 | 8 | 8 | 10.8 | 10.78 | 2.6 | 2.65 | 5 | 5 | 11.6 | 11.59 | 2.3 | 2.29 | 3 | 3 | 9.4 | 9.43 | 3.1 | 3.11 | 1/2/5 | 1/2/5 | 9 | 9 |
| GTX06 | 3 | 3 | 3.5 | 3.51 | 0.9 | 0.94 | 1 | 1 | 4.6 | 4.58 |  |  | 2 | 2 | 3.0 | 2.98 | 0.3 | 0.27 | 0/3/0 | 0/3/0 | 10 | 10 |
| GTX07 | 2 | 2 | 9.4 | 9.40 | 2.4 | 2.40 | 1 | 1 | 11.1 | 11.10 |  |  | 1 | 1 | 7.7 | 7.70 |  |  | 0/1/1 | 0/1/1 | 8 | 8 |
| GTX08 | 4 | 4 | 32.0 | 32.00 | 3.2 | 3.23 | 1 | 1 | 31.2 | 31.18 |  |  | 3 | 3 | 32.3 | 32.28 | 3.9 | 3.90 | 1/2/1 | 1/2/1 | 8 | 8 |
| GTX09 | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0/0/0 | 0/0/0 | 8 | 8 |
| GTX10 | 3 | 3 | 30.8 | 30.82 | 1.3 | 1.28 | 0 | 0 |  |  |  |  | 3 | 3 | 30.8 | 30.82 | 1.3 | 1.28 | 0/2/1 | 0/2/1 | 10 | 10 |
| GTX11 | 7 | 7 | 28.7 | 28.74 | 3.2 | 3.19 | 5 | 5 | 28.3 | 28.26 | 3.1 | 3.08 | 2 | 2 | 29.9 | 29.91 | 4.4 | 4.41 | 2/3/2 | 2/3/2 | 8 | 8 |
| OL01 | 1 | 0 | 38.8 |  |  |  | 0 | 0 |  |  |  |  | 1 | 0 | 38.8 |  |  |  | 0/0/1 | 0/0/0 | 9 | 9 |
| OL02 | 8 | 8 | 16.1 | 16.14 | 4.7 | 4.73 | 5 | 5 | 18.0 | 17.96 | 4.7 | 4.67 | 3 | 3 | 13.1 | 13.10 | 3.5 | 3.53 | 5/3/0 | 5/3/0 | 9 | 9 |
| OL03 | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0 | 0 |  |  |  |  | 0/0/0 | 0/0/0 | 9 | 8 |
| OL04 | 6 | 6 | 39.7 | 39.73 | 5.4 | 5.36 | 4 | 4 | 42.0 | 42.04 | 2.2 | 2.21 | 2 | 2 | 35.1 | 35.12 | 8.1 | 8.07 | 1/4/1 | 1/4/1 | 8 | 8 |

VADMs (Table 3) from the published site paleointensity and the site latitude (`pmag.b_vdm`), in 10²² Am²; `sigma` is the VADM times ΔB/B:

| site | B | lat | vadm_pub | vadm | sigma_pub | sigma |
| --- | --- | --- | --- | --- | --- | --- |
| GTX03 | 37.9 | 42.1662 | 6.39 | 6.39 | 0.79 | 0.79 |
| OL04 | 39.7 | 42.1585 | 6.69 | 6.69 | 0.91 | 0.91 |
| GTX08 | 32.0 | 42.1597 | 5.40 | 5.40 | 0.54 | 0.54 |
| GTX02 | 27.6 | 42.1672 | 4.65 | 4.65 | 0.76 | 0.76 |
| GTX05 | 10.8 | 42.0772 | 1.82 | 1.82 | 0.44 | 0.44 |
| OL02 | 16.1 | 42.1444 | 2.72 | 2.72 | 0.79 | 0.79 |
| GTX06 | 3.5 | 42.1145 | 0.59 | 0.59 | 0.15 | 0.15 |
| GTX07 | 9.4 | 42.1574 | 1.59 | 1.59 | 0.40 | 0.40 |
| GTX11 | 28.7 | 42.1707 | 4.84 | 4.84 | 0.54 | 0.54 |
| GTX10 | 30.8 | 42.1956 | 5.19 | 5.19 | 0.22 | 0.22 |

## Rock-magnetic files

21 powders, each with four VFTB curves, converted with `convert_2_magic.vftb`: LP-HYS 21 curves, 1071 points; LP-IMT 21 curves, 4844 points; LP-IRM 21 curves, 315 points; LP-IRM-DCD 21 curves, 500 points. Each powder is entered with the suffix `r`, in the sample of its core. The paper gives no rock-magnetic values per sample (only the Day plot of Fig. 2C), so none is entered. For the record, and as a check of PmagPy on these curves:

| specimen | points | bcr | ms | ms_branch | mr | mr_branch | bc | bc_branch | mr_ms | bcr_bc |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTX0102infr | 41 | 27.9 | 1.471 | 1.517 | 0.046 | 0.343 | 3.2 | 14.3 | 0.226 | 1.94 |
| GTX0208B_MALr | 41 | 23.2 | 3.265 | 3.241 | 0.085 | 0.375 | 2.8 | 10.2 | 0.116 | 2.27 |
| GTX0208Br | 41 | 23.6 | 3.211 | 3.304 | 0.167 | 0.345 | 5.3 | 10.4 | 0.104 | 2.27 |
| GTX0307inf_MALr | 41 | 39.6 | 1.359 | 1.412 | 0.073 | 0.236 | 4.7 | 11.5 | 0.167 | 3.43 |
| GTX0307infr | 41 | 38.2 | 1.290 | 1.327 | 0.181 | 0.220 | 11.4 | 11.2 | 0.166 | 3.42 |
| GTX0403supr | 41 | 31.6 | 2.826 | 2.869 | 0.307 | 0.314 | 10.3 | 8.6 | 0.110 | 3.66 |
| GTX0507infr | 41 | 42.7 | 2.800 | 2.906 | 0.383 | 0.509 | 16.1 | 18.3 | 0.175 | 2.34 |
| GTX0605fragr | 41 | 38.7 | 1.632 | 1.616 | 0.265 | 0.283 | 17.7 | 14.1 | 0.175 | 2.75 |
| GTX0701infr | 41 | 32.6 | 1.695 | 1.716 | 0.342 | 0.377 | 17.8 | 14.7 | 0.219 | 2.22 |
| GTX080103infr | 41 | 38.2 | 1.099 | 1.133 | 0.131 | 0.306 | 9.4 | 16.6 | 0.270 | 2.30 |
| GTX0903infr | 41 | 17.5 | 1.351 | 1.404 | 0.252 | 0.275 | 14.9 | 11.3 | 0.196 | 1.55 |
| GTX100203infr | 41 | 26.6 | 0.615 | 0.636 | 0.008 | 0.120 | 1.2 | 10.9 | 0.189 | 2.44 |
| GTX1101r | 41 | 38.8 | 0.614 | 0.631 | 0.053 | 0.138 | 7.1 | 15.2 | 0.218 | 2.55 |
| OL0102Ar | 41 | 26.4 | 0.778 | 0.818 | 0.060 | 0.062 | 6.0 | 6.1 | 0.075 | 4.29 |
| OL0110Cr | 41 | 13.2 | 0.849 | 0.877 | 0.103 | 0.186 | 9.6 | 13.4 | 0.212 | 0.99 |
| OL0203Br | 41 | 37.1 | 3.914 | 4.052 | 0.239 | 0.154 | 8.5 | 6.0 | 0.038 | 6.16 |
| OL0206Ar | 41 | 36.4 | 3.085 | 3.167 | 0.417 | 0.418 | 15.0 | 14.2 | 0.132 | 2.56 |
| OL0308Ar | 41 | 24.1 | 1.636 | 1.679 | 0.297 | 0.354 | 15.1 | 14.4 | 0.211 | 1.68 |
| OL0309Br | 41 | 28.6 | 1.816 | 1.871 | 0.224 | 0.232 | 11.5 | 10.4 | 0.124 | 2.75 |
| OL0401Br | 41 | 49.0 | 0.340 | 0.347 | 0.089 | 0.089 | 26.2 | 25.1 | 0.255 | 1.96 |
| OL0406Br | 41 | 36.4 | 1.029 | 1.046 | 0.113 | 0.205 | 11.0 | 16.0 | 0.196 | 2.28 |

Moments in Am²/kg, fields in mT. `bcr`: zero crossing of the back-field curve (`rockmag.process_backfield_data`). `ms`, `mr`, `bc`: `rockmag.process_hyst_loop`, which leaves out the initial magnetization curve at the start of each file; `_branch`: read from the measured branches after removing the high-field slope above 60 percent of the peak field. `process_hyst_loop` gives Mr -94 to 55 percent and Bc -89 to 41 percent from the branch values, and Ms -4.8 to 0.9 percent: the loops have 41 points each, unevenly spaced (about 50 mT apart near zero field), and the function resamples a loop on an even grid of its median field step, which does not resolve the loop near zero field. `mr_ms` and `bcr_bc` are from the branch values.

## Thermal stability (Table IV)

46 magnetization-temperature cycles, converted with `convert_2_magic.vftb`, for the rows of Table IV. The field of a cycle (`field_mT`, the median of its file) is 33.3 to 37.4 mT for 35 files (the text gives 38 mT); the other 11 (GTX309B_500, GTX309B_600, GTX501B_500, GTX501B_600, GTX5-5_500, GTX5-5_560, GTX5-5_600, GTX803_250, GTX803_300, OLO106_250, OLO106_300) give -999 in the field column, the missing value of the VFTB software, and their field is left empty.

MAGF/MAGI is recalculated as the magnetization at the end of the cooling branch over that of the heating branch at the measured temperature nearest to that of the end of cooling (`ratio`); MAG2F/MAG1I the same with the end of the second cycle and the heating branch of the first. `agrees`: `ratio` within 0.005. Two other ratios for comparison: `ratio_interpolated`, with the heating branch interpolated linearly to the temperature of the end of cooling, and `ratio_start`, over the first measurement of the heating branch.

| row | kind | file | specimen | weight_mg | field_mT | T_pub | T | ratio_pub | ratio | ratio_interpolated | ratio_start | agrees |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTX0206 | MAGF/MAGI | GTX206_540 | GTX0206s | 347 | 34.2 | 540 | 539 | 1.081 | 1.081 | 1.081 | 1.047 | yes |
| GTX0208 | MAGF/MAGI | GTX0208B | GTX0208s | 294 | 35.7 | 500 | 499 | 1.023 | 1.023 | 1.021 | 1.002 | yes |
| GTX0308 | MAGF/MAGI | GTX0308B_500 | GTX0308s | 433 | 35.2 | 500 | 499 | 0.944 | 0.941 | 0.942 | 0.920 | yes |
| GTX0308 | MAGF/MAGI | GTX308B_570 | GTX0308s | 433 | 34.8 | 570 | 569 | 1.054 | 1.054 | 1.054 | 0.989 | yes |
| GTX0308 | MAG2F/MAG1I | GTX308B_570 / GTX0308B_500 | GTX0308s |  |  |  |  | 0.974 | 0.974 | 0.973 | 0.938 | yes |
| GTX0309 | MAGF/MAGI | GTX309B_500 | GTX0309s | 398 |  | 500 | 500 | 0.963 | 0.963 | 0.963 | 0.940 | yes |
| GTX0309 | MAGF/MAGI | GTX309B_600 | GTX0309s | 398 |  | 600 | 599 | 1.034 | 1.034 | 1.033 | 1.002 | yes |
| GTX0309 | MAG2F/MAG1I | GTX309B_600 / GTX309B_500 | GTX0309s |  |  |  |  | 0.964 | 0.964 | 0.964 | 0.941 | yes |
| GTX0501 | MAGF/MAGI | GTX501B_500 | GTX0501s | 244 |  | 500 | 499 | 0.966 | 0.990 | 0.990 | 0.966 | no |
| GTX0501 | MAGF/MAGI | GTX501B_600 | GTX0501s | 244 |  | 600 | 598 | 1.035 | 1.045 | 1.042 | 1.009 | no |
| GTX0501 | MAG2F/MAG1I | GTX501B_600 / GTX501B_500 | GTX0501s |  |  |  |  | 1.015 | 1.015 | 1.017 | 0.983 | yes |
| GTX0503 | MAGF/MAGI | GTX503B_500 | GTX0503s | 303 | 35.6 | 500 | 499 | 0.985 | 0.985 | 0.985 | 0.957 | yes |
| GTX0503 | MAGF/MAGI | GTX503B_600 | GTX0503s | 303 | 35.6 | 600 | 598 | 1.076 | 1.076 | 1.075 | 1.037 | yes |
| GTX0503 | MAG2F/MAG1I | GTX503B_600 / GTX503B_500 | GTX0503s |  |  |  |  | 1.045 | 1.040 | 1.041 | 1.010 | no |
| GTX0504 | MAGF/MAGI | GTX504B_560 | GTX0504s | 438 | 34.6 | 560 | 559 | 1.004 | 1.004 | 1.004 | 0.971 | yes |
| GTX0505 | MAGF/MAGI | GTX5-5_500 | GTX0505s | 449 |  | 500 | 499 | 1.051 | 0.983 | 0.985 | 0.960 | no |
| GTX0505 | MAGF/MAGI | GTX5-5_560 | GTX0505s2 | 389 |  | 560 | 559 | 0.998 | 0.998 | 1.000 | 0.971 | yes |
| GTX0505 | MAGF/MAGI | GTX5-5_600 | GTX0505s | 449 |  | 600 | 598 | 0.983 | 1.051 | 1.051 | 1.022 | no |
| GTX0505 | MAG2F/MAG1I | GTX5-5_600 / GTX5-5_500 | GTX0505s |  |  |  |  | 1.003 | 1.027 | 1.028 | 1.003 | no |
| GTX0506 | MAGF/MAGI | GTX506B_550 | GTX0506s | 412 | 35.4 | 550 | 547 | 1.005 | 1.005 | 1.005 | 0.980 | yes |
| GTX0604 | MAGF/MAGI | GTX604B_560 | GTX0604s | 468 | 35.3 | 560 | 559 | 1.053 | 1.053 | 1.051 | 1.028 | yes |
| GTX0604 | MAGF/MAGI | GTX604_560 | GTX0604s | 468 | 35.3 | 560 | 559 | 1.053 | 1.053 | 1.051 | 1.028 | yes |
| GTX0605 | MAGF/MAGI | GTX0605A_560 | GTX0605s | 450 | 35.4 | 560 | 559 | 1.018 | 1.018 | 1.019 | 0.997 | yes |
| GTX0705 | MAGF/MAGI | OLO705B_560 | GTX0705s | 358 | 35.5 | 560 | 559 | 1.028 | 1.029 | 1.026 | 0.945 | yes |
| GTX0802 | MAGF/MAGI | GTX0802_500 | GTX0802s | 358 | 35.5 | 500 | 499 | 1.033 | 1.033 | 1.033 | 1.011 | yes |
| GTX0803 | MAGF/MAGI | GTX803_250 | GTX0803s | 415 |  | 250 | 251 | 1.008 | 1.008 | 1.015 | 0.988 | yes |
| GTX0803 | MAGF/MAGI | GTX803_300 | GTX0803s | 415 |  | 300 | 300 | 1.021 | 1.021 | 1.025 | 0.982 | yes |
| GTX0803 | MAG2F/MAG1I | GTX803_300 / GTX803_250 | GTX0803s |  |  |  |  | 1.010 | 1.010 | 1.017 | 0.990 | yes |
| GTX1001 | MAGF/MAGI | GTX10-1_450 | GTX1001s | 333 | 34.8 | 450 | 449 | 1.053 | 1.053 | 1.053 | 0.947 | yes |
| GTX1001 | MAGF/MAGI | GTX10-1_520 | GTX1001s | 333 | 34.7 | 520 | 519 | 1.153 | 1.161 | 1.153 | 1.005 | no |
| GTX1001 | MAG2F/MAG1I | GTX10-1_520 / GTX10-1_450 | GTX1001s |  |  |  |  | 1.140 | 1.140 | 1.140 | 1.026 | yes |
| GTX1003 | MAGF/MAGI | GTX1003_500 | GTX1003s | 398 | 37.2 | 500 | 499 | 1.613 | 1.613 | 1.660 | 0.837 | yes |
| GTX1101 | MAGF/MAGI | GTX1101_500 | GTX1101s | 383 | 34.1 | 500 | 499 | 1.039 | 1.039 | 1.038 | 1.009 | yes |
| GTX1101 | MAGF/MAGI | GTX1101_600 | GTX1101s | 383 | 35.3 | 600 | 598 | 0.976 | 0.976 | 0.976 | 0.947 | yes |
| GTX1101 | MAG2F/MAG1I | GTX1101_600 / GTX1101_500 | GTX1101s |  |  |  |  | 1.015 | 1.015 | 1.014 | 0.986 | yes |
| GTX1102 | MAGF/MAGI | GTX1102_500 | GTX1102s | 429 | 34.6 | 500 | 499 | 0.955 | 0.955 | 0.958 | 0.934 | yes |
| GTX1102 | MAGF/MAGI | GTX1102_600 | GTX1102s2 | 406 | 35.3 | 600 | 598 | 0.845 | 0.845 | 0.846 | 0.825 | yes |
| GTX1103 | MAGF/MAGI | GTX1103_560 | GTX1103s | 479 | 33.6 | 560 | 559 | 0.991 | 0.993 | 0.993 | 0.993 | yes |
| OLO106 | MAGF/MAGI | OLO106_250 | OL0106s | 122 |  | 250 | 251 |  | 1.448 | 1.404 | 0.860 |  |
| OLO106 | MAGF/MAGI | OLO106_300 | OL0106s2 | 354 |  | 300 | 300 |  | 1.215 | 1.215 | 0.780 |  |
| OLO201 | MAGF/MAGI | OLO201A_520 | OL0201s | 377 | 33.9 | 520 | 518 | 1.037 | 1.037 | 1.038 | 1.018 | yes |
| OLO203 | MAGF/MAGI | OLO203B_540 | OL0203s | 524 | 35.7 | 540 | 539 | 0.980 | 0.980 | 0.980 | 0.965 | yes |
| OLO204 | MAGF/MAGI | OLO204C_560 | OL0204s | 433 | 35.4 | 560 | 559 | 0.987 | 0.987 | 0.988 | 0.970 | yes |
| OLO209 | MAGF/MAGI | OLO209C_540 | OL0209s | 313 | 36.3 | 540 | 540 | 1.023 | 1.023 | 1.023 | 1.001 | yes |
| OLO210 | MAGF/MAGI | OLO210B_500 | OL0210s | 431 | 34.8 | 500 | 499 | 0.977 | 0.977 | 0.977 | 0.961 | yes |
| OLO210 | MAGF/MAGI | OLO210B_600 | OL0210s | 431 | 33.9 | 600 | 598 | 0.977 | 0.977 | 0.977 | 0.962 | yes |
| OLO210 | MAG2F/MAG1I | OLO210B_600 / OLO210B_500 | OL0210s |  |  |  |  | 0.942 | 0.942 | 0.943 | 0.927 | yes |
| OLO404 | MAGF/MAGI | OLO404A_450 | OL0404s | 142 | 33.3 | 450 | 449 | 0.978 | 0.978 | 0.979 | 0.945 | yes |
| OLO404 | MAGF/MAGI | OLO404A_520 | OL0404s2 | 380 | 35.3 | 520 | 519 | 0.994 | 0.994 | 0.994 | 0.974 | yes |
| OLO407 | MAGF/MAGI | OLO407A_450 | OL0407s | 406 | 33.7 | 450 | 449 | 1.047 | 1.072 | 1.073 | 1.047 | no |
| OLO407 | MAGF/MAGI | OLO407A_500 | OL0407s2 | 407 | 35.5 | 500 | 499 | 1.176 | 1.179 | 1.180 | 1.145 | yes |
| OLO409 | MAGF/MAGI | OLO409C_500 | OL0409s | 448 | 35.4 | 500 | 498 | 1.067 | 1.066 | 1.065 | 1.045 | yes |
| OLO409 | MAGF/MAGI | OLO409C_600 | OL0409s | 448 | 34.7 | 600 | 599 | 1.022 | 1.022 | 1.024 | 1.008 | yes |
| OLO409 | MAG2F/MAG1I | OLO409C_600 / OLO409C_500 | OL0409s |  |  |  |  | 1.046 | 1.050 | 1.049 | 1.029 | yes |
| OLO410 | MAGF/MAGI | OLO410B_500 | OL0410s | 213 | 37.4 | 500 | 499 | 1.064 | 1.064 | 1.065 | 1.039 | yes |
| OLO410 | MAGF/MAGI | OLO410B_600 | OL0410s | 213 | 37.0 | 600 | 598 | 1.030 | 1.030 | 1.029 | 1.003 | yes |
| OLO410 | MAG2F/MAG1I | OLO410B_600 / OLO410B_500 | OL0410s |  |  |  |  | 1.072 | 1.072 | 1.074 | 1.047 | yes |

47 of 55 printed ratios recalculate within 0.005. To the printed digit, `ratio` gives 41 of them, `ratio_interpolated` 17 and `ratio_start` 3. Of those that `ratio` does not give, `ratio_start` gives GTX0501 at 500 °C (0.966), GTX0505 MAG2F/MAG1I (1.003), OLO407 at 450 °C (1.047). For GTX0505 the cycle to 500 °C gives the ratio printed for T3 (600 °C) and the cycle to 600 °C the one printed for T1 (500 °C). Table IV prints no ratio for OLO106.


## Information that would complete the contribution

Not needed for any result entered, and not asked of the authors (README.md, "Questions for the authors"):

- The volumes of the Thellier-Coe microcores, which would give their moments (`magn_moment`) as well.
- The rock-magnetic parameters of each powder, which the paper plots (Fig. 2C) but does not list.
