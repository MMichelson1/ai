#!/usr/bin/env python3
"""One-time update (Oct 28, 2026): Lovable joins the core tools, NotebookLM is renamed Notebook.

- Adds a `lovable` use-case list to every built-in audience (Problem -> what you build in Lovable)
- Moves Lovable into the core tool group, maps it to the new `lovable` field
- Adds Lovable to the workbook prompt kit (generated from the audience's first Lovable use case)
- Renames "NotebookLM" and "Gemini Notebook" to "Notebook" everywhere the user sees it,
  and migrates saved workshops that used the old names
Safe to re-run: it checks before each change.
"""
import json, os, re, sys
IDX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
s = open(IDX, encoding="utf-8").read()

LOVABLE = {
 "Consultants & Solopreneurs": ["Clients ask for a status update every week → a simple client portal with project status and next steps","Proposals go out as plain documents → a one-page proposal site with scope, timeline, and price","Leads come in from everywhere → a lead tracker you can open on your phone"],
 "Small Business Owners": ["Customers call with the same questions → a small website with hours, services, and an FAQ","Bookings live in texts and sticky notes → a booking form that drops every request into one list","Inventory gets counted on paper → a phone-friendly inventory checklist"],
 "Qualitative Research Professionals": ["Screeners live in long email threads → a screener form that scores and sorts respondents","Findings get buried in long reports → an insights site clients can click through","Field schedules live in five calendars → one fieldwork calendar for the whole team"],
 "Customer Experience Professionals": ["VOC lives in spreadsheets → a dashboard of top themes by journey stage","Journey maps sit in a slide deck → a clickable journey map the whole company can use","Closing the loop with customers is manual → a follow-up tracker for detractors"],
 "Community Builders & Managers": ["Members can't find past events → a member hub with events, recordings, and resources","Volunteer sign-ups happen in DMs → a sign-up page with roles and dates","Engagement is tracked from memory → an attendance tracker that flags members you haven't seen lately"],
 "Marketing Professionals": ["Every campaign needs a landing page → a campaign page with a signup form, built in an hour","The content calendar lives in five places → one shared content calendar app","Leadership keeps asking how campaigns are doing → a simple results dashboard from your exports"],
 "HR & People Operations Leaders": ["New hires ask the same first-week questions → an onboarding portal with checklists and contacts","Interview feedback is scattered → a structured interview scorecard","Policy questions flood your inbox → a searchable policy FAQ site"],
 "Conference Organizers": ["Speakers send their details by email → a speaker intake form that builds the agenda page","Attendees can't find the schedule → a mobile agenda site with rooms and times","Sponsor benefits live in a spreadsheet → a sponsor deliverables tracker"],
 "Sales Professionals": ["Call prep is scattered across tabs → a one-screen account brief before every call","Your pipeline lives in your head → a simple personal pipeline tracker on your phone","Prospects want a price fast → a quote calculator page you can share"],
 "Nonprofit Leaders": ["Volunteers sign up by email → a volunteer sign-up page with shifts","Donors want to see the impact → an impact page with stories and numbers","Program data lives in spreadsheets → an intake form and a simple dashboard for staff"],
 "Healthcare Administrators": ["Staff can't find forms and policies → an internal resource hub","Shift swaps happen in group texts → a shift swap request board","Patients ask the same prep questions → a plain-language visit prep page"],
 "Real Estate Professionals": ["Every listing needs its own page → a single-property site with photos and a showing form","Buyers lose track of the homes they saw → a shared showing tracker with notes","Clients ask what they can afford → a simple affordability calculator"],
 "Financial Advisors": ["Clients ask the same planning questions → a retirement scenario calculator page","Review prep pulls from many files → a client review checklist app","Prospects need a reason to book → a short quiz that leads to a booking form"],
 "Product Designers": ["Static mockups don't feel real → a clickable working prototype stakeholders can try","Design system docs live in slides → a living component reference site","Usability test notes pile up → a session notes tracker tagged by issue"],
 "Product Managers": ["Feature requests come from everywhere → a request intake form with voting","Specs are hard to picture → a working prototype to test the idea before engineering builds it","Roadmap questions every week → a simple roadmap page"],
 "Customer Success": ["Account health lives in your notes → a health dashboard for your book of accounts","Onboarding steps go out by email → a customer onboarding checklist portal","QBR data takes days to gather → a QBR summary page per account"],
 "Legal Professionals": ["Clients keep asking for status → a simple matter status page","Intake questions repeat every time → a client intake form that flags what to check","Deadlines are tracked by hand → a deadline tracker with reminders"],
 "SMB": ["Requests come in by text, email, and phone → one request form that lands in one list","Jobs and schedules live on a whiteboard → a team job board on everyone's phone","Customers want quotes fast → an instant quote calculator page"],
 "Enterprise Teams": ["Status reports take hours → a team status page everyone updates in two minutes","Nobody knows who owns what → an internal who-does-what directory","AI ideas come from everywhere → an AI idea intake and review board"],
 "Founders": ["You need a page to test an idea → a landing page with a waitlist, live today","Investors ask for your metrics → a simple metrics page from your spreadsheet","Your MVP is still a slide → a first working version users can try"],
 "Retail Design": ["Store concepts are hard to picture → a clickable store walkthrough","Rollout tasks live in email → a store rollout tracker by location","Brand standards sit in a PDF → a searchable brand standards site"],
 "Merchandising": ["Line reviews need the same slides every time → a category scorecard dashboard","Planogram changes get lost → a planogram change log for stores","Vendor follow-ups slip → a vendor commitment tracker"],
 "Customer Service": ["Reps hunt for answers → a searchable answer library for the team","Customers ask the same five questions → a self-service help page","Complaints never reach the fix → a complaint log with owners and status"],
 "Customer Support": ["Troubleshooting lives in senior people's heads → a step-by-step troubleshooting guide","Escalations arrive without detail → an escalation form engineers actually like","Status questions flood the queue → a simple service status page"],
 "Mystery Shopping": ["Shopper applications arrive by email → a shopper application and screening form","Clients want results faster → a client results dashboard by location","Assigning shops is manual → a shop assignment board"],
 "CX Design": ["Journey maps are hard to share → a clickable journey map site","Service blueprints stay in the workshop room → a living blueprint page teams can browse","Workshop ideas get lost → an idea board with owners and votes"],
 "CX Management": ["Executives skip long reports → a one-screen CX scorecard","Fixes stall across teams → a CX action tracker with owners and dates","VOC themes change every week → a theme trend page from your survey exports"],
}

