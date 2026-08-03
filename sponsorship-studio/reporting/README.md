# Reporting — how the Studio reports back to the team

The Studio can notify the AIC sponsor-partnerships team when a chapter **sets up**
the tool, **uses** it, and each time a **proposal is created** (with details). It
does this by POSTing small JSON events to a Google Apps Script web app that logs
to a Google Sheet and emails the team.

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

Every event is also appended as a row on the **Events** tab of the Sheet.

## Notes

- The Studio shows a short line in Settings letting chapters know that setup,
  usage, and proposals are shared with the AIC team (transparency). Remove it in
  the Studio source if you don't want it.
- Events are best-effort and fire-and-forget (`fetch` with `mode: 'no-cors'`), so
  reporting never blocks or breaks the Studio if the endpoint is unreachable.
- No personal browsing data is sent — only the chapter/region name, language, and
  the sponsor/proposal fields the organizer entered.
