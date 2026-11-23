# Praia Grande: build report

Written by `convert.py`; do not edit. Study: Calvo Rathert et al. (2022), doi:10.1093/gji/ggac173; data doi:10.5281/zenodo.5553392. `README.md` explains the sources and the decisions.

## Contents of the contribution

| Table | Rows | Source |
| --- | --- | --- |
| measurements | 9291: 1186 demagnetization steps (`.rs3`), 1750 Thellier-Coe steps (`.tdt`), 385 multispecimen steps (`.jr6`), 5970 rock-magnetic points (VFTB) | files |
| specimens | 359 rows for 242 specimens: 88 demagnetized (174 rows of stored fits in specimen and geographic coordinates, 2 rows of a fit recalculated here), 66 Thellier (22 with a determination), 77 multispecimen, 11 rock-magnetic (24 rows of Curie temperatures) | files; table (Tables 2 and S1); inferred (use in the flow means) |
| samples | 92: 79 cores with a demagnetization file, 2 cores without, 11 multispecimen samples | files (orientation); text (method) |
| sites | 20: 11 flow directions, 9 flow paleointensities | table (Tables 1 to 3); text (age, lithology); figure (position) |
| locations | 1 | table (Tables 1 and 3); text; figure |
| ages | 2 | text |
| criteria | 10 | table (Tables 2 and 3) |

## Validation with the rules of MagIC (`pmagpy.magic_validation`)

No problems.

## Uploading to MagIC

`magic_contribution.txt` holds every table except the contribution table, which is made on MagIC when the file is uploaded (the file is written with `ipmag.upload_magic`). Enter there:

- Reference: 10.1093/gji/ggac173
- Laboratories: Paleomagnetic and Rock Magnetic Laboratory (Universidad de Burgos, Spain); Interinstitutional Laboratory of Natural Magnetism (UNAM Morelia, Mexico)
- Description: Converted from the laboratory files archived by the authors (https://doi.org/10.5281/zenodo.5553392) and from the paper and its supporting information. Sources, choices and checks are documented at <permalink>.

`<permalink>` is the link to this study folder at the commit the upload is made from, so that it keeps pointing to the files that made the contribution. After committing and pushing, `python common/studies.py --permalink calvo-rathert_2022_praia_grande` prints it; enter that commit as `upload_commit` in `study.json`.

## Directions

The demagnetization files hold 87 stored line fits. Re-made from the measurements between their stated limits, with the line type the file flags (OA = anchored), 86 agree with the stored direction within 0.15° (largest MAD difference 0.07°).

Flow means recalculated from the contribution: Fisher mean of the characteristic fits flagged good, at the level given, against Table 1. `vgp_diff` is the angle between the published VGP and the VGP of the published mean direction at 16.864°N, 335.107°E.

| site | level | N_pub | N | dec | inc | k | a95 | dec_pub | inc_pub | k_pub | a95_pub | angle | reproduced | left_out | vgp_diff |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRG1 | specimens | 6 | 6 | 330.6 | 28.4 | 872 | 2.3 | 330.6 | 28.4 | 872 | 2.3 | 0.05 | yes | PRG1-6B | 0.01 |
| PRG2 | specimens | 8 | 8 | 328.2 | 33.3 | 48 | 8.1 | 328.2 | 33.3 | 48 | 8.1 | 0.03 | yes |  | 0.02 |
| PRG3 | specimens | 8 | 8 | 329.7 | 26.4 | 260 | 3.4 | 329.7 | 26.4 | 260 | 3.4 | 0.02 | yes |  | 0.03 |
| PRG4 | specimens | 7 | 7 | 332.8 | 27.4 | 122 | 5.5 | 332.8 | 27.4 | 122 | 5.5 | 0.03 | yes | PRG4-8 | 0.04 |
| PRG5 | specimens | 7 | 7 | 335.1 | 29.6 | 127 | 5.4 | 335.1 | 29.6 | 127 | 5.4 | 0.06 | yes |  | 1.09 |
| PRG6 | samples | 8 | 8 | 332.7 | 28.6 | 270 | 3.4 | 332.7 | 28.7 | 269 | 3.4 | 0.06 | yes |  | 0.05 |
| PRG7 | samples | 8 | 8 | 332.2 | 33.1 | 198 | 3.9 | 332.2 | 33.1 | 199 | 3.9 | 0.04 | yes |  | 0.03 |
| PRG8 | samples | 7 | 7 | 335.4 | 31.5 | 111 | 5.8 | 335.4 | 31.5 | 111 | 5.8 | 0.05 | yes |  | 0.02 |
| PRG9 | specimens | 6 | 6 | 334.4 | 29.6 | 132 | 5.8 | 334.4 | 29.6 | 132 | 5.8 | 0.05 | yes | PRG9-4, PRG9-4A | 0.04 |
| PRG10 | specimens | 8 | 8 | 333.2 | 26.9 | 307 | 3.2 | 333.2 | 26.9 | 307 | 3.2 | 0.02 | yes | PRG10-1A | 0.04 |
| PRG11 | specimens | 2 | 2 | 329.0 | 31.9 | 2467 | 5.0 | 329.0 | 31.9 | 2467 | 5.0 | 0.04 | yes |  | 0.02 |

Sequence-mean VGP: published 63.3°N, 247.0°E; the Fisher mean of the 11 published VGPs is 0.03° from it and the VGP of the mean direction 0.09°, so the pole is coded DE-VGP.

- PRG6-2A CA: the stored fit is 0.84° from a fit between its stated limits (2mT to 90mT) and is recalculated with T 480 to 90mT (16 steps). dir_n_measurements and meas_step_min were set accordingly.
- PRG5: the stored fits give 337.0/28.1 (k 364), 2.2° from the published mean. It is reproduced when the free line stored for PRG5-4B (300°C to 580°C, 337.1/27.5, MAD 27.6°) is recalculated over the same steps as an anchored line (322.4/37.6, MAD 13.3°). The stored row is flagged b and the recalculated fit is entered as a new row.
- PRG5: the published VGP (66.1°N, 243.6°E) is 1.09° from the VGP calculated from the published direction (66.1°N, 246.3°E); for the other flows the two agree within 0.05°. The published values are entered as printed.

## Thellier-Coe files

The archive holds 82 `.tdt` files. 66 carry ThellierTool step codes (T.00 zero field, T.11 in field, T.12 pTRM check) and are the 66 specimens of the paper. The other 16 carry the steps as labeled at measurement (125C, 126C, ...) and specimen names that count up row by row. Each matches one of the 66 on its measured directions: 15 with identical moments, PRG1-12 with the moments of PRG1-8 multiplied by 3.33. 7 of them hold one or two rows that the coded file does not. They are not converted.

| file | name_column | rows | same data as | same_directions | moment_ratio | rows_not_in_coded |
| --- | --- | --- | --- | --- | --- | --- |
| PRG1-12 | PRG1-12 to 29 | 29 | PRG1-8 | 27 of 29 | 0.30 | NRM 0.00225 287.5/34.5; 513C 0.00158 295.2/-71.3 |
| PRG10-11 | PRG10-11 to PRG10-37 | 27 | PRG10-7 | 27 of 27 | 1.00 |  |
| PRG10-5 | PRG10-5 to PRG10-31 | 27 | PRG10-1 | 27 of 27 | 1.00 |  |
| PRG2--7B | PRG2--7B to PRG2--7B | 27 | PRG2-7B | 26 of 27 | 1.00 | 226C 0.000365 137.5/-32.3 |
| PRG3-12 | PRG3-12 to PRG3-38 | 27 | PRG3-8 | 27 of 27 | 1.00 |  |
| PRG3-7 | PRG3-7 to PRG3-33 | 27 | PRG3-3 | 27 of 27 | 1.00 |  |
| PRG4-10 | PRG4-10 to 28 | 28 | PRG4-6 | 27 of 28 | 1.00 | 539C 0.00227 120.1/-86.3 |
| PRG4-12 | PRG4-12 to 28 | 28 | PRG4-8 | 27 of 28 | 1.00 | 538C 0.000664 57.8/-63.3 |
| PRG5-5 | PRG5-5 to PRG5-31 | 27 | PRG5-1 | 26 of 27 | 1.00 | 539C 0.00464 317.7/-87.1 |
| PRG6-11 | PRG6-11 to PRG6-37 | 27 | PRG6-7 | 27 of 27 | 1.00 |  |
| PRG7-9 | PRG7-9 to PRG7-35 | 27 | PRG7-5 | 27 of 27 | 1.00 |  |
| PRG8-11 | PRG8-11 to PRG8-37 | 27 | PRG8-7A | 27 of 27 | 1.00 |  |
| PRG8-5 | PRG8-5 to 28 | 28 | PRG8-1 | 27 of 28 | 1.00 | 442C 0.00124 40.3/-84.7 |
| PRG8-7 | PRG8-7 to PRG8-33 | 27 | PRG8-3 | 27 of 27 | 1.00 |  |
| PRG9-12 | PRG9-12 to PRG9-38 | 27 | PRG9-8 | 27 of 27 | 1.00 |  |
| PRG9-9 | PRG9-9 to 28 | 28 | PRG9-5 | 27 of 28 | 1.00 | 586C 2.03e-07 295.9/-81.4 |

In the 66 converted files:

- PRG1-3Ac.tdt holds specimen PRG1-3A.
- PRG1-8.tdt: in-field step 566.11 follows the zero-field step at 565 °C and is entered as 565.11.
- PRG11-2Ac.tdt holds specimen PRG11-2A.
- PRG2-4A.tdt: specimen written PRG2--4A in the file, entered as PRG2-4A.
- PRG2-7B.tdt: specimen written PRG2--7B in the file, entered as PRG2-7B.
- PRG4-5Ac.tdt holds specimen PRG4-5A.
- PRG4-8.tdt: several names in the specimen column (PRG4-8 (26 rows), PRG4-13 (1 rows)); PRG4-8 is used.
- PRG7-7Ac.tdt holds specimen PRG7-7A.
- PRG7-8Bc.tdt holds specimen PRG7-8B.
- The Thellier specimens are fragments in 10 mm vials, distinct from the demagnetized specimens, but 31 of them were published under the name of a demagnetized specimen of the same core (PRG1-2A, PRG1-3A, PRG1-5A, PRG10-1, PRG10-2A, PRG10-5A, PRG10-7, PRG11-1A, PRG11-2A, PRG2-4A, PRG3-1A, PRG3-7C, PRG4-2A, PRG4-8, PRG5-2A, PRG5-4B, PRG5-5A, PRG6-1A, PRG6-2A, PRG6-5C, PRG6-6A, PRG6-7, PRG7-2A, PRG7-3A, PRG7-5, PRG8-5A, PRG8-7A, PRG9-1A, PRG9-2A, PRG9-5, PRG9-6A). Every Thellier specimen is entered with the suffix `t` (PRG1-2A becomes PRG1-2At), and its description gives the published name.
- The specimen directions are in the coordinates of the unoriented fragment.

Published determinations recalculated: best-fit line on the Arai plot (Coe et al., 1978) over the published range, from the converted measurements, against Table 2. d(CK), k', MAD and α are entered as published and are not recalculated.

| specimen | range | N_pub | N | B_pub | B | B_sigma_pub | B_sigma | beta_pub | beta | f_pub | f | q_pub | q | agrees |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRG1-1A | 20-512 | 7 | 7 | 19.5 | 19.58 | 0.8 | 0.80 | 0.047 | 0.041 | 0.74 | 0.74 | 14.4 | 14.4 | yes, except sigma/slope |
| PRG1-2A | 20-484 | 6 | 6 | 17.4 | 17.33 | 0.7 | 0.73 | 0.042 | 0.042 | 0.62 | 0.62 | 10.5 | 10.5 | yes |
| PRG1-3A | 20-512 | 7 | 7 | 18.2 | 18.22 | 0.6 | 0.55 | 0.030 | 0.030 | 0.64 | 0.63 | 15.9 | 15.9 | yes |
| PRG1-5A | 328-512 | 5 | 5 | 18.1 | 18.00 | 0.7 | 0.64 | 0.036 | 0.036 | 0.60 | 0.60 | 12.3 | 12.3 | yes |
| PRG1-7A | 226-512 | 6 | 6 | 17.7 | 17.71 | 0.1 | 0.15 | 0.001 | 0.009 | 0.74 | 0.74 | 65.0 | 65.0 | yes, except sigma/slope |
| PRG1-8 | 226-584 | 9 | 9 | 17.2 | 17.20 | 0.3 | 0.35 | 0.020 | 0.020 | 0.84 | 0.84 | 35.1 | 34.1 | yes |
| PRG2-4A | 20-512 | 7 | 7 | 17.7 | 17.71 | 0.5 | 0.43 | 0.024 | 0.024 | 0.55 | 0.55 | 17.3 | 17.3 | yes |
| PRG3-1A | 20-512 | 7 | 7 | 22.5 | 22.52 | 0.8 | 0.75 | 0.033 | 0.033 | 0.48 | 0.48 | 12.1 | 12.1 | yes |
| PRG3-2A | 20-565 | 9 | 9 | 19.1 | 19.08 | 1.0 | 1.00 | 0.052 | 0.052 | 0.64 | 0.64 | 10.4 | 10.4 | yes |
| PRG3-3 | 20-537 | 8 | 8 | 25.3 | 25.28 | 0.9 | 0.93 | 0.037 | 0.037 | 0.52 | 0.52 | 12.0 | 12.0 | yes |
| PRG3-4 | 20-537 | 8 | 8 | 19.3 | 19.32 | 0.9 | 0.90 | 0.046 | 0.046 | 0.59 | 0.59 | 10.7 | 10.7 | yes |
| PRG3-6A | 20-512 | 7 | 7 | 17.0 | 17.04 | 0.8 | 0.76 | 0.045 | 0.045 | 0.41 | 0.43 | 7.8 | 7.8 | yes |
| PRG3-7C | 20-512 | 7 | 7 | 23.2 | 23.23 | 1.3 | 1.28 | 0.055 | 0.055 | 0.48 | 0.48 | 7.3 | 7.3 | yes |
| PRG3-8 | 20-512 | 7 | 7 | 19.1 | 19.12 | 1.3 | 1.24 | 0.065 | 0.065 | 0.55 | 0.55 | 6.9 | 6.9 | yes |
| PRG4-2A | 328-537 | 6 | 6 | 19.2 | 19.20 | 1.3 | 1.28 | 0.067 | 0.067 | 0.55 | 0.55 | 6.4 | 6.4 | yes |
| PRG4-3B | 20-512 | 7 | 7 | 21.4 | 21.32 | 1.5 | 1.45 | 0.068 | 0.068 | 0.40 | 0.40 | 4.8 | 4.8 | yes |
| PRG4-4 | 328-512 | 5 | 5 | 18.7 | 18.73 | 1.4 | 1.45 | 0.077 | 0.077 | 0.45 | 0.45 | 4.2 | 4.2 | yes |
| PRG4-5A | 20-512 | 6 | 6 | 19.9 | 19.85 | 1.4 | 1.42 | 0.071 | 0.071 | 0.54 | 0.54 | 5.9 | 5.9 | yes |
| PRG4-6 | 20-537 | 8 | 8 | 19.3 | 19.26 | 1.0 | 1.01 | 0.053 | 0.053 | 0.60 | 0.60 | 9.4 | 9.4 | yes |
| PRG4-8 | 20-512 | 7 | 7 | 25.6 | 25.66 | 2.4 | 2.40 | 0.093 | 0.093 | 0.50 | 0.50 | 4.3 | 4.3 | yes |
| PRG9-6A | 328-512 | 5 | 5 | 12.0 | 12.03 | 0.6 | 0.60 | 0.091 | 0.050 | 0.62 | 0.61 | 8.9 | 8.9 | yes, except sigma/slope |
| PRG11-2A | 389-565 | 6 | 6 | 10.0 | 9.99 | 0.8 | 0.84 | 0.084 | 0.084 | 0.84 | 0.84 | 6.8 | 6.8 | yes |

22 of 22 determinations recalculate in N, B, its standard error, f and q. For PRG1-1A, PRG1-7A, PRG9-6A the recalculated σ/slope is the value that follows from the published B, standard error and q. A published range that starts at 20 °C is reproduced only when the unheated point is left out of the fit, so N counts heating steps.

## Multispecimen files

Five JR6 files (M0 to M4), one per step of the protocol, each with 77 rows: seven sub-specimens per flow, in fields of 10 to 70 μT. The paper speaks of eight sub-specimens per sample (88 in total). The step label of a row is the field (A10 = 10 μT); a JR6 reader takes it for an alternating field in mT, so the rows are read directly here.

- M1.jr6: the row named PRG6-6 with field label A60 is entered as PRG7-6 (it stands where the other blocks of the file have flow PRG7).
- M2.jr6: the row named PRG8-2 with field label A20 is entered as PRG9-2 (it stands where the other blocks of the file have flow PRG9).
- M3.jr6: the row named PRG6-2 with field label A60 is entered as PRG6-6.
- M4.jr6: the row named PRG1-1 with field label A20 is entered as PRG1-2.
- The sub-specimens are named like cores (PRG1-1 is sub-specimen 1 of flow PRG1, not core 1). They are entered with the suffix `m`, in a sample `<flow>-MS`.
- The heating temperature (400 or 450 °C) is not given per flow, so `treat_temp` is empty and the description says so. The moments are in A/m of pellet (`magn_volume`).

Standard determinations of Table S3 (MSP-DB) recalculated: (m1 − m0)/m0 from the moduli, regressed on the field, zero crossing in μT; `alteration` is the mean of (m4 − m1)/m1 in percent. Where Table S3 rejects sub-specimens, the N that come closest to its value are used and `left_out` names the others.

| site | N_pub | B_pub | B | r2_pub | r2 | alteration_pub | alteration | left_out | agrees |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRG1 | 7 | 18.8 | 18.8 | 0.990 | 0.990 | -0.9 | -0.9 |  | yes |
| PRG2 | 5 | 15.1 | 15.1 | 0.979 | 0.979 | -21.5 | -21.5 | PRG2-3, PRG2-6 | yes |
| PRG3 | 7 | 19.3 | 19.3 | 0.938 | 0.938 | -1.1 | -1.1 |  | yes |
| PRG4 | 7 | 20.7 | 20.7 | 0.906 | 0.906 | -4.4 | -4.4 |  | yes |
| PRG5 | 6 | 20.2 | 20.2 | 0.945 | 0.945 | -14.5 | -14.5 | PRG5-2 | yes |
| PRG6 | 7 | 7.3 | 7.3 | 0.809 | 0.809 | -17.6 | -17.6 |  | yes |
| PRG7 | 7 | 13.6 | 14.3 | 0.910 | 0.938 | -6.2 | -5.8 |  | no |
| PRG9 | 6 | 13.7 | 13.7 | 0.802 | 0.802 | -20.3 | -20.3 | PRG9-1 | yes |
| PRG10 | 7 | 17.8 | 17.8 | 0.931 | 0.931 | -10.7 | -10.7 |  | yes |
| PRG11 | 7 | 18.9 | 18.9 | 0.943 | 0.943 | -6.0 | -5.4 |  | yes |

9 of 10 agree in B (0.15 μT), R² (0.002) and alteration (0.7 percent).

Determinations selected by the authors (Table 2) against a plain calculation of the selected protocol (`db` as above; `fc`: 2(m1 − m0)/(2m0 − m1 − m2) along the NRM), with all seven sub-specimens (`B_all`) and with the N that come closest to the published value (`B_closest`). This is not the authors' calculation (no alignment correction, no bootstrap bounds), and the published values are what is entered. `established` says whether the rejected sub-specimens (`left_out`) are identified: by this calculation reproducing B, R² and alteration, or by the standard determination of Table S3 with the same number rejected.

| site | type | ratio | N_pub | B_pub | B_all | B_closest | r2_pub | r2_closest | alteration_pub | alteration | left_out | established |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRG1 | FCc | fc | 6 | 18.7 | 19.9 | 18.9 | 0.972 | 0.974 | -0.9 | -0.9 | PRG1-7 | this calculation |
| PRG2 | DBc | db | 5 | 15.1 | 8.0 | 15.1 | 0.977 | 0.979 | -17.5 | -21.5 | PRG2-3, PRG2-6 | standard determination (Table S3) |
| PRG3 | FCc | fc | 6 | 19.1 | 19.2 | 19.3 | 0.975 | 0.975 | -2.6 | -2.6 | PRG3-6 | this calculation |
| PRG4 | FCc | fc | 6 | 18.3 | 22.0 | 18.6 | 0.920 | 0.918 | -4.5 | -4.8 | PRG4-7 | this calculation |
| PRG5 | DBc | db | 6 | 20.1 | 14.5 | 20.2 | 0.944 | 0.945 | -14.2 | -14.5 | PRG5-2 | this calculation |
| PRG7 | DBc | db | 6 | 15.5 | 14.3 | 15.6 | 0.961 | 0.961 | -5.0 | -5.4 | PRG7-4 | this calculation |
| PRG10 | DBc | db | 7 | 17.7 | 17.8 | 17.8 | 0.930 | 0.931 | -10.1 | -10.7 |  | this calculation |
| PRG11 | DB | db | 7 | 18.9 | 18.9 | 18.9 | 0.943 | 0.943 | -6.0 | -5.4 |  | this calculation |

Table 2 against the rows of Table S3 for the same protocols: PRG7 DBc: B_min 7.9 in Table 2, 7.3 in Table S3; PRG7 DBc: B_max 18.5 in Table 2, 18.4 in Table S3.

## Flow and sequence paleointensities (Table 3)

Every Thellier-Coe and combined row of Table 3 against the mean and standard deviation of the Table 2 values (a multispecimen result counts as one value):

| site | treatment | N_pub | N | B_pub | B | sigma_pub | sigma | percent_pub | percent |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRG1 | Coe | 6 | 6 | 18.0 | 18.02 | 0.8 | 0.82 | 4.4 | 4.6 |
| PRG1 | Coe + MS | 7 | 7 | 18.1 | 18.11 | 0.4 | 0.79 | 3.9 | 4.4 |
| PRG2 | Coe + MS | 2 | 2 | 16.4 | 16.40 | 1.8 | 1.84 | 11.0 | 11.2 |
| PRG3 | Coe | 7 | 7 | 20.8 | 20.79 | 2.9 | 2.93 | 13.9 | 14.1 |
| PRG3 | Coe + MS | 8 | 8 | 20.6 | 20.58 | 2.8 | 2.77 | 13.6 | 13.5 |
| PRG4 | Coe | 6 | 6 | 20.7 | 20.68 | 2.6 | 2.58 | 12.6 | 12.5 |
| PRG4 | Coe + MS | 7 | 7 | 20.3 | 20.34 | 2.5 | 2.52 | 12.3 | 12.4 |
| PRG9 | Coe | 1 | 1 | 12.0 | 12.00 | 0.6 | 0.60 | 5.0 | 5.0 |
| PRG11 | Coe | 1 | 1 | 10.0 | 10.00 | 0.8 | 0.80 | 8.0 | 8.0 |

For a single determination `sigma` is its standard error. Sequence means against the flow values entered, and the VADM of the published mean at the latitude used:

| classes | N_pub | N | B_pub | B | sigma_pub | sigma | vadm_pub | vadm |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 and 2 | 4 | 4 | 18.9 | 18.85 | 2.0 | 1.98 | 4.4 | 4.37 |
| 1 to 3 | 8 | 8 | 18.5 | 18.45 | 1.9 | 1.87 | 4.3 | 4.27 |

## Rock-magnetic files

11 powders, one per flow, converted with the PmagPy VFTB converter: LP-HYS 11 curves, 506 points; LP-IMT 10 curves, 5125 points; LP-IRM 11 curves, 140 points; LP-IRM-DCD 11 curves, 199 points. Each specimen is entered with the suffix `r` in the sample named by the file (PRG1-2.irm is a powder of core PRG1-2), with the weight given in the file.

The results of Table S1 are entered on the specimen rows (hysteresis parameters, S ratio) and as one row per Curie temperature. A simple recalculation from the archived curves, against Table S1 with its Mrs and Ms multiplied by 1000 (`_pub`; Am²/kg, mT): `sirm_irm` largest IRM, `sirm_back` first point of the back-field curve, `mrs_loop`, `ms` and `bc` from the loop after removing the high-field slope, `bcr` zero crossing of the back-field curve, `s_ratio` from the back-field curve at 0.3 T.

| sample | mrs_pub | sirm_irm | sirm_back | mrs_loop | ms_pub | ms | bc_pub | bc | bcr_pub | bcr | s_pub | s_ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PRG1-2 | 0.107 | 0.110 | 0.109 | 0.111 | 0.325 | 0.326 | 28.0 | 28.9 | 52.8 | 52.9 | 0.95 | 0.94 |
| PRG2-4 | 0.158 | 0.158 | 0.160 | 0.162 | 1.090 | 1.090 | 17.8 | 16.6 | 42.8 | 43.4 | 0.98 | 0.97 |
| PRG3-5 | 0.142 | 0.144 | 0.143 | 0.145 | 0.888 | 0.890 | 17.2 | 17.8 | 42.4 | 42.9 | 0.96 | 0.97 |
| PRG4-2 | 0.170 | 0.170 | 0.170 | 0.175 | 1.040 | 1.039 | 19.8 | 19.6 | 49.1 | 47.4 | 0.96 | 0.97 |
| PRG5-6 | 0.342 | 0.358 | 0.357 | 0.369 | 1.330 | 1.331 | 22.8 | 22.5 | 59.2 | 56.9 | 0.98 | 1.01 |
| PRG6-7 | 0.577 | 0.582 | 0.580 | 0.597 | 2.030 | 2.037 | 27.0 | 27.1 | 54.5 | 54.8 | 0.99 | 0.99 |
| PRG7-8 | 0.444 | 0.457 | 0.457 | 0.462 | 1.410 | 1.407 | 41.3 | 40.5 | 69.0 | 70.5 | 1.00 | 0.99 |
| PRG8-7 | 0.328 | 0.331 | 0.335 | 0.342 | 1.190 | 1.187 | 28.2 | 28.4 | 70.5 | 70.4 | 0.98 | 0.98 |
| PRG9-8 | 0.385 | 0.384 | 0.382 | 0.396 | 2.440 | 2.434 | 20.9 | 19.6 | 41.8 | 48.2 | 0.98 | 0.99 |
| PRG10-5 | 0.754 | 0.776 | 0.777 | 0.783 | 1.890 | 1.910 | 53.4 | 49.6 | 75.4 | 76.9 | 0.98 | 0.98 |
| PRG11-1 | 0.437 | 0.448 | 0.450 | 0.453 | 1.280 | 1.280 | 40.4 | 40.0 | 65.5 | 65.5 | 0.98 | 0.98 |

Recalculated over published: Ms 0.997 to 1.011; saturation remanence 0.996 to 1.046; Bc 0.93 to 1.04; Bcr 0.96 to 1.15 (the largest is PRG9-8); S ratio within 0.025. The agreement of Ms fixes the factor of 1000 between Table S1 and the archived curves in emu/g. The Curie temperatures were not recalculated; on the archived curves the magnetization falls fastest 20 to 30 °C lower on cooling than on heating, so the higher column of Table S1 (H) is entered as the heating branch, as in the text of the paper.

- No file for: PRG8-7.rmp.
- PRG8-7: Table S1 gives Curie temperatures, but the archive has no magnetization-temperature file for it.

## Units of the moments

The demagnetization files give the moments in a column labeled A/m, with NRMs of 5.5e-04 to 1.4e-03 (flow medians); the Thellier files give no unit and have the same values flow by flow. Both are entered as volume-normalized magnetization (`magn_volume`) after multiplying by 1000, that is, reading the numbers as emu/cm³:

- emu/cm³ is the volume-normalized unit of the 2G magnetometer software, and 1 emu/cm³ is 1000 A/m.
- The rock-magnetic table of the same study (Table S1) is related to its archived curves by the same factor of 1000 (section above).
- The NRMs become 0.55 to 1.45 A/m (`rs3`), 0.04 to 0.30 percent of the saturation remanence of the IRM curves at 2900 kg/m³ (`rem`). The multispecimen pellets, measured on a JR6 and scaled from one eighth of a core to a whole one, give values of the same order (`pellets`).
- If the numbers were per gram instead (emu/g), the NRMs would be 2.9 times higher (`as_mass`). The comparisons do not separate the two readings, so the magnetization is known to about that factor.
- The paleointensities and directions do not depend on the unit. The multispecimen moments are JR6 values in A/m of pellet, and the rock-magnetic curves are in emu/g in the files.
- `build/converted_directions/` and `build/converted_thellier/` hold the converter output with the values as in the files.

| flow | rs3 | tdt | sirm | rem | pellets | as_mass |
| --- | --- | --- | --- | --- | --- | --- |
| PRG1 | 0.71 | 0.59 | 0.110 | 0.22 | 1.8 | 2.1 |
| PRG2 | 0.60 | 1.08 | 0.158 | 0.13 | 1.7 | 1.7 |
| PRG3 | 1.24 | 1.27 | 0.144 | 0.30 | 2.0 | 3.6 |
| PRG4 | 1.45 | 1.38 | 0.170 | 0.29 | 1.5 | 4.2 |
| PRG5 | 0.92 | 0.89 | 0.358 | 0.09 | 1.6 | 2.7 |
| PRG6 | 0.69 | 0.75 | 0.582 | 0.04 | 1.1 | 2.0 |
| PRG7 | 1.35 | 1.32 | 0.457 | 0.10 | 2.7 | 3.9 |
| PRG8 | 0.55 | 0.69 | 0.331 | 0.06 | 1.5 | 1.6 |
| PRG9 | 0.60 | 0.54 | 0.384 | 0.05 | 0.9 | 1.7 |
| PRG10 | 0.91 | 0.85 | 0.776 | 0.04 | 1.9 | 2.6 |
| PRG11 | 1.16 | 1.06 | 0.448 | 0.09 | 2.6 | 3.4 |

`rs3`, `tdt`: median NRM of the demagnetization and Thellier specimens as entered (A/m). `sirm`: largest IRM of the flow's `.irm` file (Am²/kg). `rem`: NRM as a percentage of it. `pellets`: eight times the median JR6 NRM of the flow's multispecimen pellets (A/m). `as_mass`: the NRM in A/m if the file values were emu/g.

## Information that would complete the contribution

- The coordinates of each flow (now one position for all 11, georeferenced from the star of Figure 1b).
- Bedding, if any applies (the flows are taken as untilted).
- The compass used for each core and any declination correction (all cores carry SO-SUN:SO-MAG).
- The unit of the moments in the demagnetization and Thellier files, and specimen volumes or masses.
- The stratigraphic height of each flow (the order, PRG1 at the base, is entered).
- The multispecimen heating temperature of each flow and the core used.

