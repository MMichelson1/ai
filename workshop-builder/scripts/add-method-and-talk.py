#!/usr/bin/env python3
"""Add "The way of thinking" and "Talk it through" to the workshop builder (repeatable).

- METHODS: a thinking framework per audience (stages, case studies, who it is for and not for).
  Ships with the Marketing Strategy framework: From Problem To Purchase.
- The framework becomes a deck section, a workbook section, Luma and LinkedIn lines, and a
  4-week Maven outline. It is a Session focus topic that can be switched off, and every part
  of it can be edited in the form.
- "Talk it through": type or dictate a ramble about the workshop. Inside Claude, the page asks
  Claude (sample capability) to turn it into the setup. Anywhere else, copy the prompt to Claude
  and paste the answer back.
"""
import sys, pathlib

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
s = p.read_text()
if "const METHODS" in s:
    print("already applied"); sys.exit(0)

def sub(a, b):
    global s
    n = s.count(a)
    assert n == 1, (a[:90], n)
    s = s.replace(a, b)

# ---------------------------------------------------------------- data + helpers
METHODS_JS = r'''
/* ============================================================ THE WAY OF THINKING ============================================================
   A thinking framework per audience: the stages the room walks through, with the questions each stage answers
   and where AI helps, plus case studies and who the session is (and is not) for. It drives a deck section, a
   workbook section, Luma and LinkedIn lines, and the Maven outline. Edit it in Session focus, or build it by
   talking it through. */
const METHODS = {
  "Marketing Strategy Professionals": {
    title:"From Problem To Purchase",
    label:"Marketing Strategy",
    subtitle:"Find the problem. Own the position. Help them buy.",
    pitch:"Most marketing starts with the product and goes looking for buyers. This workshop starts where great marketing does, with a real customer problem. You learn the fundamentals of marketing and of AI side by side, and use AI at every step.",
    isFor:"Marketing directors, marketing consultants, and founders or business owners who are new to marketing. The focus is B2B. Most of it works for B2C too.",
    isNot:"This is not a digital marketing or analytics class. We won't tune ad dashboards or chase a score. Measurement comes after the fact. We talk about what sits behind the numbers.",
    intro:[
      "Two ways in: an idea looking for a problem, or a real problem you found by listening",
      "Start with the problem, then test the idea against it",
      "Every need pulls one of two ways: toward something people want, or away from something that hurts",
      "Toward: more profit, growth, a good time. Away: a cost, lost customers, a daily headache"
    ],
    stages:[
      {name:"Explore and uncover problems", questions:["What are people struggling with right now?","Is it a real problem, or one we made up?","Where do you hear about it: talking to people, reading, events, your own field?"], ai:"Perplexity scans news, forums, and groups. Notebook reads interviews and reviews for repeated complaints."},
      {name:"Understand the motivation", questions:["What emotion sits behind the problem?","How urgent is it, and what happens if it isn't solved?","Are they moving toward a gain or away from pain?"], ai:"Claude pulls the emotions, urgency, and best quotes out of your interview notes."},
      {name:"Learn how they cope today", questions:["What have they tried before?","What stopgaps do they use?","What barriers block a fix?","What have competitors tried, and how is yours different?"], ai:"Notebook across your transcripts. Perplexity on competitor offers and what their customers say."},
      {name:"How to find out", questions:["Observation: watch what people actually do","Interviews: ask about the last time it happened","Ethnography: spend time in their world"], ai:"Claude drafts your discussion guide and screener. AI transcribes and codes the interviews. You still do the listening."},
      {name:"Size it", questions:["How many people or companies have this problem?","How much do they spend on it today?","Is it a want or a need?"], ai:"Perplexity finds industry reports and the groups where these people gather. Claude drafts the survey. Gemini sorts the results in Sheets."},
      {name:"Shape the solution", questions:["A product, a service, a subscription, coaching, or a shift in mindset?","A product is anything someone made, not only tech","Does it solve the problem better than what they do today?"], ai:"Claude compares solution options against the problem. Lovable builds a quick page to test demand."},
      {name:"The P's", questions:["Problem: what you solve","People: exactly who has it","Positioning: why you, and not the others","Price, place, and promotion"], ai:"Claude drafts positioning options and a price and value case."},
      {name:"Help them buy", questions:["People love to buy and hate being sold","What do they need to know at the point of sale?","How do they compare you to the alternatives?","Sell the hole, not the drill"], ai:"Claude writes the comparison, the sell sheet, and packaging copy built on the problem you solve."},
      {name:"Remove friction", questions:["What blocks the purchase: stock, shipping delays, damage, a confusing checkout?","Where on the path to purchase do people drop off?"], ai:"Claude maps the path to purchase and flags the friction points."},
      {name:"Get known", questions:["Earned: word of mouth, social posts, demos, events","Paid: ads and PR","Partners: communities and groups that win when you win"], ai:"Claude drafts a month of posts and emails in one voice. Gemini drafts follow-ups to everyone you met at an event."},
      {name:"Support after the sale", questions:["Who helps when something goes wrong?","Where does AI answer first, and where does a person step in?"], ai:"Claude drafts the FAQ and the hand-off rules for a support assistant."}
    ],
    values:"Through every stage: who do you want to help, how do you want to help them, and does it fit your values and your human mission?",
    measure:"Measurement comes last. A score tells you what happened. The work tells you why it happened and what to do about it.",
    cases:[
      {title:"The Morning Milkshake", real:true,
        story:["A fast-food chain asked customers to describe the ideal milkshake. Sales didn't move.","A researcher spent a day in one restaurant. About 40% of milkshakes sold first thing in the morning, to commuters.","Interviews showed the job: make a long, boring drive bearable and stay full until noon.","A thicker shake that lasted the drive fit that job better than any flavor change."],
        lesson:"Observation and interviews found the motivation the survey missed.",
        source:"https://www.library.hbs.edu/working-knowledge/clay-christensens-milkshake-marketing"},
      {title:"Spanx", real:true,
        story:["Sara Blakely needed to look smooth under slacks without pantyhose feet showing in sandals.","She cut the feet off her pantyhose. It worked, but the legs rolled up.","She put $5,000 of her savings into solving that one problem.","She demoed it for the Neiman Marcus buyer herself, and asked friends to request it in stores."],
        lesson:"A problem she lived herself, a demo at the point of decision, and word of mouth before paid media.",
        source:"https://en.wikipedia.org/wiki/Sara_Blakely"},
      {title:"The Calendar That Won't Sync", real:false,
        story:["A consultant notices clients keep missing meetings because Apple, Google, and Microsoft calendars don't agree.","Perplexity finds the forums and groups where people complain about it.","Claude drafts five interview questions about what it costs them and what they do today.","The room decides: real need or small annoyance? Toward gain or away from pain?"],
        lesson:"Walk one everyday problem through every stage before you build anything.", source:""},
      {title:"The Expert Finds Her Niche", real:false,
        story:["A former hospital operations director wants to consult. \"Operations consulting for healthcare\" sounds like everyone else.","She uploads ten past projects to Notebook and asks which problems she solved best, and for whom.","The answer: patient discharge delays at mid-size hospitals.","Perplexity sizes that market. Claude drafts three positions built on it."],
        lesson:"Your expertise holds your niche. Name one problem for one buyer.", source:""}
    ]
  }
};
function blankMethod(){ return {title:"",label:"",subtitle:"",pitch:"",isFor:"",isNot:"",intro:[],stages:[],values:"",measure:"",cases:[]}; }
function normMethod(m){
  const S=x=>typeof x==="string"?x.trim():"", A=x=>Array.isArray(x)?x.map(v=>String(v==null?"":v).trim()).filter(Boolean):(S(x)?[S(x)]:[]);
  const o=blankMethod(); if(!m||typeof m!=="object") return o;
  ["title","label","subtitle","pitch","isFor","isNot","values","measure"].forEach(k=>o[k]=S(m[k]));
  o.intro=A(m.intro);
  o.stages=(Array.isArray(m.stages)?m.stages:[]).filter(x=>x&&S(x.name)).map(x=>({name:S(x.name), questions:A(x.questions), ai:S(x.ai)}));
  o.cases=(Array.isArray(m.cases)?m.cases:[]).filter(x=>x&&S(x.title)).map(x=>({title:S(x.title), real:x.real===true, story:A(x.story), lesson:S(x.lesson), source:S(x.source)}));
  return o;
}
function methodFor(){
  const m = state.method || METHODS[state.audience==="__custom__"?"":primaryName()] || null;
  return (m && list(m.stages).length) ? m : null;
}
function ensureMethod(){
  if(!state.method){ const d=METHODS[state.audience==="__custom__"?"":primaryName()]; state.method = d ? JSON.parse(JSON.stringify(d)) : blankMethod(); }
  return state.method;
}

/* ============================================================ TALK IT THROUGH ============================================================
   Ramble about the workshop instead of filling every form. Inside Claude the page asks Claude directly
   (the sample capability, on the viewer's own account). Anywhere else: copy the prompt, paste the answer back. */
let _talkSample=null, talkLast=null;
function talkSample(){
  if(!_talkSample){
    _talkSample = (window.claude && typeof window.claude.use==="function") ? Promise.resolve(window.claude.use("sample")).catch(()=>null) : Promise.resolve(null);
  }
  return _talkSample;
}
function talkPrompt(){
  const cur={audience:state.audience, customName:state.customName, label:state.label, noun:state.noun, date:state.date, venue:state.venue, seats:state.seats,
    tools:Object.keys(state.include||{}).filter(k=>state.include[k]), deep:state.deep, focus:state.focus||{}, icp:state.icp, method:state.method||methodFor(), teach:state.teach};
  const schema = {
    summary:"2 or 3 plain sentences for Mark: what you set up and what you left alone",
    questions:["up to 4 short questions whose answers would make the workshop better"],
    audience:"one name from the audience list, or empty",
    customName:"only when no audience in the list fits: a short audience name",
    label:"what goes after 'AI Fundamentals for' in the title, e.g. Marketing Strategy",
    noun:"singular noun for one attendee, e.g. marketing strategist",
    date:"YYYY-MM-DD, only if he gave a date",
    venue:"only if he named a place",
    seats:"number, only if he said",
    tools:["tool names from the tool list to include this session"],
    deep:["2 to 4 of those tools to go deep on"],
    focus:{think:true,prompts:true,limits:true,agents:true,automation:true,tools:true,memd:false,graphs:false,method:true},
    icp:{titles:"comma list of job titles", pains:["..."], winning:["..."], tools:["everyday tools they already use"],
      claude:["Problem → what Claude does about it"], gemini:["same format"], perplexity:["same format"], notebooklm:["same format, for Notebook"], lovable:["same format"], cowork:["same format, for Claude Cowork"]},
    method:{title:"name of the way of thinking", label:"same as label", subtitle:"one short line", pitch:"2 or 3 sentences for the event page",
      isFor:"who it is for", isNot:"what it is not, so the wrong people don't sign up", intro:["3 or 4 short framing lines"],
      stages:[{name:"stage name", questions:["the questions this stage answers"], ai:"where AI helps at this stage, naming tools"}],
      values:"one line", measure:"one line",
      cases:[{title:"...", real:true, story:["3 or 4 short sentences"], lesson:"one line", source:"link for a real case, empty for a made-up one"}]},
    teach:{analogy:"Think of AI as ... (a machine analogy from their world)", notFor:["3 things to keep away from AI in this work"], bad:"a bad one-line prompt", agent:"A ... : one small tool to build in the room", auto:"trigger → AI step → human check → result", graph:"Connect ..., so AI can ..."}
  };
  return [
    "You help Mark Michelson set up one workshop in his AI Fundamentals workshop builder. Mark is a marketing researcher and strategist with 42 years of experience. He teaches professionals to use AI by starting from a real problem, not from the technology. The AI Collective Atlanta hosts the workshops.",
    "Below is what Mark said, in his own words, often dictated and rambling. Turn it into the workshop setup. Reply with ONLY one JSON object in the shape shown. Leave out any key you have nothing for. Arrays replace what is there now, so send whole lists.",
    "Shape:\n"+JSON.stringify(schema,null,1),
    "Rules:\n- Use what Mark said. Fill gaps only where his intent is clear, and say so in summary.\n- Never invent a date, venue, price, number, statistic, or quote.\n- Real case studies only when they are well known and documented, with a source link. Mark anything else real:false. Prefer cases Mark tells you about.\n- Plain, short sentences. No em dashes, no semicolons, no hype words, no emojis.\n- Use cases are written as a real problem, then →, then what the tool does about it.\n- The way of thinking (method) is the heart of the session: capture his process stage by stage, in his order and his words, with the questions he asks at each stage.\n- Keep everything in the current setup that he does not change.",
    "Audience list: "+AUDIENCES.join(" | "),
    "Tool list: "+Object.keys(TOOL_KIND).join(" | "),
    "Topics (focus ids): "+MODULES.filter(m=>!m.core).map(m=>m.id+" = "+m.label).join(" | "),
    "Current setup:\n"+JSON.stringify(cur),
    "What Mark said:\n"+(state.brief||"")
  ].join("\n\n");
}
function talkParse(text){
  const t=String(text||""); const a=t.indexOf("{"), b=t.lastIndexOf("}");
  if(a<0||b<=a) throw new Error("No JSON found");
  return JSON.parse(t.slice(a,b+1));
}
function applyTalk(o){
  if(!o||typeof o!=="object"||Array.isArray(o)) throw new Error("Not a setup object");
  const S=x=>typeof x==="string"?x.trim():"";
  const A=x=>Array.isArray(x)?x.map(v=>String(v==null?"":v).trim()).filter(Boolean):null;
  const before=state.audience+"|"+state.customName;
  if(S(o.audience) && AUDIENCES.indexOf(S(o.audience))>=0){
    if(state.audience!==S(o.audience)){ state.audience=S(o.audience); state.audience2=""; state.customName=""; state.label=""; state.noun=""; applyAud(); }
  } else if(S(o.customName) && !(state.audience==="__custom__" && state.customName===S(o.customName))){
    state.audience="__custom__"; state.audience2=""; state.customName=S(o.customName); state.label=""; state.noun=""; applyAud();
  }
  if(!state.audience){ state.audience="__custom__"; state.customName=S(o.label)||"Custom Audience"; applyAud(); }
  if(before!==state.audience+"|"+state.customName){ state.method=null; state.teach=null; }
  if(!state.icp) applyAud();
  if(S(o.label)) state.label=S(o.label);
  if(S(o.noun)) state.noun=S(o.noun);
  if(/^\d{4}-\d{2}-\d{2}$/.test(S(o.date))) state.date=S(o.date);
  if(S(o.venue)) state.venue=S(o.venue);
  if(+o.seats>0) state.seats=Math.round(+o.seats);
  const tl=A(o.tools);
  if(tl){ const known=tl.filter(t=>TOOL_KIND[t]); if(known.length){ state.include={}; known.forEach(t=>state.include[t]=true); } }
  const dl=A(o.deep);
  if(dl) state.deep=dl.filter(t=>state.include[t]).slice(0,4);
  if(o.focus && typeof o.focus==="object"){
    state.focus=Object.assign({}, state.focus||{});
    MODULES.forEach(m=>{ if(!m.core && typeof o.focus[m.id]==="boolean") state.focus[m.id]=o.focus[m.id]; });
  }
  if(o.icp && typeof o.icp==="object"){
    const icp=state.icp||freshIcp("");
    if(S(o.icp.titles)) icp.titles=S(o.icp.titles);
    ["pains","winning","tools"].concat(UC_FIELDS).forEach(k=>{ const a=A(o.icp[k]); if(a&&a.length) icp[k]=a; });
    UC_FIELDS.forEach(k=>{ if(!Array.isArray(icp[k])) icp[k]=[]; });
    state.icp=icp; persistIcp();
  }
  if(o.method && typeof o.method==="object"){
    const m=normMethod(o.method);
    if(m.stages.length) state.method=m;
  }
  if(o.teach && typeof o.teach==="object" && S(o.teach.analogy)){
    state.teach={analogy:S(o.teach.analogy), notFor:A(o.teach.notFor)||[], bad:S(o.teach.bad), agent:S(o.teach.agent), auto:S(o.teach.auto), graph:S(o.teach.graph)};
  }
  talkLast={summary:S(o.summary), questions:A(o.questions)||[]};
}
'''
sub("function teachFor(){", METHODS_JS + "\nfunction teachForBase(){")
sub("const lcFirst=s=>", r'''function teachFor(){
  const b=teachForBase(), t=state.teach;
  if(!t||!t.analogy) return b;
  const o=Object.assign({}, b);
  ["analogy","bad","agent","auto","graph"].forEach(k=>{ if(t[k]) o[k]=t[k]; });
  if(Array.isArray(t.notFor) && t.notFor.length) o.notFor=t.notFor.concat(b.notFor).slice(0, Math.max(3, t.notFor.length));
  return o;
}
const lcFirst=s=>''')

