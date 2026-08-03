/**
 * AIC Sponsorship Studio — reporting web app (Google Apps Script).
 *
 * Receives events from the Studio, logs every one to a Google Sheet, and emails
 * the team on chapter setup and whenever a proposal is created (with details).
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
 * To change who gets notified, edit NOTIFY below and redeploy
 * (Deploy -> Manage deployments -> edit -> new version).
 */

var NOTIFY = ['mark@aicollective.com', 'erich@aicollective.com'];

function doGet() {
  return _json({ ok: true, service: 'AIC Sponsorship Studio reporting' });
}

function doPost(e) {
  var out = { ok: true };
  try {
    var data = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    data._received = new Date().toISOString();
    _logRow(data);
    _maybeEmail(data);
  } catch (err) {
    out = { ok: false, error: String(err) };
  }
  return _json(out);
}

function _json(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}

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

function _logRow(d) {
  _sheet().appendRow([
    d._received || '', d.event || '', d.chapter || '', d.region || '',
    _refName(d), d.sponsor || '', d.amount || '', d.proposalNo || '',
    d.lang || '', JSON.stringify(d)
  ]);
}

function _maybeEmail(d) {
  var ev = d.event || '';
  if (ev !== 'setup' && ev !== 'proposal') return; // usage pings are logged, not emailed
  var subject, lines = [];
  if (ev === 'setup') {
    subject = 'AIC Studio set up: ' + (d.chapter || 'a chapter');
    lines.push((d.chapter || 'A chapter') + ' configured the Sponsorship Studio.');
  } else {
    subject = 'AIC proposal created: ' + (d.sponsor || 'sponsor') +
      (d.chapter ? ' — ' + d.chapter : '');
    lines.push('A new sponsorship proposal was created.');
  }
  lines.push('');
  lines.push('Event: ' + ev);
  if (d.chapter) lines.push('Chapter: ' + d.chapter);
  if (d.region) lines.push('Region: ' + d.region);
  if (d.sponsor) lines.push('Sponsor: ' + d.sponsor);
  if (d.amount) lines.push('Amount: ' + d.amount);
  if (d.proposalNo) lines.push('Proposal #: ' + d.proposalNo);
  if (_refName(d)) {
    lines.push('Referred by: ' + _refName(d) +
      (_refEmail(d) ? ' <' + _refEmail(d) + '>' : ''));
  }
  if (d.items) lines.push('\nLine items:\n' + d.items);
  lines.push('\n— AIC Sponsorship Studio');
  MailApp.sendEmail(NOTIFY.join(','), subject, lines.join('\n'));
}
