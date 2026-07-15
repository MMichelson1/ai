#!/usr/bin/env node
/**
 * AI Collective Event Calendar — event fetcher.
 *
 * Subscribes to structured calendar feeds (Luma ICS, Meetup ICS, IEEE vTools
 * ICS, university ICS), validates that each event is in-person and AI-related,
 * classifies it, geocodes its venue, and writes data/events.json.
 *
 * Zero AI/LLM tokens are used: everything here is plain HTTP + string parsing.
 * Designed to run in GitHub Actions on a schedule (see .github/workflows).
 *
 * Usage:
 *   node scripts/fetch-events.mjs            # full run
 *   node scripts/fetch-events.mjs --no-geocode  # skip Nominatim lookups
 *   node scripts/fetch-events.mjs --self-test   # run parser unit checks only
 */

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const DATA = join(ROOT, "data");
const UA = "AI-Collective-Event-Calendar/1.0 (+https://github.com/mmichelson1/ai)";

const WINDOW_PAST_DAYS = 1; // keep events since yesterday
const WINDOW_FUTURE_DAYS = 120; // look ahead ~4 months
const MAX_GEOCODES_PER_RUN = 150;

// Trusted hosts an event listing must live on to count as "validated".
const TRUSTED_HOSTS = [
  "lu.ma", "luma.com", "meetup.com", "eventbrite.com", "eventbrite.co.uk",
  "eventbrite.ca", "eventbrite.com.au", "eventbrite.de", "eventbrite.fr",
  "ieee.org", "vtools.ieee.org", "acm.org",
];
const trustedHost = (url) => {
  try {
    const h = new URL(url).hostname.replace(/^www\./, "");
    return TRUSTED_HOSTS.some((t) => h === t || h.endsWith("." + t)) || h.endsWith(".edu");
  } catch { return false; }
};

const AI_RE = /(\bA\.?I\.?\b|artificial intelligence|machine learning|deep learning|\bgen\s?ai\b|generative|\bLLMs?\b|\bGPT\b|ChatGPT|Claude|Gemini|Copilot|data science|neural net|robotic|computer vision|\bNLP\b|natural language|\bagentic\b|AI agent|prompt engineer|MLOps|RAG\b|diffusion model|foundation model)/i;

const VIRTUAL_RE = /(zoom\.us|zoom meeting|meet\.google|teams\.microsoft|webex|\bonline only\b|\bonline event\b|\bvirtual\b|\bwebinar\b|livestream|live stream|\bremote\b)/i;

const TYPE_RULES = [
  ["hackathon", /hackathon|hack night|build(-|\s)?a(-|\s)?thon|buildathon/i],
  ["demo night", /demo night|demo day|demos\b|show\s?&?\s?tell|showcase/i],
  ["vibe night", /vibe coding|vibe night|vibecode/i],
  ["workshop", /workshop|hands-on|bootcamp|masterclass|tutorial|training/i],
  ["class", /\bclass\b|course|lecture|seminar/i],
  ["panel", /panel|fireside|keynote|\btalk\b|speaker|discussion|summit|conference/i],
  ["coffee", /coffee|breakfast|brunch|morning meet/i],
  ["walk", /\bwalk\b|hike|run club|stroll/i],
  ["pitch", /pitch|investor|founder showcase/i],
  ["social", /social|happy hour|mixer|networking|drinks|party|picnic/i],
];
const classify = (text) => {
  for (const [type, re] of TYPE_RULES) if (re.test(text)) return type;
  return "meetup";
};

const priceOf = (text) => {
  if (/free to attend|free admission|free event|admission is free|\bfree\b/i.test(text)) return "free";
  if (/\$\s?\d|€\s?\d|£\s?\d|tickets? (from|start)|paid event|registration fee|admission:/i.test(text)) return "paid";
  return "check";
};