# ---------------------------------------------------------------- state, fields, focus topic
sub('const WORKSHOP_FIELDS=["audience",', 'const WORKSHOP_FIELDS=["method","teach","brief","audience",')
sub('const state = {\n  audience:"",', 'const state = {\n  method:null,         // the way of thinking (null = the audience default)\n  teach:null,          // teaching overrides from Talk it through\n  brief:"",            // the Talk it through ramble\n  audience:"",')
sub('  {id:"think", on:true,', '  {id:"method", on:true, label:"The way of thinking", hint:"The framework this session teaches, stage by stage, with case studies. Edit it below, or build it with Talk it through."},\n  {id:"think", on:true,')
sub('sel.onchange=()=>{ state.audience=sel.value;', 'sel.onchange=()=>{ state.audience=sel.value; state.method=null; state.teach=null;')
sub('  if(!state.audience2) return withRole(primaryName());',
    '  if(!state.audience2){ const m=methodFor(); if(m&&m.label) return m.label; return withRole(primaryName()); }')

# ---------------------------------------------------------------- deck
sub('    const p2=["context, sources, and the output you want"];',
    '    { const Mt=on("method")&&methodFor(); if(Mt) a1.push("The way of thinking - "+(Mt.title||"how we approach it")); }\n    const p2=["context, sources, and the output you want"];')
