# Backups — original AIC Sponsorship Studio release

Frozen, byte-for-byte copies of the **original** Studio files as first released
(git commit `8820eb6`), kept as a known-good baseline. If later updates cause
any drift — a layout change, a broken feature, wrong pricing — compare against
or restore from these.

| Backup file | Restores | Original size / SHA-256 |
| --- | --- | --- |
| `AIC-Sponsorship-Studio.original-v1.html` | `../AIC-Sponsorship-Studio.html` | 111,873 bytes · `bc66b7f6…3f9c1c` |
| `AIC-Studio-Setup-Guide.original-v1.html` | `../AIC-Studio-Setup-Guide.html` | 20,290 bytes |

These are reference copies only — **never edit them**. They are not part of the
published/hosted Studio and should be excluded from any GitHub Pages deploy.

## How to restore the original

```sh
# From the sponsorship-studio/ directory:
cp backups/AIC-Sponsorship-Studio.original-v1.html AIC-Sponsorship-Studio.html
cp backups/AIC-Studio-Setup-Guide.original-v1.html AIC-Studio-Setup-Guide.html
```

## How to check for drift

```sh
# See exactly what changed vs. the original release:
diff backups/AIC-Sponsorship-Studio.original-v1.html AIC-Sponsorship-Studio.html
```

## Note

Git already preserves every version of these files. This folder is an
extra, easy-to-find safety copy that travels with the repo (and the Drive
backup) so a non-developer can recover the original without using git.
Each subsequent stable release can be snapshotted here as
`…original-v2.html`, `…original-v3.html`, and so on.