def once(old, new, label, count=1):
    global s
    if new in s or old not in s: return  # already applied
    if s.count(old) != count: sys.exit("anchor mismatch: %s (%d)" % (label, s.count(old)))
    s = s.replace(old, new)

# 1. lovable use cases per audience, after each notebooklm line
if "\n    lovable:[" not in s:
    def add(m):
        block_start = s.rfind('\n  "', 0, m.start())
        name = re.match(r'\n  "([^"]+)"', s[block_start:]).group(1)
        if name not in LOVABLE: sys.exit("no Lovable cases for " + name)
        return m.group(0) + "    lovable:" + json.dumps(LOVABLE[name], ensure_ascii=False) + ",\n"
    s2 = re.sub(r'\n    notebooklm:\[[^\n]*\],?\n', add, s)
    if s2.count("\n    lovable:[") != len(LOVABLE): sys.exit("lovable insert count off")
    s = s2

# 2. fields, merge, tool groups, tool kinds
once('const UC_FIELDS = ["claude","gemini","perplexity","notebooklm","cowork"];',
     'const UC_FIELDS = ["claude","gemini","perplexity","notebooklm","cowork","lovable"];', "UC_FIELDS")
once('["pains","winning","tools","claude","gemini","perplexity","notebooklm","cowork"].forEach(',
     '["pains","winning","tools","claude","gemini","perplexity","notebooklm","cowork","lovable"].forEach(', "merge")
once('{cat:"Core LLMs", tools:["Claude Code","Claude Chat","ChatGPT","Gemini"]},',
     '{cat:"Core LLMs", tools:["Claude Code","Claude Chat","ChatGPT","Gemini","Lovable"]},', "core")
once('{cat:"App & Agent Builders", tools:["Claude Artifacts","Lovable","Bolt","Replit"]},',
     '{cat:"App & Agent Builders", tools:["Claude Artifacts","Bolt","Replit"]},', "builders")
once('"Lovable":["builder",null]', '"Lovable":["builder","lovable"]', "kind")