sub("  // Part 2\n", r'''  // The way of thinking (its own section, between Part 1 and Part 2)
  {
    const M=on("method")&&methodFor();
    if(M){
      S.push({kind:"section", part:"p1", accent:A.p2, subtitle:"THE WAY OF THINKING", title:M.title||"How We Approach It",
        note:(M.subtitle?M.subtitle+" ":"")+"This is the spine of tonight. Each stage is a question to answer before the next one."});
      if(list(M.intro).length) S.push({kind:"content", part:"p1", title:"Where It Starts", bullets:list(M.intro).slice(0,5),
        note:"Ask the room which way they usually start: with an idea, or with a problem they heard about. Most start with the idea."});
      { const all=list(M.stages).map((st,i)=>(i+1)+". "+st.name), per=Math.ceil(all.length/(all.length>6?3:all.length>3?2:1)), cols=[];
        for(let i=0;i<all.length;i+=per) cols.push({head:"Stages "+(i+1)+(Math.min(i+per,all.length)>i+1?(" to "+Math.min(i+per,all.length)):""), items:all.slice(i,i+per)});
      S.push({kind:"content", part:"p1", title:"The Path", subtitle:M.subtitle||"", columns:cols,
        note:"The whole path on one slide. We walk it stage by stage, and at each stage you see where AI helps and where your judgment leads."}); }
      list(M.stages).forEach((st,i)=>{
        const b=list(st.questions).slice(0,4); if(st.ai) b.push("Where AI helps: "+st.ai);
        S.push({kind:"content", part:"p1", title:(i+1)+". "+st.name, bullets:b.length?b:["Add the questions this stage answers"],
          note:"Ask the room first, then show it. Use the AI step live if there is time, on one person's real problem."});
      });
      const close=[M.values, M.measure].filter(Boolean);
      if(close.length) S.push({kind:"dark", part:"p1", title:"Through Every Stage", bullets:close,
        note:"Come back to values. Who you want to help, and how, decides every stage above."});
      list(M.cases).forEach(cs=>{
        const b=list(cs.story).slice(0,4); if(cs.lesson) b.push("The lesson: "+cs.lesson);
        S.push({kind:"content", part:"p1", title:(cs.real?"Case: ":"Practice: ")+cs.title, bullets:b,
          note:cs.real?("A real case. Source: "+(cs.source||"add the source")):"A made-up example for practice. Say so out loud, then let the room run it through the stages with AI."});
      });
    }
  }

  // Part 2
''')

