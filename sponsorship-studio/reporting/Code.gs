/**
 * AIC Sponsorship Studio — reporting web app (Google Apps Script).
 *
 * Receives events from the Studio, logs every one to a Google Sheet, keeps a
 * per-chapter Summary (hits vs. wins vs. $ won), and emails the team on chapter
 * setup, each new proposal, each invoice sent, and — most important — each WIN
 * (payment received).
 *
 * SETUP (about 5 minutes):
 *   1. Create a new Google Sheet (it will hold the log). Name it e.g.
 *      "AIC Sponsorship Studio — Activity".
 *   2. In that Sheet: Extensions -> Apps Script. Delete the sample code,
 *      paste THIS file, and Save.
 *   3. Deploy -> New deployment -> gear icon -> "Web app".
 *        Description: AIC Studio reporting
 *        Execute as:  Me
 *        Who has access: Anyone
 *      Click Deploy, authorize when prompted, and COPY the Web app URL
 *      (it ends in "/exec").
 *   4. Send that /exec URL back so it can be set as the Studio's REPORT_ENDPOINT.
 *
 * REDEPLOYING after an edit (e.g. you pasted this newer version):
 *   Deploy -> Manage deployments -> (pencil/edit) -> Version: New version -> Deploy.
 *   The /exec URL stays the same, so nothing changes in the Studio.
 *
 * To change who gets notified, edit NOTIFY below and redeploy.
 */

var NOTIFY = ['mark@aicollective.com', 'erich@aicollective.com'];

// HQ passcode — unlocks READING every chapter's clients (for you / Erich / an HQ
// dashboard). CHANGE THIS to a strong phrase before deploying, and keep it private.
// Chapter leads never need it; they use their own chapter passcode.
var HQ_PASS = 'CHANGE-ME-HQ-PASSCODE';

// Which set of books THIS deployment is. Deploy this file TWICE, each bound to
// its OWN Google Sheet, so commercial and non-profit money is never commingled:
//   Sheet 1 "AIC Sponsorship - Commercial"  -> STREAM = 'commercial'
//   Sheet 2 "AIC Sponsorship - Non-profit"  -> STREAM = 'nonprofit'
// An event tagged for the other stream is rejected rather than written here.
var STREAM = 'commercial';

// Commissions exist only on the commercial side.
function _commissionable() { return STREAM === 'commercial'; }

function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.action === 'listClients') {
    var res;
    var lock = LockService.getScriptLock();
    try { lock.waitLock(15000); } catch (ignore) {}
    try { res = _listClients(p.chapter || '', p.pass || ''); }
    catch (err) { res = { ok: false, error: String(err) }; }
    finally { try { lock.releaseLock(); } catch (ignore) {} }
    return _jsonp(p.callback, res);
  }
  if (p.action === 'salesSummary') {           // Sponsor Sales Dashboard (HQ only)
    var out;
    try { out = _salesSummary(p.pass || ''); }
    catch (err2) { out = { ok: false, error: String(err2) }; }
    return _jsonp(p.callback, out);
  }
  return _json({ ok: true, service: 'AIC Sponsorship Studio reporting', stream: STREAM });
}

function doPost(e) {
  var out = { ok: true };
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000); // serialize writes so rows/summary never collide
  } catch (lockErr) {
    // Couldn't get the lock in time — still try to log, best-effort.
  }
  try {
    var data = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    if (data.action === 'saveClients') {          // CRM sync (push), not an event
      out = _saveClients(data);
      return _json(out);
    }
    // Never write another stream's money into this book.
    if (data.stream && data.stream !== STREAM) {
      return _json({ ok: false, error: 'wrong book: this deployment is ' + STREAM +
        ', event was tagged ' + data.stream });
    }
    data._received = new Date().toISOString();
    data.stream = STREAM;
    _logRow(data);
    _updateSummary(data);
    _maybeEmail(data);
  } catch (err) {
    out = { ok: false, error: String(err) };
  } finally {
    try { lock.releaseLock(); } catch (ignore) {}
  }
  return _json(out);
}

function _json(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}

// JSONP: reads from a browser on another origin can't use plain fetch against an
// Apps Script web app, so the Studio requests clients via a <script> tag and we
// reply with `callback({...})`.
function _jsonp(cb, obj) {
  cb = String(cb || 'callback').replace(/[^A-Za-z0-9_$]/g, '') || 'callback';
  return ContentService.createTextOutput(cb + '(' + JSON.stringify(obj) + ');')
    .setMimeType(ContentService.MimeType.JAVASCRIPT);
}

/* ---------- Clients (CRM sync) ----------
   Two tabs:
     Clients     — one row per client: Chapter | Client ID | Updated | JSON
     ChapterKeys — one row per chapter: Chapter | Passcode | Region | Created
   A chapter's passcode gates that chapter's clients. HQ_PASS reads any chapter
   (or chapter '*' for everything). This is lightweight gating, not encryption —
   passcodes and client data live in the Sheet in plain text. */