const capacityOf = (text) => {
  const m = text.match(/(?:capacity|limited to|max(?:imum)?(?: of)?)[:\s]+(\d{2,4})\b/i);
  return m ? Number(m[1]) : null;
};

// ---------------------------------------------------------------- ICS parsing

export function unfoldIcs(raw) {
  return raw.replace(/\r?\n[ \t]/g, "");
}

const unescapeText = (v) =>
  v.replace(/\\n/gi, "\n").replace(/\\,/g, ",").replace(/\\;/g, ";").replace(/\\\\/g, "\\");

export function parseIcs(raw) {
  const lines = unfoldIcs(raw).split(/\r?\n/);
  const events = [];
  let cur = null;
  for (const line of lines) {
    if (line === "BEGIN:VEVENT") { cur = {}; continue; }
    if (line === "END:VEVENT") { if (cur) events.push(cur); cur = null; continue; }
    if (!cur) continue;
    const idx = line.indexOf(":");
    if (idx < 0) continue;
    const left = line.slice(0, idx);
    const value = line.slice(idx + 1);
    const [prop, ...paramParts] = left.split(";");
    const params = Object.fromEntries(
      paramParts.map((p) => { const [k, v] = p.split("="); return [k, v]; })
    );
    switch (prop) {
      case "SUMMARY": cur.title = unescapeText(value).trim(); break;
      case "DESCRIPTION": cur.description = unescapeText(value); break;
      case "LOCATION": cur.location = unescapeText(value).trim(); break;
      case "URL": cur.url = value.trim(); break;
      case "UID": cur.uid = value.trim(); break;
      case "GEO": {
        const [lat, lon] = value.split(";").map(Number);
        if (Number.isFinite(lat) && Number.isFinite(lon)) { cur.lat = lat; cur.lon = lon; }
        break;
      }
      case "DTSTART": cur.start = { value, params }; break;
      case "DTEND": cur.end = { value, params }; break;
      case "ORGANIZER": {
        const cn = params.CN ? unescapeText(params.CN) : null;
        if (cn) cur.organizer = cn;
        break;
      }
    }
  }
  return events;
}

/** Convert a wall-clock time in an IANA timezone to a UTC Date. */
export function zonedTimeToUtc(y, mo, d, h, mi, s, tz) {
  let utc = Date.UTC(y, mo - 1, d, h, mi, s);
  // Two passes converge across DST boundaries.
  for (let i = 0; i < 2; i++) {
    const parts = Object.fromEntries(
      new Intl.DateTimeFormat("en-US", {
        timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit",
        hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
      }).formatToParts(new Date(utc)).map((p) => [p.type, p.value])
    );
    const asIf = Date.UTC(+parts.year, +parts.month - 1, +parts.day,
      parts.hour === "24" ? 0 : +parts.hour, +parts.minute, +parts.second);
    utc -= asIf - Date.UTC(y, mo - 1, d, h, mi, s);
  }
  return new Date(utc);
}

/** Parse a DTSTART/DTEND into {iso, allDay}. fallbackTz applies to floating times. */
export function parseIcsDate(dt, fallbackTz) {
  if (!dt) return null;
  const { value, params = {} } = dt;
  if (params.VALUE === "DATE" || /^\d{8}$/.test(value)) {
    const y = +value.slice(0, 4), mo = +value.slice(4, 6), d = +value.slice(6, 8);
    const tz = params.TZID || fallbackTz || "UTC";
    return { iso: zonedTimeToUtc(y, mo, d, 0, 0, 0, tz).toISOString(), allDay: true };
  }
  const m = value.match(/^(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})(Z?)$/);
  if (!m) return null;
  const [, y, mo, d, h, mi, s, z] = m;
  if (z === "Z") return { iso: new Date(Date.UTC(+y, +mo - 1, +d, +h, +mi, +s)).toISOString(), allDay: false };
  const tz = params.TZID || fallbackTz || "UTC";
  return { iso: zonedTimeToUtc(+y, +mo, +d, +h, +mi, +s, tz).toISOString(), allDay: false };
}