# ---------------------------------------------------------------- workbook
sub("  // where AI helps: the problem-framed use cases, two per tool\n", r'''  // the way of thinking
  {
    const M=on("method")&&methodFor();
    if(M){
      body+=br+h1(M.title||"The way of thinking");
      if(M.subtitle) body+=p("<b>"+wbEsc(M.subtitle)+"</b>");
      if(list(M.intro).length) body+=ul(list(M.intro).map(wbEsc));
      body+='<table class="ct"><tr class="hd"><td>Stage</td><td>The questions it answers</td><td>Where AI helps</td></tr>'
        +list(M.stages).map((st,i)=>'<tr><td class="tk">'+(i+1)+'. '+wbEsc(st.name)+'</td><td>'+list(st.questions).map(wbEsc).join("<br>")+'</td><td>'+wbEsc(st.ai||"")+'</td></tr>').join("")+'</table>';
      if(M.values) body+=p(wbEsc(M.values));
      if(M.measure) body+=p(wbEsc(M.measure));
      body+=p("<b>Your turn:</b> write one problem you want to work on tonight, and who has it.")+'<div class="wline">&nbsp;</div><div class="wline">&nbsp;</div>';
      list(M.cases).forEach(cs=>{
        body+=h2((cs.real?"Case: ":"Practice: ")+cs.title)
          +p(list(cs.story).map(wbEsc).join(" "))
          +(cs.lesson?p("<b>The lesson:</b> "+wbEsc(cs.lesson)):"")
          +(cs.real&&cs.source?p('Source: <a href="'+wbEsc(cs.source)+'">'+wbEsc(cs.source)+'</a>'):(cs.real?"":p("<i>A made-up example for practice.</i>")));
      });
    }
  }

  // where AI helps: the problem-framed use cases, two per tool
''')

