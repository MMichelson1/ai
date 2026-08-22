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

## Notes

- The Studio shows a short line in Settings letting chapters know that setup,
  usage, and proposals are shared with the AIC team (transparency). Remove it in
  the Studio source if you don't want it.
- Events are best-effort and fire-and-forget (`fetch` with `mode: 'no-cors'`), so
  reporting never blocks or breaks the Studio if the endpoint is unreachable.
- No personal browsing data is sent — only the chapter/region name, language, and
  the sponsor/proposal fields the organizer entered.