# 3. ICP editor: Lovable use cases box, and tolerate older saved audiences without the field
once('      grid.appendChild(fld("Cowork use cases",',
     '      grid.appendChild(fld("Lovable use cases", ta((icp.lovable||[]).join("\\n"), v=>{icp.lovable=splitLines(v); persistIcp(); rerenderOut();}), null));\n      grid.appendChild(fld("Cowork use cases",', "editor")
once('      state.icp=JSON.parse(JSON.stringify(ov)); return;',
     '      if(!ov.lovable && ICP[name]){ ov.lovable=JSON.parse(JSON.stringify(ICP[name].lovable||[])); saveStore(s); }\n      state.icp=JSON.parse(JSON.stringify(ov)); return;', "override lovable")

# 4. workbook prompt kit: Lovable as a sixth tool, generated from the first Lovable use case when a kit lacks it
once('const KIT_TOOLS = ["Claude","Perplexity","NotebookLM","Gemini","Claude Cowork"];',
     'const KIT_TOOLS = ["Claude","Perplexity","NotebookLM","Gemini","Claude Cowork","Lovable"];', "kit tools")
once('"Claude Cowork":"cowork"};', '"Claude Cowork":"cowork","Lovable":"lovable"};', "kit field")
once('  "Claude Cowork":{sources:"The files in [folder path].", stop:"Stop and show me the result before sending, moving, or deleting anything."}\n};',
     '  "Claude Cowork":{sources:"The files in [folder path].", stop:"Stop and show me the result before sending, moving, or deleting anything."},\n  "Lovable":      {sources:"Describe who will use it and what it should show. Paste a sample of your data or a screenshot of what you use today.", stop:"Stop at a first working version I can click through. Ask me questions if anything is unclear. Don\'t guess."}\n};', "kit default")
once('''function promptKitFor(){
  const p=PROMPT_KIT[primaryName()], s=state.audience2?PROMPT_KIT[state.audience2]:null;
  if(p && s){ const pick=(k,i)=>(i%2?s:p).find(x=>x.tool===k)||p.find(x=>x.tool===k); return KIT_TOOLS.map(pick).filter(Boolean); }
  if(p) return p;
  const icp=state.icp||freshIcp(state.audience), noun=audNoun(), kit=[];
  KIT_TOOLS.forEach(t=>{''', '''function promptKitFor(){
  const p=PROMPT_KIT[primaryName()], s=state.audience2?PROMPT_KIT[state.audience2]:null;
  let base=null;
  if(p && s){ const pick=(k,i)=>(i%2?s:p).find(x=>x.tool===k)||p.find(x=>x.tool===k); base=KIT_TOOLS.map(pick).filter(Boolean); }
  else if(p) base=p.slice();
  const icp=state.icp||freshIcp(state.audience), noun=audNoun(), kit=base||[];
  KIT_TOOLS.forEach(t=>{
    if(kit.some(x=>x.tool===t)) return;''', "kit fn")

# 5. rename NotebookLM / Gemini Notebook -> Notebook (identifiers stay lowercase `notebooklm`)
if "function renameOldTools" not in s:
    s = s.replace("Gemini Notebook", "Notebook").replace("NotebookLM", "Notebook")

# 6. migrate saved workshops that used the old tool names
once('function applyWorkshop(cfg){\n  WORKSHOP_FIELDS.forEach(k=>{ if(k in cfg && cfg[k]!=null) state[k]=JSON.parse(JSON.stringify(cfg[k])); });',
     '''function renameOldTools(){
  const map={"Gemini Notebook":"Notebook","NotebookLM":"Notebook"};
  if(state.include) Object.keys(map).forEach(o=>{ if(o in state.include){ state.include[map[o]]=state.include[o]; delete state.include[o]; } });
  if(Array.isArray(state.deep)) state.deep=state.deep.map(t=>map[t]||t);
}
function applyWorkshop(cfg){
  WORKSHOP_FIELDS.forEach(k=>{ if(k in cfg && cfg[k]!=null) state[k]=JSON.parse(JSON.stringify(cfg[k])); });
  renameOldTools();''', "migrate")

open(IDX, "w", encoding="utf-8").write(s)
print("ok", "lovable lists:", s.count("\n    lovable:["), "Notebook mentions:", s.count("Notebook"), "NotebookLM left:", s.count("NotebookLM"))