// ------------------------------------------------------------------ fetching

async function fetchText(url) {
  const res = await fetch(url, { headers: { "User-Agent": UA, "Accept": "text/calendar, text/html, application/json, */*" }, redirect: "follow" });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.text();
}

/** Resolve a lu.ma calendar slug to candidate ICS feed URLs (best first),
 *  plus a diagnostic string describing how resolution went. */
async function lumaIcsCandidates(slug) {
  const candidates = [];
  let diag = "";
  try {
    const html = await fetchText(`https://lu.ma/${slug}`);
    // Prefer the explicit api_id field; otherwise rank every cal- id on the
    // page by frequency (calendar pages embed their own id many times).
    const exact = html.match(/"api_id"\s*:\s*"(cal-[A-Za-z0-9]+)"/);
    const counts = new Map();
    for (const m of html.matchAll(/cal-[A-Za-z0-9]{6,}/g))
      counts.set(m[0], (counts.get(m[0]) || 0) + 1);
    const ranked = [...counts.entries()].sort((a, b) => b[1] - a[1]).map((e) => e[0]);
    if (exact) ranked.unshift(exact[1]);
    for (const id of [...new Set(ranked)].slice(0, 3))
      candidates.push(`https://api.lu.ma/ics/get?entity=calendar&id=${id}`);
    if (!candidates.length) diag = `page https://lu.ma/${slug} loaded but contains no calendar id`;
  } catch (err) {
    diag = `page https://lu.ma/${slug} failed: ${String(err.message || err).slice(0, 80)}`;
  }
  candidates.push(`https://api.lu.ma/ics/get?entity=calendar&id=${slug}`);
  return { candidates, diag };
}

/** Fetch the first candidate URL that answers with an iCal payload. */
async function fetchFirstIcs(urls) {
  const errors = [];
  for (const url of urls) {
    try {
      const raw = await fetchText(url);
      if (/BEGIN:VCALENDAR/.test(raw)) return raw;
      errors.push(`${url}: not an iCal feed`);
    } catch (err) {
      errors.push(String(err.message || err).slice(0, 100));
    }
  }
  throw new Error(errors.join(" | "));
}

// ------------------------------------------------------------------ geocoding

function loadJson(path, fallback) {
  try { return JSON.parse(readFileSync(path, "utf8")); } catch { return fallback; }
}

