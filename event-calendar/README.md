# The AI Collective — AI Event Calendar

A shareable, self-updating monthly calendar of **validated, in-person AI events** —
meetings, classes, workshops, demo nights, hackathons, socials and more — for any
market where The AI Collective operates (250+ chapters, 60+ countries).

**Zero AI tokens, forever.** Events are gathered by *subscribing to structured
calendar feeds* (Luma iCal, Meetup iCal, IEEE vTools, university calendars), not by
AI-powered searching. A scheduled GitHub Action fetches, validates, classifies and
geocodes events using plain HTTP, then publishes a static page. Viewing, sharing,
and refreshing the calendar costs nothing — no API keys, no tokens, no per-viewer
compute. It runs on the free tier of GitHub Actions + GitHub Pages.

## What viewers get

- **Current month opens automatically** (open it on August 3, you see August), with
  ‹ › arrows to move between months.
- **Orange dots** = AI Collective events · **Blue dots** = community events. Click
  any date for that day's full list.
- **"Coming up"** list of the next four weeks below the calendar.
- Every event shows **title, location, date, time, organizer, capacity, type**
  (workshop / hackathon / panel / demo night / vibe night / social / coffee / walk /
  class / pitch / meetup), a **Free / Paid** label, and a **Register** button linking
  to the live listing.
- **City search**: type any city name (e.g. "Atlanta", "Berlin", "São Paulo") and the
  calendar shows validated events within a 25 / 50 / 100-mile radius. Shareable links:
  `…/#city=Berlin`.

## How events are validated

An event appears only if **all** of these hold:

1. **Trusted, active source** — the listing lives on lu.ma, meetup.com, eventbrite.*,
   ieee.org / vtools.ieee.org, acm.org, or a `.edu` domain, and the feed answered
   at fetch time.
2. **In-person** — the listing carries a physical street address; anything matching
   virtual/webinar/Zoom/Meet/Teams patterns is rejected.
3. **AI-related** — title/description must match AI keywords (machine learning, LLM,
   GenAI, robotics, data science, …). Feeds that are 100% AI (like AI Collective
   calendars) are marked `assumeAI: true` and skip the keyword check.

Duplicates across feeds are collapsed. Venues are geocoded once (OpenStreetMap
Nominatim, cached in `data/geocache.json`) so radius search works.

## Sources searched per market

| Source | How |
|---|---|
| The AI Collective — Atlanta | `lu.ma/aicatl` (Luma iCal feed, auto-resolved) |
| The AI Collective — Worldwide | `lu.ma/genaicollective` (all chapters' events, geocoded, searchable by city) |
| Meetup.com | any group's feed: `https://www.meetup.com/<group>/events/ical/` |
| IEEE (vTools) | section iCal feed from events.vtools.ieee.org |
| Universities, colleges & schools | their public ICS feeds (Localist, Google Calendar, etc.) |
| Eventbrite | per-organizer via free API token (`EVENTBRITE_TOKEN` repo secret) — optional |
| LinkedIn & Facebook | no public feeds exist; chapter leads submit validated events via PR to `data/manual-events.json` |

The live page lists each source with its status (`ok` / `error` / `needs-setup` /
`manual`) and the number of events it contributed.

## One-time setup (repo owner)

1. Merge this to your default branch.
2. Repo **Settings → Pages → Source: GitHub Actions**.
3. Run the **"Update events & deploy calendar"** workflow once (Actions tab →
   Run workflow). It self-tests the parser, fetches live events, commits
   `data/events.json`, and deploys the site.
4. Done — it refreshes itself every 6 hours.

## Add your city (chapter leads anywhere in the world)

Copy the `atlanta` block in [`data/sources.json`](data/sources.json), then:

```jsonc
"berlin": {
  "label": "Berlin, Germany",
  "tz": "Europe/Berlin",
  "center": { "lat": 52.52, "lon": 13.405 },
  "radiusMiles": 50,
  "sources": [
    { "name": "AI Collective Berlin (Luma)", "type": "luma-calendar",
      "slug": "your-luma-slug", "url": "https://lu.ma/your-luma-slug",
      "organizer": "The AI Collective — Berlin", "aic": true, "assumeAI": true, "enabled": true }
  ]
}
```

Even with **no** local feeds configured, city search already works everywhere:
worldwide AI Collective events from `lu.ma/genaicollective` are geocoded and
searchable by any city name.

## Sharing without using anyone's tokens

- **Share the GitHub Pages URL** — viewers just load a static page.
- **Fork the repo** — every chapter can run its own copy on GitHub's free tier;
  nothing points back at your account or files.
- The single-file app (`index.html`) also works standalone (embedded fallback data)
  and can be dropped into any static host.

## Token / cost budget

| Activity | AI tokens | Other cost |
|---|---|---|
| Viewing / sharing the calendar | 0 | free (GitHub Pages) |
| 6-hourly refresh | 0 | ~1–2 min GitHub Actions (free tier ≈ 2,000 min/mo) |
| Geocoding new venues | 0 | free (Nominatim, rate-limited, cached) |
| One-time build of this tool | done | — |

## Files

- `index.html` — the whole app (no build step, no dependencies, works offline).
- `data/sources.json` — per-market feed registry. **Edit this to add cities/feeds.**
- `data/events.json` — generated event data (do not edit; overwritten by the Action).
- `data/manual-events.json` — hand-validated events from LinkedIn/Facebook/etc.
- `data/geocache.json` — venue → coordinates cache (generated).
- `scripts/fetch-events.mjs` — fetch/validate/classify/geocode (Node 20, stdlib only;
  `--self-test` runs its parser checks).
- `.github/workflows/update-events.yml` — 6-hourly refresh + Pages deploy.
