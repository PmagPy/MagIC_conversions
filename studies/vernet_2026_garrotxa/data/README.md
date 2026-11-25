# Source data

The archive in this folder is an unmodified copy of the file of:

Vernet Tarragó, E. (2026). *Raw data of La Garrotxa Volcanic Field (NE Iberia) Pleistocene lava-flows* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20326424

License: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/. Downloaded 2026-11-11. The MD5 checksum matches the one listed by Zenodo.

| File | Bytes | MD5 | SHA-256 |
| --- | --- | --- | --- |
| `LA GARROTXA_rev1.zip` | 13,459,220 | `4c30b26f29d2562ee36218b0615dede6` | `dab7627b3baeaa48c8353b5afc81c402d3695d45de2994406d80e1f50359c3ca` |

| Folder in the archive | Contents | Format |
| --- | --- | --- |
| `PALEOMAGNETIC DIRECTIONS/` | 99 `.dat` files (GTX sites) and 134 `.rs3` files (all sites), one per specimen; the `.rs3` files hold the authors' fits and, for the GTX sites, the measurements of the `.dat` files except six steps (study README, item 1); 4 `.rsf` | 2G Enterprises binary; Remasoft (AGICO) |
| `PALEOINTENSITY/` | 142 `.TDT` files in one folder per site: 82 standard Thellier-Coe experiments, 46 with low-temperature demagnetization (`LTD_*.TDT`) and 14 corrected copies (`*_C.TDT`, `*_CC.TDT`; study README, item 23) | ThellierTool |
| `ROCK MAG/` | 21 powders, each with `.irm`, `.coe`, `.hys` and `.rmp` curves and a `.prm` file of instrument settings; figures (`.pdf`, `.png`, `.emf`, `.svg`) | VFTB (RockMag Analyzer) |
| `THERMAL STABILITY/` | 46 `.rmp` partial magnetization-temperature cycles in one folder per site, 7 `.prm` files of settings, figures | VFTB (RockMag Analyzer) |

The `.prm` files are the measurement settings of the instrument (YAML), not data; they and the figures are not converted.

`extract_tables.py` in the study folder downloads the PDF of the paper (CC BY-SA 4.0) into `build/` and checks it against SHA-256 `43787a91083db460b6896065ac944dd3ece3522a92ec4eb797c88b48d7e1bf71` (MD5 `898f9688ce7e2672b3f0affc5a9e7d66`, 14,438,016 bytes, downloaded 2026-11-25); it is not kept here.
