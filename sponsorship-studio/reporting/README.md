# Reporting — how the Studio reports back to the team

The Studio can notify the AIC sponsor-partnerships team when a chapter **sets up**
the tool, **uses** it, each time a **proposal is created**, when an **invoice is
sent**, and — most important — each time a sponsorship is **won** (payment
received). It does this by POSTing small JSON events to a Google Apps Script web
app that logs every event to a Google Sheet, keeps a per-chapter **Summary**
(hits vs. wins vs. $ won), and emails the team.

This only works on the **hosted** Studio (GitHub Pages), not a downloaded file —
and only once the endpoint is configured (below). Until then, reporting is off
and the Studio behaves exactly as before.

## One-time setup (~5 minutes)

1. Create a Google Sheet to hold the log (e.g. "AIC Sponsorship Studio — Activity").
2. In that Sheet, open **Extensions → Apps Script**, delete the sample, and paste
   [`Code.gs`](./Code.gs). Save.
3. **Deploy → New deployment → Web app.** Set **Execute as: Me** and
   **Who has access: Anyone**. Deploy, authorize, and copy the **Web app URL**
   (ends in `/exec`).
4. Send that URL back to be set as the Studio's `REPORT_ENDPOINT` (one-line change,
   then the hosted Studio redeploys). Notifications go to `mark@aicollective.com`
   and `erich@aicollective.com` — edit `NOTIFY` in `Code.gs` to change that.

## What gets sent

| Event | When | Emailed? |
| --- | --- | --- |
| `setup` | first time a chapter configures its name in Settings | Yes |
| `usage` | once per browser session when a configured chapter opens the Studio | Logged only |
| `proposal` | each time a proposal number is assigned | Yes, with sponsor / amount / referrer / line items |
| `invoice` | chapter clicks **Mark invoice sent** in the Documents tab | Yes |
| `payment` | chapter clicks **Log payment received ✓ (win)** in the Documents tab | Yes — a 🎉 WIN notice |

Every event is appended as a row on the **Events** tab of the Sheet. The
`proposal`, `invoice`, and `payment` events also roll up into a **Summary** tab —
one row per chapter with proposals (hits), invoices sent, wins (paid), $ won, and
a win rate — so you can see hits vs. wins at a glance.

### Already deployed? Redeploy to pick up the new events

If you deployed an earlier version of `Code.gs`, paste the current file over it in
Apps Script, then **Deploy → Manage deployments → edit (pencil) → Version: New
version → Deploy**. The `/exec` URL stays the same, so nothing changes in the
Studio — it just starts recording invoices, wins, and the Summary tab.

## Two separate books (commercial vs. non-profit)

Commercial money and 501(c)(3) money are kept in **two different Google Sheets**,
with two separate Apps Script deployments. They are never combined — separate
files means separate books, separate sharing, and nothing to untangle if the
fiscal sponsor or an auditor asks.

| | Commercial | Non-profit |
| --- | --- | --- |
| Sheet | "AIC Sponsorship — Commercial" | "AIC Sponsorship — Non-profit" |
| `STREAM` in `Code.gs` | `'commercial'` | `'nonprofit'` |
| Studio constant | `REPORT_ENDPOINT` | `REPORT_ENDPOINT_NP` |
| Holds | Sponsorships into the regional LLC | Grants and 501(c)(3)-required donors |
| Commissions | Yes | **Never** |

### Setting up the second (non-profit) book

1. Create a **second** Google Sheet, e.g. "AIC Sponsorship — Non-profit".
2. **Extensions → Apps Script**, paste the same `Code.gs`, and change one line
   near the top to `var STREAM = 'nonprofit';` (also set `HQ_PASS`). Save.
3. **Deploy → New deployment → Web app** (Execute as: Me · Who has access:
   Anyone). Copy the `/exec` URL.
4. Set that URL as `REPORT_ENDPOINT_NP` in the Studio.

Each deployment **refuses events tagged for the other stream**, so a non-profit
payment can never land in the commercial book even if something is misconfigured.
In the Studio's Documents tab, every deal is booked with a **Commercial /
Non-profit** switch before it's logged.

## Client sync (the shared CRM)

The same web app also backs the **Clients (CRM)** panel in the Documents tab.
Chapter leads work locally, then click **Sync now** to share their clients with
the team and pull in teammates' updates. Two extra tabs appear automatically:

| Tab | Holds |
| --- | --- |
| `Clients` | one row per client — `Chapter · Client ID · Updated · JSON` |
| `ChapterKeys` | one row per chapter — `Chapter · Passcode · Region · Created` |

**How the passcode works**

- The **first** time a chapter syncs, whatever passcode the lead types becomes
  that chapter's passcode (a row is added to `ChapterKeys`). After that, the same
  code is required to read or write that chapter's clients.
- A chapter's passcode unlocks **only that chapter's** clients — chapters can't
  see each other's pipelines.
- **Set `HQ_PASS`** at the top of `Code.gs` to a strong private phrase before you
  deploy. That one passcode can **read every chapter** (use chapter `*` for all,
  or a specific chapter name). It's read-only — saving always uses the chapter's
  own passcode.

**How merging works** — newest edit wins. Every client carries an `updated`
timestamp; a save never overwrites a server record that's newer, and a pull only
replaces a local record when the server's copy is newer. Sync is manual, so leads
always control when their local copy (the source of truth) is shared.

> This is lightweight gating, not encryption — passcodes and client data live in
> the Sheet in plain text, and passcodes travel in the request. Fine for
> coordinating a team; don't store anything you'd treat as a secret.

## Notes

- The Studio shows a short line in Settings letting chapters know that setup,
  usage, and proposals are shared with the AIC team (transparency). Remove it in
  the Studio source if you don't want it.
- Events are best-effort and fire-and-forget (`fetch` with `mode: 'no-cors'`), so
  reporting never blocks or breaks the Studio if the endpoint is unreachable.
- No personal browsing data is sent — only the chapter/region name, language, and
  the sponsor/proposal fields the organizer entered.
