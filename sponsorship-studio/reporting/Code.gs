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

function doGet() {
  return _json({ ok: true, service: 'AIC Sponsorship Studio reporting' });
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
    data._received = new Date().toISOString();
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