# ---------------------------------------------------------------- Luma
sub('  const pain=(list(icp.pains)[0]||"the manual work that eats your week").toLowerCase();',
    '  const pain=(list(icp.pains)[0]||"the manual work that eats your week").toLowerCase();\n  const M=focusOn("method")&&methodFor();')
sub('  out += clean("AI Fundamentals for "+aud)+"\\n";',
    '  out += clean("AI Fundamentals for "+aud)+"\\n";\n  if(M&&M.subtitle) out += clean(M.subtitle)+"\\n";')
sub('  out += clean(about)+"\\n\\n";',
    '  out += clean((M&&M.pitch)||about)+"\\n\\n";\n  if(M&&M.isFor) out += "Who It\'s For\\n"+clean(M.isFor)+"\\n\\n";\n  if(M&&M.isNot) out += "What This Is Not\\n"+clean(M.isNot)+"\\n\\n";')
sub('  ml.filter(m=>m.id!=="human").forEach(m=>learn.push(m.line));',
    '  if(M) learn.push("🧭 The path we walk together: "+list(M.stages).map(st=>st.name).join(", "));\n  ml.filter(m=>m.id!=="human").forEach(m=>learn.push(m.line));')

# ---------------------------------------------------------------- LinkedIn
sub('  const pain=(list(icp.pains)[0]||"the busywork").toLowerCase();',
    '  const pain=(list(icp.pains)[0]||"the busywork").toLowerCase();\n  const M=focusOn("method")&&methodFor();')