const geocachePath = join(DATA, "geocache.json");
const geocache = loadJson(geocachePath, {});
let geocodeCount = 0;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function geocode(location) {
  const key = location.toLowerCase().replace(/\s+/g, " ").trim();
  if (key in geocache) return geocache[key];
  if (geocodeCount >= MAX_GEOCODES_PER_RUN) return null;
  geocodeCount++;
  try {
    await sleep(1100); // Nominatim usage policy: max 1 req/sec
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(location)}`,
      { headers: { "User-Agent": UA } }
    );
    const json = res.ok ? await res.json() : [];
    const hit = json[0] ? { lat: +json[0].lat, lon: +json[0].lon } : null;
    geocache[key] = hit;
    return hit;
  } catch {
    return null;
  }
}

const R_EARTH_MI = 3958.8;
export function milesBetween(a, b) {
  const rad = (x) => (x * Math.PI) / 180;
  const dLat = rad(b.lat - a.lat), dLon = rad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * R_EARTH_MI * Math.asin(Math.sqrt(h));
}

// ----------------------------------------------------------------- validation

/** In-person check: a real street-address-looking LOCATION, not a meeting link. */
export function looksInPerson(location) {
  if (!location) return false;
  if (VIRTUAL_RE.test(location)) return false;
  if (/^https?:\/\//i.test(location)) return false;
  // Address-ish: contains letters plus either a digit or a comma-separated part.
  return /[A-Za-z]/.test(location) && (/\d/.test(location) || location.includes(","));
}

// ----------------------------------------------------------------------- main

async function processSource(source, market, marketKey, out, skipGeocode) {
  const status = {
    market: marketKey, name: source.name, url: source.url || "",
    type: source.type, aic: !!source.aic, status: "ok", count: 0,
    lastChecked: new Date().toISOString(), note: source.note || "",
  };
  out.sources.push(status);
  if (source.enabled === false) { status.status = "needs-setup"; return; }
  if (source.type === "manual") { status.status = "manual"; return; }

  try {
    let raw, diag = "";
    if (source.type === "luma-calendar") {
      const resolved = await lumaIcsCandidates(source.slug);
      diag = resolved.diag;
      try {
        raw = await fetchFirstIcs(resolved.candidates);
      } catch (err) {
        throw new Error([diag, String(err.message || err)].filter(Boolean).join(" | "));
      }
    } else {
      raw = await fetchText(source.url);
      if (!/BEGIN:VCALENDAR/.test(raw)) throw new Error("not an iCal feed");
    }
    const now = Date.now();
    const min = now - WINDOW_PAST_DAYS * 864e5;
    const max = now + WINDOW_FUTURE_DAYS * 864e5;

    for (const ev of parseIcs(raw)) {
      const start = parseIcsDate(ev.start, market?.tz);
      if (!start) continue;
      const t = Date.parse(start.iso);
      if (!(t >= min && t <= max)) continue;
      if (!ev.title) continue;
      if (!looksInPerson(ev.location)) continue; // validated in-person only

      const text = `${ev.title}\n${ev.description || ""}`;
      if (!source.assumeAI && !AI_RE.test(text)) continue; // AI-related only

      const url = ev.url || source.url;
      if (!trustedHost(url)) continue; // must link to a live, trusted listing

      const end = parseIcsDate(ev.end, market?.tz);
      let lat = ev.lat, lon = ev.lon;
      if ((lat == null || lon == null) && !skipGeocode) {
        const g = await geocode(ev.location);
        if (g) ({ lat, lon } = g);
      }
      // Market-scoped sources: drop events geocoded outside the market radius.
      if (market && lat != null && lon != null &&
          milesBetween({ lat, lon }, market.center) > (market.radiusMiles || 50) + 15) continue;
      // Global sources need coordinates to be searchable by city.
      if (!market && (lat == null || lon == null)) continue;

      out.events.push({
        id: (ev.uid || `${source.name}-${ev.title}-${start.iso}`).slice(0, 120),
        title: ev.title,
        start: start.iso,
        end: end?.iso || null,
        allDay: start.allDay,
        tz: market?.tz || null,
        location: ev.location,
        lat: lat ?? null,
        lon: lon ?? null,
        organizer: source.organizer || ev.organizer || source.name,
        url,
        sourceDomain: new URL(url).hostname.replace(/^www\./, ""),
        aic: !!source.aic,
        type: classify(text),
        price: priceOf(text),
        capacity: capacityOf(text),
        market: marketKey,
      });
      status.count++;
    }
  } catch (err) {
    status.status = "error";
    status.note = String(err.message || err).slice(0, 200);
  }
}

function mergeManualEvents(out) {
  const manual = loadJson(join(DATA, "manual-events.json"), { events: [] });
  for (const ev of manual.events || []) {
    if (!ev.title || !ev.start || !ev.url) continue;
    if (!trustedHost(ev.url)) continue;
    if (!looksInPerson(ev.location)) continue;
    out.events.push({
      price: "check", capacity: null, aic: false, type: "meetup",
      allDay: false, end: null, tz: null, lat: null, lon: null,
      sourceDomain: new URL(ev.url).hostname.replace(/^www\./, ""),
      id: `manual-${ev.title}-${ev.start}`.slice(0, 120),
      market: "manual",
      ...ev,
    });
  }
}

function dedupe(events) {
  const seen = new Map();
  for (const ev of events) {
    const key = `${ev.title.toLowerCase().replace(/\s+/g, " ").trim()}|${ev.start.slice(0, 10)}`;
    const prev = seen.get(key);
    // Prefer market-scoped entries over global duplicates.
    if (!prev || (prev.market === "global" && ev.market !== "global")) seen.set(key, ev);
  }
  return [...seen.values()].sort((a, b) => a.start.localeCompare(b.start));
}

async function main() {
  const skipGeocode = process.argv.includes("--no-geocode");
  const cfg = JSON.parse(readFileSync(join(DATA, "sources.json"), "utf8"));
  const out = { generatedAt: new Date().toISOString(), sample: false, markets: {}, sources: [], events: [] };

  for (const [key, market] of Object.entries(cfg.markets || {})) {
    out.markets[key] = { label: market.label, center: market.center, radiusMiles: market.radiusMiles || 50, tz: market.tz };
    for (const source of market.sources || []) {
      await processSource(source, market, key, out, skipGeocode);
    }
  }
  for (const source of cfg.global || []) {
    await processSource(source, null, "global", out, skipGeocode);
  }
  mergeManualEvents(out);
  out.events = dedupe(out.events);

  writeFileSync(join(DATA, "events.json"), JSON.stringify(out, null, 2));
  writeFileSync(geocachePath, JSON.stringify(geocache, null, 2));
  console.log(`Wrote ${out.events.length} validated in-person events from ${out.sources.length} sources.`);
  for (const s of out.sources) console.log(`  [${s.status}] ${s.name}: ${s.count} events ${s.note ? "— " + s.note : ""}`);
}

// ------------------------------------------------------------------ self-test

function selfTest() {
  const fixture = [
    "BEGIN:VCALENDAR",
    "BEGIN:VEVENT",
    "UID:test-1",
    "SUMMARY:AI Demo Night — Test",
    "DESCRIPTION:Free to attend. Capacity: 150. Live demos of LLM agents.",
    "LOCATION:Atlanta Tech Village\\, 3423 Piedmont Rd NE\\, Atlanta\\, GA",
    "DTSTART;TZID=America/New_York:20260801T180000",
    "DTEND;TZID=America/New_York:20260801T203000",
    "URL:https://lu.ma/test",
    "END:VEVENT",
    "BEGIN:VEVENT",
    "UID:test-2",
    "SUMMARY:Virtual webinar (should fail in-person check)",
    "LOCATION:https://zoom.us/j/123",
    "DTSTART:20260802T170000Z",
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");

  const events = parseIcs(fixture);
  const assert = (cond, msg) => { if (!cond) { console.error("FAIL:", msg); process.exit(1); } };
  assert(events.length === 2, "parses two VEVENTs");
  assert(events[0].title === "AI Demo Night — Test", "summary parsed");
  assert(events[0].location.includes("Atlanta Tech Village, 3423"), "location unescaped");
  const d = parseIcsDate(events[0].start, "America/New_York");
  assert(d.iso === "2026-08-01T22:00:00.000Z", `TZID converted to UTC (got ${d.iso})`);
  const z = parseIcsDate(events[1].start, null);
  assert(z.iso === "2026-08-02T17:00:00.000Z", "Z time passthrough");
  assert(looksInPerson(events[0].location) === true, "address passes in-person check");
  assert(looksInPerson(events[1].location) === false, "zoom link fails in-person check");
  assert(classify(events[0].title) === "demo night", "classified as demo night");
  assert(priceOf(events[0].description) === "free", "price detected as free");
  assert(capacityOf(events[0].description) === 150, "capacity detected");
  assert(Math.abs(milesBetween({ lat: 33.749, lon: -84.388 }, { lat: 33.846, lon: -84.366 }) - 6.8) < 1.5, "haversine sane");
  console.log("Self-test passed: parser, validation, classification, pricing, capacity, distance.");
}

if (process.argv.includes("--self-test")) selfTest();
else main();
