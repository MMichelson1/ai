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

## Hosted version (GitHub Pages) — the live link

This repo publishes the Studio to GitHub Pages automatically. The
`.github/workflows/update-events.yml` workflow assembles the site and deploys it
on every push to the default branch that touches `sponsorship-studio/**`.

| Page | URL |
| --- | --- |
| Sponsorship Studio | `https://mmichelson1.github.io/ai/sponsorship-studio/` |
| Setup guide | `https://mmichelson1.github.io/ai/sponsorship-studio/setup-guide.html` |

> The exact base URL is shown in the **deploy** job's output (Actions tab) and in
> **Settings → Pages**. The link goes live after this branch is merged to the
> default branch and the workflow runs.

**This hosted link is the primary way chapters use the Studio.** Editing a source
file and merging it republishes the live page for everyone automatically — each
chapter's own settings live in their browser (`localStorage`) and survive
updates. The single HTML file also still works fully offline (it bundles the PDF
libraries), so it doubles as a downloadable backup via Drive.

> Note: a Claude-artifact host is **not** suitable here — its content security
> policy blocks the outbound request the Studio needs for reporting-back. GitHub
> Pages allows it, which is why it's the canonical host.

## Distributing to directors

1. Send directors the **live link**
   (`https://mmichelson1.github.io/ai/sponsorship-studio/`). They open it in any
   browser — nothing to install, and they always get the latest version.
2. A shared Drive folder holds a downloadable copy of the single HTML file as an
   **offline backup** (it runs fully offline too).
3. **Sponsor contact:** the brochure's "Book a sponsorship call" button defaults
   to the organization contact (Erich Starrett). In **Settings → Chapter
   profile**, a chapter can override it with its own **Sponsor contact** — an
   email, a calendar link (e.g. Calendly), or both.

## How data is stored

All settings are saved in the director's own browser (`localStorage`), scoped to
their device. Nothing is uploaded or shared automatically, and no director sees
another's configuration. To move a setup between devices, use **Settings → Export**
to download a config file and **Import** to restore it.

## Editing

Both files are plain, dependency-free HTML — open in any editor. The Studio's
content and pricing defaults live in the `DEFAULTS` object near the top of
`AIC-Sponsorship-Studio.html`; UI strings are in the `T` translation table.