sub('  p += clean(event)+"\\n\\n";\n  p += "What we will cover:\\n";',
    '  p += clean(event)+"\\n\\n";\n  if(M&&M.isNot) p += clean(M.isNot)+"\\n\\n";\n  p += "What we will cover:\\n";\n  if(M) p += "→ "+clean("The path: "+list(M.stages).slice(0,6).map(st=>lcFirst(st.name)).join(", "))+"\\n";')

# ---------------------------------------------------------------- Maven
sub('  out += "=== LIGHTNING LESSON PROMO (free 30-min preview) ===\\n\\n";', r'''  {
    const M=methodFor();
    if(M){
      out += "=== "+clean(M.title||"The way of thinking").toUpperCase()+": 4-WEEK COURSE OUTLINE ===\n\n";
      if(M.subtitle) out += clean(M.subtitle)+"\n";
      if(M.isFor) out += "Who it's for: "+clean(M.isFor)+"\n";
      if(M.isNot) out += "What it is not: "+clean(M.isNot)+"\n";
      out += "\n";
      const st=list(M.stages), per=Math.max(1,Math.ceil(st.length/4));
      for(let w=0; w<4; w++){
        const g=st.slice(w*per,(w+1)*per); if(!g.length) break;
        out += "Week "+(w+1)+" - "+g.map(x=>x.name).join(", ")+"\n";
        g.forEach(x=>{ out += "  "+clean(x.name)+": "+clean(list(x.questions).map(q=>/[.?!]$/.test(q)?q:q+".").join(" "))+(x.ai?("  AI: "+clean(x.ai)):"")+"\n"; });
        out += "\n";
      }
      const cs=list(M.cases);
      if(cs.length){ out += "Case studies\n"; cs.forEach(c=>{ out += "  "+clean(c.title)+(c.real?"":" (made up, for practice)")+": "+clean(c.lesson)+"\n"; }); out += "\n"; }
    }
  }
  out += "=== LIGHTNING LESSON PROMO (free 30-min preview) ===\n\n";''')

