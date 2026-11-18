# Source data

The four archives in this folder are unmodified copies of the files of:

Calvo-Rathert, M., Carrancho, Á., Morales, J., Pérez, N., & Caccavari, A. (2021). *Rock-magnetic, paleomagnetic and multimethod paleointensity data from an upper Miocene lava flow sequence from São Vicente (Cape Verde)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.5553392

License: Creative Commons Attribution 4.0 International (CC BY 4.0). Downloaded 2026-10-24 and 2026-11-10. The MD5 checksums match those listed by Zenodo.

| File | Bytes | MD5 | SHA-256 |
| --- | --- | --- | --- |
| `Praia Grande Paleomagnetism Data.zip` | 62,119 | `c623b2d45613d9fd05ab6371f3db4de5` | `bcf864becf1cb2743f0377db419599bdb657105c0e2e2d78d5792a7af6469ed7` |
| `Praia Grande Thellier-Coe Data.zip` | 46,169 | `0806d4dc4206f89ad161092f25aa53af` | `4833cf170697467e46dcdfe73709e0028bdd6d34ffb1182112d0384c724b7ecc` |
| `Praia Grande Multispecimen Data.zip` | 30,117 | `1c9b74fdc8915c25fa9fe87c1637b67e` | `78cc568a159e0c1a68c1f907ef5fbc8c1924683720e5b0a18a004dc098fde6f5` |
| `Praia Grande Rock Magnetism Data.zip` | 105,813 | `6263c9a655eb4e009fc1c34aa10fadeb` | `b75549d77a2a746ca629f9700426d26dd254b1750e60f380c7224c57681734da` |

| Archive | Contents | Format |
| --- | --- | --- |
| Paleomagnetism | 88 `.rs3` files, one per specimen: thermal and alternating-field demagnetization | Remasoft (AGICO) |
| Thellier-Coe | 82 `.tdt` files | ThellierTool |
| Multispecimen | `M0`–`M4`, each as `.jr6` and `.txt`: one file per step of the protocol | AGICO JR6 |
| Rock Magnetism | 11 `.irm`, 11 `.hys`, 11 `.coe`, 10 `.rmp` | variable field translation balance (VFTB) |

`convert.py` unzips them into `build/extracted/`, which is not kept in the repository.
