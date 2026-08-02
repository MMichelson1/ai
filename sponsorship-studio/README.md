# AIC Sponsorship Studio

A self-contained toolkit for The AI Collective chapter and region directors to
build sponsorship brochures, proposals, agreements, and price quotes. Everything
runs client-side in a single HTML file — no server, no build step, works offline.

## Files

| File | What it is |
| --- | --- |
| `AIC-Sponsorship-Studio.html` | The tool itself. Calculator, proposal builder, agreement/invoice generator, and a print-ready brochure. Ships blank — each director fills in their own chapter details. |
| `AIC-Studio-Setup-Guide.html` | One-page setup guide for directors, with a language switcher (English, Español, Français, Deutsch, Português, 日本語). Auto-detects the reader's browser language. |
| `START-HERE-Instructions.txt` | Plain-text setup instructions for the distributable kit, aimed at regional managers and chapter leads. |
| `scripts/artifact-src.sh` | Strips the standalone `<!doctype>/<html>` wrapper to produce publish-ready source for the hosted Claude artifacts (see "Hosted versions" below). |

## Hosted versions (Claude artifacts)

These files are the source of truth; the hosted artifacts are republished from them.

| Source file | Hosted artifact |
| --- | --- |
| `AIC-Sponsorship-Studio.html` | https://claude.ai/code/artifact/9e3f2ce7-6736-41ad-ba52-c580c4949b75 |
| `AIC-Studio-Setup-Guide.html` | https://claude.ai/code/artifact/0ac3aeb0-080b-4299-9b37-3a209f51888c |

To keep an artifact in sync after editing its source file, regenerate the
publish-ready body and republish it to the **same** artifact URL:

```sh
scripts/artifact-src.sh AIC-Sponsorship-Studio.html > /tmp/publish.html
# then publish /tmp/publish.html to the artifact URL above
```

## Distributing to directors

1. Send the kit (`AIC-Sponsorship-Studio-Kit.zip`, or the files individually) via
   email attachment or a shared Drive/Dropbox folder.
2. A director saves `AIC-Sponsorship-Studio.html` and double-clicks it — it opens
   in any browser and runs fully offline.
3. **Required for every chapter and region:** in **Settings → Chapter profile**,
   set the **Brochure CTA link** to the chapter's Luma / signup URL. The brochure's
   "Sponsor" button has nowhere to send prospects until this is set, and a warning
   stays on screen until it is.

## How data is stored

All settings are saved in the director's own browser (`localStorage`), scoped to
their device. Nothing is uploaded or shared automatically, and no director sees
another's configuration. To move a setup between devices, use **Settings → Export**
to download a config file and **Import** to restore it.

## Editing

Both files are plain, dependency-free HTML — open in any editor. The Studio's
content and pricing defaults live in the `DEFAULTS` object near the top of
`AIC-Sponsorship-Studio.html`; UI strings are in the `T` translation table.