# ---------------------------------------------------------------- form: way of thinking editor (inside Session focus)
sub('    const n=el("div","hint"); n.style.marginTop="6px";\n', r'''    // ----- the way of thinking editor -----
    {
      const box=el("div"); box.style.cssText="margin:14px 0 6px;padding:13px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm)";
      const gh=el("div","gh","The way of thinking"); gh.style.color="var(--p2)"; box.appendChild(gh);
      const M=methodFor();
      const hint=el("div","hint"); hint.style.margin="2px 0 10px";
      hint.textContent=M ? "This framework becomes its own deck section, a workbook page, lines on Luma and LinkedIn, and the Maven outline. Edit any part. Each stage line: Stage name :: questions, split with ; :: where AI helps."
                         : "No framework for this audience yet. Describe yours in Talk it through, or start one here.";
      box.appendChild(hint);
      if(!M){
        const st=el("button","btn ghost sm","Start a way of thinking");
        st.onclick=()=>{ ensureMethod(); rerenderAll(); };
        box.appendChild(st);
      }
      if(M || state.method){
        const m=()=>ensureMethod(), save=()=>{ rerenderOut(); };
        box.appendChild(fld("Name", inp(m().title, v=>{m().title=v; save();}), null));
        box.appendChild(fld("One-line promise", inp(m().subtitle, v=>{m().subtitle=v; save();}), null));
        box.appendChild(fld("Title label", inp(m().label, v=>{m().label=v; save();}), "What follows AI Fundamentals for... in the title."));
        box.appendChild(fld("Who it's for", ta(m().isFor, v=>{m().isFor=v.trim(); save();}), null));
        box.appendChild(fld("What it is not", ta(m().isNot, v=>{m().isNot=v.trim(); save();}), "Keeps the wrong people from signing up."));
        box.appendChild(fld("Event page pitch", ta(m().pitch, v=>{m().pitch=v.trim(); save();}), null));
        box.appendChild(fld("Where it starts (one per line)", ta(list(m().intro).join("\n"), v=>{m().intro=splitLines(v); save();}), null));
        const stTxt=list(m().stages).map(x=>[x.name, list(x.questions).join("; "), x.ai||""].join(" :: ")).join("\n");
        const stTa=ta(stTxt, v=>{ m().stages=splitLines(v).map(line=>{ const parts=line.split("::").map(x=>x.trim()); return {name:parts[0]||"", questions:(parts[1]||"").split(";").map(x=>x.trim()).filter(Boolean), ai:parts[2]||""}; }).filter(x=>x.name); save(); });
        stTa.rows=12; box.appendChild(fld("Stages (one per line)", stTa, "Stage name :: question; question :: where AI helps"));
        box.appendChild(fld("Values line", inp(m().values, v=>{m().values=v; save();}), null));
        box.appendChild(fld("Measurement line", inp(m().measure, v=>{m().measure=v; save();}), null));
        const csTxt=list(m().cases).map(x=>[x.title, x.real?"real":"made up", list(x.story).join(" | "), x.lesson||"", x.source||""].join(" :: ")).join("\n");
        const csTa=ta(csTxt, v=>{ m().cases=splitLines(v).map(line=>{ const q=line.split("::").map(x=>x.trim()); return {title:q[0]||"", real:/^real$/i.test(q[1]||""), story:(q[2]||"").split("|").map(x=>x.trim()).filter(Boolean), lesson:q[3]||"", source:q[4]||""}; }).filter(x=>x.title); save(); });
        csTa.rows=6; box.appendChild(fld("Case studies (one per line)", csTa, "Title :: real or made up :: story sentences split with | :: lesson :: source link"));
        if(state.method && METHODS[state.audience==="__custom__"?"":primaryName()]){
          const rs=el("button","btn ghost sm","Reset to the default for this audience");
          rs.onclick=()=>{ if(confirm("Replace your edits with the default way of thinking?")){ state.method=null; rerenderAll(); } };
          box.appendChild(rs);
        }
      }
      body.appendChild(box);
    }
    const n=el("div","hint"); n.style.marginTop="6px";
''')

