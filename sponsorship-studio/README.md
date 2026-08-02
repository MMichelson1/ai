# AIC Sponsorship Studio

A self-contained toolkit for The AI Collective chapter and region directors to
build sponsorship brochures, proposals, agreements, and price quotes. Everything
runs client-side in a single HTML file — no server, no build step, works offline.

## Files

| File | What it is |
| --- | --- |
| `AIC-Sponsorship-Studio.html` | The tool itself. Calculator, proposal builder, agreement/invoice generator, and a print-ready brochure. Ships blank — each director fills in their own chapter details. |
| `AIC-Studio-Setup-Guide.html` | One-page setup guide for directors, with a language switcher (English, Español, Français, Deutsch, Português, 日本語). Auto-detects the reader's browser language. |

## Distributing to directors

1. Send both files (email attachment, shared Drive/Dropbox folder, etc.).
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
