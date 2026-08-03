# AI Fundamentals Workshop Builder

A self-contained tool for building **The AI Collective — "AI Fundamentals for
Professionals"** workshop each month. Pick the audience, set the date and venue,
choose which AI tools to feature, and it generates every asset you need to
promote and run the session. Everything runs client-side in a single HTML file —
no server, no build step, no API keys or tokens, and it works offline.

## What it generates

From one audience selection (plus date, venue, seats, and tool choices), the
builder produces:

- **Luma listing** — event title, description, and promo copy for the audience.
- **Agenda / run-of-show** — timed segments for the session.
- **Slides** — a slide-by-slide outline you can hand to a deck.
- **Handouts** — audience-specific take-home material.
- **`me.md` context file** — a personal-context file to paste into Claude,
  ChatGPT, or Gemini so the tools answer as *this* professional.
- **A prep reminder** — under **Event details**, the builder computes a reminder
  a set number of weeks before the event (default **3**, adjustable) and exports
  it as an **`.ics` download** or an **Add to Google Calendar** link. A one-click
  **"Use 2nd Wednesday of next month"** button fills the series' default date, but
  the reminder follows whatever date you enter, so a one-off date or venue works
  the same way. Your weeks-before preference is saved in the browser.

It ships pre-loaded with the Atlanta chapter defaults (Mark Michelson, Threads
Marketing Research & Strategy, AIC Atlanta, Improving — Alpharetta) and covers 17
professional audiences — Sales, HR, Legal, Real Estate, Financial Advisors,
Marketing, Product, Customer Success, Nonprofit, Healthcare, and more — with the
option to merge two audiences or define a custom one.

Your edits to an audience profile (ICP) and any custom audiences you add are
saved in the browser (`localStorage`), so they carry over month to month.

## Monthly workflow

1. Open the hosted page (link below) and bookmark it.
2. Pick the month's **audience**, set the **date / venue / seats** (use the
   **2nd Wednesday** button for the default cadence, or set your own date).
3. Add the **prep reminder** to your calendar (`.ics` or Google Calendar) so the
   next build is scheduled — 3 weeks out by default.
4. Choose the **AI tools** to feature and up to four to **deep-dive**.
5. Click **Generate all**, then copy each tab into Luma, your deck, and handouts.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The tool itself. Single-file, self-contained, works offline. |
| `scripts/artifact-src.sh` | Strips the standalone `<!doctype>/<html>` wrapper to produce publish-ready source for the hosted Claude artifact. |

## Hosted version (GitHub Pages) — the live link

This repo publishes the builder to GitHub Pages automatically. The
`.github/workflows/update-events.yml` workflow assembles the site and deploys it
on every push to the default branch that touches `workshop-builder/**`.

| Page | URL |
| --- | --- |
| Workshop Builder | `https://mmichelson1.github.io/ai/workshop-builder/` |

> The exact base URL is shown in the **deploy** job's output (Actions tab) and in
> **Settings → Pages**. The link goes live after this branch is merged to the
> default branch and the workflow runs.

**This hosted link is the primary way to use the builder each month.** Editing
`index.html` and merging republishes the live page automatically — your own
settings live in your browser (`localStorage`) and survive updates. The single
HTML file also works fully offline, so it doubles as a downloadable backup.