function _clientsSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('Clients');
  if (!sh) {
    sh = ss.insertSheet('Clients');
    sh.appendRow(['Chapter', 'Client ID', 'Updated', 'JSON']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function _chapterKeysSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('ChapterKeys');
  if (!sh) {
    sh = ss.insertSheet('ChapterKeys');
    sh.appendRow(['Chapter', 'Passcode', 'Region', 'Created (UTC)']);
    sh.setFrozenRows(1);
  }
  return sh;
}

// Returns {ok, hq} or {ok:false, error}. allowCreate registers a new chapter's
// passcode the first time it syncs.
function _verifyPass(chapter, pass, allowCreate, region) {
  if (pass && pass === HQ_PASS) return { ok: true, hq: true };
  if (!chapter) return { ok: false, error: 'missing chapter' };
  if (!pass) return { ok: false, error: 'missing passcode' };
  var sh = _chapterKeysSheet();
  var vals = sh.getDataRange().getValues();
  for (var i = 1; i < vals.length; i++) {
    if (String(vals[i][0]) === String(chapter)) {
      return String(vals[i][1]) === String(pass)
        ? { ok: true, hq: false }
        : { ok: false, error: 'wrong passcode for ' + chapter };
    }
  }
  if (allowCreate) {
    sh.appendRow([chapter, pass, region || '', new Date().toISOString()]);
    return { ok: true, hq: false, created: true };
  }
  return { ok: false, error: 'unknown chapter (nothing synced yet)' };
}

function _saveClients(data) {
  var chapter = data.chapter || '';
  var list = data.clients || [];
  var region = '';
  for (var k = 0; k < list.length; k++) { if (list[k].chapter) region = list[k].region || region; }
  var v = _verifyPass(chapter, data.pass || '', true, region);
  if (!v.ok) return v;
  if (v.hq) return { ok: false, error: 'HQ passcode is read-only; save with the chapter passcode' };
  var sh = _clientsSheet();
  var vals = sh.getDataRange().getValues();
  var index = {}; // "chapter|id" -> { row: 1-based, updated: stored timestamp }
  for (var r = 1; r < vals.length; r++) {
    index[String(vals[r][0]) + '\u001f' + String(vals[r][1])] = { row: r + 1, updated: String(vals[r][2] || '') };
  }
  var saved = 0, skipped = 0;
  for (var j = 0; j < list.length; j++) {
    var cl = list[j];
    if (!cl || !cl.id) continue;
    var ch = cl.chapter || chapter;
    var key = ch + '\u001f' + cl.id;
    var inc = String(cl.updated || '');
    var row = [ch, cl.id, inc, JSON.stringify(cl)];
    var ex = index[key];
    if (ex) {
      // Newest edit wins: a stale push must not clobber a newer server record.
      if (inc >= ex.updated) { sh.getRange(ex.row, 1, 1, 4).setValues([row]); saved++; }
      else skipped++;
    } else {
      sh.appendRow(row); saved++;
    }
  }
  return { ok: true, saved: saved, skipped: skipped };
}

function _listClients(chapter, pass) {
  var v = _verifyPass(chapter === '*' ? '' : chapter, pass, false);
  if (chapter === '*') { if (!v.hq) return { ok: false, error: 'HQ passcode required for all-chapter read' }; }
  else if (!v.ok) return v;
  var sh = _clientsSheet();
  var vals = sh.getDataRange().getValues();
  var clients = [];
  for (var r = 1; r < vals.length; r++) {
    if (chapter === '*' || String(vals[r][0]) === String(chapter)) {
      try { clients.push(JSON.parse(vals[r][3])); } catch (e) {}
    }
  }
  return { ok: true, clients: clients, server: new Date().toISOString() };
}

// Sponsor Sales Dashboard data (HQ only): per-chapter hits/wins from the Summary
// tab, each tagged with its region so the dashboard can roll up by region.
function _salesSummary(pass) {
  if (!pass || pass !== HQ_PASS) return { ok: false, error: 'HQ passcode required' };
  var sh = _summarySheet();
  var vals = sh.getDataRange().getValues();
  var rows = [];
  for (var r = 1; r < vals.length; r++) {
    var v = vals[r];
    if (!v[0]) continue;
    rows.push({
      chapter: String(v[0] || ''),
      region: String(v[1] || ''),
      proposals: Number(v[2]) || 0,
      invoices: Number(v[3]) || 0,
      wins: Number(v[4]) || 0,
      won: Number(v[5]) || 0,
      lastActivity: String(v[7] || '')
    });
  }
  return { ok: true, rows: rows, stream: STREAM, commissionable: _commissionable(), server: new Date().toISOString() };
}

/* ---------- Events tab (append-only log of everything) ---------- */

function _sheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('Events');
  if (!sh) {
    sh = ss.insertSheet('Events');
    sh.appendRow(['Received (UTC)', 'Event', 'Chapter', 'Region', 'Referred by',
      'Sponsor', 'Amount', 'Proposal #', 'Language', 'Details (JSON)']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function _refName(d) {
  return (d.referredBy && d.referredBy.name) || d.referredByName || '';
}
function _refEmail(d) {
  return (d.referredBy && d.referredBy.email) || d.referredByEmail || '';
}

function _amountNum(d) {
  // Prefer an explicit numeric amount; else strip non-digits from the display amount.
  if (typeof d.amountNum === 'number' && !isNaN(d.amountNum)) return d.amountNum;
  var n = parseFloat(String(d.amount || '').replace(/[^0-9.\-]/g, ''));
  return isNaN(n) ? 0 : n;
}

function _logRow(d) {
  _sheet().appendRow([
    d._received || '', d.event || '', d.chapter || '', d.region || '',
    _refName(d), d.sponsor || '', d.amount || '', d.proposalNo || '',
    d.lang || '', JSON.stringify(d)
  ]);
}

/* ---------- Summary tab (one row per chapter: hits vs. wins) ---------- */

function _summarySheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('Summary');
  if (!sh) {
    sh = ss.insertSheet('Summary');
    sh.appendRow(['Chapter', 'Region', 'Proposals (hits)', 'Invoices sent',
      'Wins (paid)', '$ Won', 'Win rate', 'Last activity (UTC)']);
    sh.setFrozenRows(1);
  }
  return sh;
}

function _updateSummary(d) {
  var ev = d.event || '';
  // Only these events move the hits/wins counters.
  if (ev !== 'proposal' && ev !== 'invoice' && ev !== 'payment') return;
  var chapter = d.chapter || '(unknown)';
  var sh = _summarySheet();
  var values = sh.getDataRange().getValues();
  var rowIdx = -1;
  for (var i = 1; i < values.length; i++) {
    if (String(values[i][0]) === String(chapter)) { rowIdx = i; break; }
  }
  var row;
  if (rowIdx === -1) {
    row = [chapter, d.region || '', 0, 0, 0, 0, '', ''];
  } else {
    row = values[rowIdx].slice();
    if (!row[1] && d.region) row[1] = d.region;
  }
  var props = Number(row[2]) || 0;
  var invs = Number(row[3]) || 0;
  var wins = Number(row[4]) || 0;
  var won = Number(row[5]) || 0;
  if (ev === 'proposal') props++;
  if (ev === 'invoice') invs++;
  if (ev === 'payment') { wins++; won += _amountNum(d); }
  row[2] = props;
  row[3] = invs;
  row[4] = wins;
  row[5] = won;
  row[6] = props ? Math.round((wins / props) * 100) + '%' : '';
  row[7] = d._received || new Date().toISOString();
  if (rowIdx === -1) {
    sh.appendRow(row);
  } else {
    sh.getRange(rowIdx + 1, 1, 1, row.length).setValues([row]);
  }
}

/* ---------- Email notifications ---------- */

function _maybeEmail(d) {
  var ev = d.event || '';
  // Logged-only events (no email): usage pings.
  if (ev !== 'setup' && ev !== 'proposal' && ev !== 'invoice' && ev !== 'payment') return;
  var subject, lines = [];
  if (ev === 'setup') {
    subject = 'AIC Studio set up: ' + (d.chapter || 'a chapter');
    lines.push((d.chapter || 'A chapter') + ' configured the Sponsorship Studio.');
  } else if (ev === 'proposal') {
    subject = 'AIC proposal created: ' + (d.sponsor || 'sponsor') +
      (d.chapter ? ' — ' + d.chapter : '');
    lines.push('A new sponsorship proposal was created.');
  } else if (ev === 'invoice') {
    subject = 'AIC invoice sent: ' + (d.sponsor || 'sponsor') +
      (d.chapter ? ' — ' + d.chapter : '');
    lines.push('An invoice was marked as sent.');
  } else { // payment — a WIN
    subject = '🎉 AIC WIN — payment received: ' + (d.sponsor || 'sponsor') +
      (d.chapter ? ' — ' + d.chapter : '');
    lines.push('A sponsorship was WON — payment received. 🎉');
  }
  lines.push('');
  lines.push('Book: ' + (STREAM === 'nonprofit' ? 'NON-PROFIT (501c3) \u2014 no commission payable' : 'COMMERCIAL'));
  lines.push('Event: ' + ev);
  if (d.chapter) lines.push('Chapter: ' + d.chapter);
  if (d.region) lines.push('Region: ' + d.region);
  if (d.sponsor) lines.push('Sponsor: ' + d.sponsor);
  if (d.amount) lines.push('Amount: ' + d.amount);
  if (d.date) lines.push('Date: ' + d.date);
  if (d.proposalNo) lines.push('Proposal #: ' + d.proposalNo);
  if (_refName(d)) {
    lines.push('Referred by: ' + _refName(d) +
      (_refEmail(d) ? ' <' + _refEmail(d) + '>' : ''));
  }
  if (d.items) lines.push('\nLine items:\n' + d.items);
  lines.push('\nSee the Summary tab for this chapter\'s hits vs. wins.');
  lines.push('\n— AIC Sponsorship Studio');
  MailApp.sendEmail(NOTIFY.join(','), subject, lines.join('\n'));
}