# ---------------------------------------------------------------- form: Talk it through (top of the form)
sub("  // SECTION 1 - Audience\n", r'''  // ---- Talk it through ----
  f.appendChild(section("✦","Talk it through", state.brief.trim()?"Notes saved":"Say it, skip the forms", body=>{
    const intro=el("div","hint"); intro.style.margin="2px 0 8px";
    intro.innerHTML="Talk about the workshop the way you would to a colleague: who it is for, what they should leave with, your way of thinking, the stages, stories and case studies, the tools, the date and place. Ramble. On your phone, tap the mic on the keyboard to dictate. Claude fills in everything below, and you can still change any of it.";
    body.appendChild(intro);
    const tx=el("textarea"); tx.rows=9; tx.value=state.brief||""; tx.placeholder="This one is for marketing directors, consultants, and founders who are new to marketing. It is not digital marketing. It starts with finding a real problem...";
    tx.oninput=()=>{ state.brief=tx.value; };
    body.appendChild(tx);
    const row=el("div"); row.style.cssText="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px;align-items:center";
    const go=el("button","btn primary sm","Build it with Claude"); go.hidden=true;
    const stop=el("button","btn ghost sm","Stop"); stop.hidden=true;
    const cp=el("button","btn ghost sm","Copy for Claude");
    row.appendChild(go); row.appendChild(stop); row.appendChild(cp);
    body.appendChild(row);
    const status=el("div","hint"); status.style.marginTop="8px"; body.appendChild(status);
    if(talkLast && (talkLast.summary || talkLast.questions.length)){
      const res=el("div"); res.style.cssText="margin-top:10px;padding:11px 13px;background:var(--surface2);border:1px solid var(--border);border-radius:var(--radius-sm);font-size:12.5px;line-height:1.45";
      if(talkLast.summary){ const pp=el("div",null,talkLast.summary); res.appendChild(pp); }
      if(talkLast.questions.length){
        const qh=el("div",null,"To make it better, tell me:"); qh.style.cssText="margin-top:8px;font-weight:600"; res.appendChild(qh);
        const ul=el("ul"); ul.style.cssText="margin:4px 0 0 18px;padding:0"; talkLast.questions.forEach(q=>ul.appendChild(el("li",null,q))); res.appendChild(ul);
        const nh=el("div","hint","Add your answers to your notes above and build again. Claude keeps what is already set up."); res.appendChild(nh);
      }
      body.appendChild(res);
    }
    const need=()=>{ if(!(state.brief||"").trim()){ toast("Say something about the workshop first"); tx.focus(); return false; } return true; };
    cp.onclick=()=>{ if(!need()) return; copyText(talkPrompt()); status.textContent="Copied. Paste it into Claude, then paste Claude's answer below."; pasteBox.open=true; };
    let ctl=null;
    stop.onclick=()=>{ if(ctl) ctl.abort(); };
    go.onclick=async()=>{
      if(!need()) return;
      const sample=await talkSample(); if(!sample){ go.hidden=true; return; }
      ctl=new AbortController(); go.disabled=true; stop.hidden=false;
      status.textContent="Thinking it through. This can take a minute or two.";
      try{
        const o=await sample.json(talkPrompt(), {signal:ctl.signal, cache:false, onText:({text})=>{ status.textContent="Writing the setup… "+text.length+" characters so far"; }});
        applyTalk(o); rerenderAll(); toast("Workshop filled in from your notes");
      }catch(e){
        const code=(e&&e.code)||"";
        if(code==="cancelled") status.textContent="Stopped. Nothing changed.";
        else if(code==="not_granted"||code==="sampling_disabled"||code==="not_declared"||code==="capability_disabled"||code==="capability_removed"){ go.hidden=true; status.textContent="Claude isn't available on this page. Use Copy for Claude instead."; }
        else if(code==="rate_limited") status.textContent="Claude is busy or you've hit a usage limit. Try again in a bit, or use Copy for Claude.";
        else if(code==="invalid_json") status.textContent="Claude's answer didn't come back in the right shape. Try again.";
        else if(code==="prompt_too_large") status.textContent="That's a lot. Trim your notes and try again.";
        else if(code==="refused") status.textContent="Claude declined that one. Try rewording your notes.";
        else if(e && e.message && !code) status.textContent="Couldn't apply the answer: "+e.message;
        else status.textContent="Something went wrong reaching Claude. Try again, or use Copy for Claude.";
      }finally{ go.disabled=false; stop.hidden=true; ctl=null; }
    };
    talkSample().then(sm=>{ go.hidden=!sm; });
    const pasteBox=el("details"); pasteBox.style.marginTop="10px";
    const ps=el("summary",null,"Paste Claude's answer"); ps.style.cssText="cursor:pointer;font-size:12.5px;color:var(--muted)"; pasteBox.appendChild(ps);
    const pt=el("textarea"); pt.rows=5; pt.placeholder="Paste the JSON Claude gave you"; pt.style.marginTop="8px"; pasteBox.appendChild(pt);
    const ap=el("button","btn ghost sm","Apply"); ap.style.marginTop="8px";
    ap.onclick=()=>{ try{ applyTalk(talkParse(pt.value)); rerenderAll(); toast("Workshop filled in from your notes"); }catch(e){ toast("That doesn't look like Claude's setup answer"); } };
    pasteBox.appendChild(ap);
    body.appendChild(pasteBox);
  }, !state.audience));

  // SECTION 1 - Audience
''')

p.write_text(s)
print("applied")
