/* ============================================================ VIBE NIGHT ============================================================
   Vibe Night mode: same GIF every month (only date, time, venue repainted), the standard Vibe Night deck
   (GIF swapped in, What's Next filled in), and the standard Luma copy.
   Assets (base GIF, deck template, fonts, GIF/zip libs) are injected by scripts/build-vibe-night.py. */
(function(){
  "use strict";
  const A = window.VN_ASSETS || {};
  const LS = "wsb_vibenight_v1";
  const BG = [13,6,37];
  const W_TEXT = "#FCFCFC";
  const VENUES = {
    sandy:   {label:"Sandy Springs", line:"Hudson Grille · Sandy Springs, GA", city:"Sandy Springs"},
    midtown: {label:"Midtown",       line:"Hudson Grille · Midtown Atlanta, GA", city:"Midtown"},
    other:   {label:"Other",         line:"", city:""}
  };
  const DEFAULT_COPY = [
    "Dine. Vibe. Learn. Connect.",
    "You've heard the term vibe coding. Maybe you know exactly what it means. Maybe you don't... yet. Either way, tonight you're doing it. And you're leaving with an app you actually built.",
    "Here's what's happening",
    "Think of an app you always wanted to create. Could be anything from a game to a personal health tracker. Desktop and/or mobile. Now you can literally talk this app into existence.",
    "With the AI Collective Atlanta organizing team on hand to help, you'll use your favorite AI chatbot: ChatGPT, Claude, Gemini, Grok Bot, Manus, right in your browser to Vibe code a working app > your idea, built tonight.",
    "BRING YOUR LAPTOP with your favorite AI's. Free accounts are fine. Phones can be used too, but refinements usually require a laptop or desktop.",
    "No coding experience needed. Just your laptop and your idea that you will work on during Vibe Night.",
    "Because Atlanta's AI scene is worth tapping into, we'll have some time for everyone to introduce themselves to the group.",
    "Before you arrive, think about:",
    "→ What app have you always wished existed?",
    "→ What would you want an agent to do for you?",
    "Half-baked ideas welcome. That's what tonight is for.\nIf you finish your app or agent on time, we'd love to have everyone share what they built.",
    "One more thing. The moment you register, you become a member of AI Collective. No fees, no forms, no secret handshake. Just show up and you're in.",
    "Your dinner's on you. Hudson Grille's menu has something for everyone. They are letting us use their room if we show them a little love. Bring your laptop and appetite. Leave with something great.",
    "We will provide guidance and demos, then your members of the AI Collective Organizing team will be on hand to guide you along.",
    "FREE REGISTRATION! FREE PARKING!",
    "DINNER IS ON YOU. 2-ITEM MINIMUM ORDER (Beverage and sandwich, entree, salad, or appetizer)",
    "As always, engaging conversation, and incredible company will all be provided!",
    "Please be advised: Unfortunately, space is very limited at these community events and we can not always accept everyone we would like to. If you are not accepted to this event, please keep applying! We appreciate your application tremendously and we are looking forward to seeing you at a future event very soon!",
    "The AI Collective is a global non-profit building the human layer for the AI era. We unite 511,000+ leaders, builders, and stakeholders across 300+ chapters in 75 countries to democratize the frontier, build trust, and coordinate how society navigates the rapid acceleration of technological progress.",
    "All attendees and organizers at events affiliated with The AI Collective agree to our privacy policy and are subject to our code of conduct."
  ].join("\n\n");

  function defaults(){
    return { venue:"sandy", venueLine:VENUES.sandy.line, city:"Sandy Springs", date:"", start:"18:00", end:"20:30",
      theme:"", nextVN:"Sandy Springs: 1st Tuesday every month. Midtown: 3rd Tuesday every month. Watch your inbox.",
      ev1n:"", ev1d:"", ev2n:"", ev2d:"", ev3n:"", ev3d:"", ev4n:"", ev4d:"", copy:DEFAULT_COPY, tab:"luma" };
  }
  let S = defaults();
  try{ const s=JSON.parse(localStorage.getItem(LS)||"{}"); S=Object.assign(S,s); }catch(e){}
  const save = ()=>{ try{ localStorage.setItem(LS, JSON.stringify(S)); }catch(e){} };
  let customGif = null;          // Uint8Array of an uploaded replacement GIF (this session only)
  let lastGif = null;            // {key, bytes, url}

  /* ---------- helpers ---------- */
  const $q = s=>document.querySelector(s);
  const mk = (t,c,txt)=>{ const e=document.createElement(t); if(c) e.className=c; if(txt!=null) e.textContent=txt; return e; };
  const note = m=>{ try{ toast(m); }catch(e){} };
  function b64(s){ const bin=atob(s); const u=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i); return u; }
  const MONTHS=["January","February","March","April","May","June","July","August","September","October","November","December"];
  const DAYS=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
  function parseDate(d){ if(!d) return null; const [y,m,dd]=d.split("-").map(Number); return new Date(y,m-1,dd); }
  function dateLine(){ const d=parseDate(S.date); return d ? DAYS[d.getDay()]+", "+MONTHS[d.getMonth()]+" "+d.getDate()+", "+d.getFullYear() : ""; }
  function fmtT(t){ if(!t) return ""; let [h,m]=t.split(":").map(Number); const pm=h>=12; h=h%12||12; return h+":"+String(m).padStart(2,"0")+(pm?" PM":" AM"); }
  function timeLine(){ const a=fmtT(S.start), b=fmtT(S.end); if(!a) return "";
    const sa=a.slice(-2), sb=b.slice(-2); return b ? (sa===sb ? a.slice(0,-3)+" – "+b : a+" – "+b) : a; }
  function venueLine(){ return S.venue==="other" ? (S.venueLine||"") : VENUES[S.venue].line; }
  function city(){ return S.venue==="other" ? (S.city||"") : VENUES[S.venue].city; }
  function fileStem(){ const d=parseDate(S.date); return "VibeNight_"+(city()||"Event").replace(/[^A-Za-z0-9]+/g,"")+(d?"_"+MONTHS[d.getMonth()].slice(0,3)+d.getDate():""); }
  function lumaTitle(){ return "Vibe Night"+(S.theme.trim()?" with "+S.theme.trim():"")+(city()?" in "+city():"")+" (w/ The AI Collective)"; }
  function lumaText(){ return lumaTitle()+"\n\n"+(dateLine()?dateLine()+"\n":"")+(timeLine()?timeLine()+"\n":"")+(venueLine()?venueLine()+"\n":"")+"\n"+S.copy; }

  // Save a file: inside Claude use the downloads capability, elsewhere a normal browser download.
  async function deliverFile(name, blob){
    if(window.claude && typeof window.claude.use==="function"){
      let dl=null; try{ dl=await window.claude.use("downloads"); }catch(e){}
      if(dl){
        try{ await dl.save({filename:name, data:blob}); note("Saved "+name); return; }
        catch(e){ if(e && e.code==="declined"){ note("Save cancelled"); return; }
                  if(e && e.code==="rate_limited"){ note("Another save is open. Try again in a moment."); return; } }
      }
    }
    const u=URL.createObjectURL(blob); const a=document.createElement("a"); a.href=u; a.download=name;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(u),4000); note("Downloaded "+name);
  }
  window.__deliverFile = deliverFile;

  /* ---------- fonts ---------- */
  let fontsReady=null;
  function loadFonts(){
    if(fontsReady) return fontsReady;
    fontsReady=(async()=>{
      const p=new FontFace("VNPoppins","url(data:font/woff2;base64,"+A.poppins+")",{weight:"700"});
      const c=new FontFace("VNCarlito","url(data:font/woff2;base64,"+A.carlito+")",{weight:"700"});
      await Promise.all([p.load(),c.load()]); document.fonts.add(p); document.fonts.add(c);
    })();
    return fontsReady;
  }

  /* ---------- GIF ---------- */
  // Erase the old date/time/venue text and the calendar icon, keep everything else exactly.
  const TEXT_BOX={x0:140,x1:962,y0:950,y1:1132};
  const CAL_BOX={x0:86,x1:134,y0:952,y1:1002};
  function buildEraseMask(rgba,W){
    const {x0,x1,y0,y1}=TEXT_BOX, w=x1-x0, h=y1-y0, m=new Uint8Array(w*h);
    for(let y=0;y<h;y++) for(let x=0;x<w;x++){ const i=((y+y0)*W+(x+x0))*4;
      if(Math.max(rgba[i],rgba[i+1],rgba[i+2])>60) m[y*w+x]=1; }
    const r=3, out=new Uint8Array(w*h);
    for(let y=0;y<h;y++) for(let x=0;x<w;x++){ if(!m[y*w+x]) continue;
      for(let dy=-r;dy<=r;dy++){ const yy=y+dy; if(yy<0||yy>=h) continue;
        for(let dx=-r;dx<=r;dx++){ const xx=x+dx; if(xx<0||xx>=w) continue; out[yy*w+xx]=1; } } }
    return out;
  }
  function drawOverlay(W,H){
    const cv=document.createElement("canvas"); cv.width=W; cv.height=H; const g=cv.getContext("2d");
    g.fillStyle=W_TEXT; g.textBaseline="alphabetic";
    g.font="700 30px VNPoppins"; g.fillText(dateLine(),151,986);
    g.font="700 38px VNCarlito"; g.fillText(timeLine(),150,1051); g.fillText(venueLine(),150,1114);
    // calendar icon with the real month and day
    const d=parseDate(S.date), x=92, y=958, w=36, h=36, r=4;
    g.save(); g.beginPath(); g.roundRect ? g.roundRect(x,y,w,h,r) : g.rect(x,y,w,h); g.clip();
    g.fillStyle="#FFFFFF"; g.fillRect(x,y,w,h); g.fillStyle="#F67317"; g.fillRect(x,y,w,12); g.restore();
    g.fillStyle="#1A1A1A"; g.beginPath(); g.arc(x+9,y+2,2.2,0,7); g.arc(x+27,y+2,2.2,0,7); g.fill();
    if(d){ g.textAlign="center"; g.fillStyle="#FFFFFF"; g.font="700 9px VNPoppins"; g.fillText(MONTHS[d.getMonth()].slice(0,3).toUpperCase(),x+w/2,y+10);
      g.fillStyle="#111111"; g.font="700 19px VNPoppins"; g.fillText(String(d.getDate()),x+w/2,y+32); }
    return g.getImageData(0,0,W,H).data;
  }
  function blend(dst,ov,W,box){
    for(let y=box.y0;y<box.y1;y++) for(let x=box.x0;x<box.x1;x++){ const i=(y*W+x)*4, a=ov[i+3];
      if(!a) continue; const k=a/255; dst[i]=ov[i]*k+dst[i]*(1-k); dst[i+1]=ov[i+1]*k+dst[i+1]*(1-k); dst[i+2]=ov[i+2]*k+dst[i+2]*(1-k); dst[i+3]=255; }
  }
  async function makeGif(onProgress){
    const key=[S.date,S.start,S.end,venueLine(),customGif?customGif.length:0].join("|");
    if(lastGif && lastGif.key===key) return lastGif;
    if(!dateLine()) throw new Error("Pick a date first");
    await loadFonts();
    const L=window.VNLib, src=customGif||b64(A.gif);
    const gif=L.parseGIF(src.buffer.slice(src.byteOffset, src.byteOffset+src.byteLength));
    const frames=L.decompressFrames(gif,true), W=gif.lsd.width, H=gif.lsd.height;
    const comp=new Uint8ClampedArray(W*H*4); for(let i=0;i<comp.length;i+=4){ comp[i]=BG[0]; comp[i+1]=BG[1]; comp[i+2]=BG[2]; comp[i+3]=255; }
    const out=[]; let mask=null; const ov=drawOverlay(W,H);
    for(let fi=0;fi<frames.length;fi++){
      const f=frames[fi], {left,top,width,height}=f.dims; const saved=f.disposalType===3?comp.slice():null;
      for(let y=0;y<height;y++) for(let x=0;x<width;x++){ const s=(y*width+x)*4; if(f.patch[s+3]===0) continue;
        const d=((y+top)*W+(x+left))*4; comp[d]=f.patch[s]; comp[d+1]=f.patch[s+1]; comp[d+2]=f.patch[s+2]; comp[d+3]=255; }
      const fr=comp.slice();
      if(!mask) mask=buildEraseMask(fr,W);
      const tw=TEXT_BOX.x1-TEXT_BOX.x0;
      for(let y=TEXT_BOX.y0;y<TEXT_BOX.y1;y++) for(let x=TEXT_BOX.x0;x<TEXT_BOX.x1;x++){
        if(!mask[(y-TEXT_BOX.y0)*tw+(x-TEXT_BOX.x0)]) continue; const i=(y*W+x)*4; fr[i]=BG[0]; fr[i+1]=BG[1]; fr[i+2]=BG[2]; }
      for(let y=CAL_BOX.y0;y<CAL_BOX.y1;y++) for(let x=CAL_BOX.x0;x<CAL_BOX.x1;x++){ const i=(y*W+x)*4; fr[i]=BG[0]; fr[i+1]=BG[1]; fr[i+2]=BG[2]; }
      blend(fr,ov,W,{x0:CAL_BOX.x0,x1:TEXT_BOX.x1,y0:TEXT_BOX.y0,y1:TEXT_BOX.y1});
      out.push({data:fr, delay:f.delay||80});
      if(f.disposalType===2){ for(let y=0;y<height;y++) for(let x=0;x<width;x++){ const d=((y+top)*W+(x+left))*4; comp[d]=BG[0]; comp[d+1]=BG[1]; comp[d+2]=BG[2]; comp[d+3]=255; } }
      else if(saved) comp.set(saved);
      if(fi%4===0){ onProgress&&onProgress(0.4*fi/frames.length); await new Promise(r=>setTimeout(r,0)); }
    }
    // one shared palette from a sample of frames, then encode every frame with it
    const step=2, sw=Math.floor(W/step), sh=Math.floor(H/step), picks=[0,12,24,36].filter(i=>i<out.length);
    const sample=new Uint8ClampedArray(sw*sh*4*picks.length); let o=0;
    picks.forEach(pi=>{ const d=out[pi].data; for(let y=0;y<sh;y++) for(let x=0;x<sw;x++){ const i=((y*step)*W+x*step)*4; sample[o++]=d[i]; sample[o++]=d[i+1]; sample[o++]=d[i+2]; sample[o++]=255; } });
    // 255 real colors plus one reserved slot: after frame 1, unchanged pixels are written as transparent
    const palette=L.quantize(sample,255); while(palette.length<255) palette.push([0,0,0]);
    const TI=255; palette.push([0,0,0]);
    const enc=L.GIFEncoder(); let prev=null;
    for(let i=0;i<out.length;i++){
      const idx=L.applyPalette(out[i].data,palette.slice(0,255));
      if(prev){ const d=new Uint8Array(idx.length); for(let k=0;k<idx.length;k++) d[k]= idx[k]===prev[k] ? TI : idx[k];
        enc.writeFrame(d,W,H,{delay:out[i].delay,transparent:true,transparentIndex:TI,dispose:1}); }
      else enc.writeFrame(idx,W,H,{palette,delay:out[i].delay,repeat:0,dispose:1});
      prev=idx; out[i].data=null;
      if(i%2===0){ onProgress&&onProgress(0.4+0.6*i/out.length); await new Promise(r=>setTimeout(r,0)); }
    }
    enc.finish(); const bytes=enc.bytes();
    if(lastGif&&lastGif.url) URL.revokeObjectURL(lastGif.url);
    lastGif={key, bytes, url:URL.createObjectURL(new Blob([bytes],{type:"image/gif"}))};
    onProgress&&onProgress(1);
    return lastGif;
  }

  /* ---------- deck ---------- */
  const xmlEsc=s=>String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  async function makeDeck(onProgress){
    const g=await makeGif(p=>onProgress&&onProgress(p*0.8));
    const zip=await window.VNLib.JSZip.loadAsync(b64(A.pptx));
    let p22=null, x=null;
    for(const name of Object.keys(zip.files)){ if(!/^ppt\/slides\/slide\d+\.xml$/.test(name)) continue;
      const t=await zip.file(name).async("string"); if(t.indexOf("{{NEXT_VN}}")>=0){ p22=name; x=t; break; } }
    if(!p22) throw new Error("Deck template is missing the What's Next slide");
    const rep={NEXT_VN:S.nextVN};
    for(let i=1;i<=4;i++){ const n=(S["ev"+i+"n"]||"").trim(), d=(S["ev"+i+"d"]||"").trim();
      rep["EV"+i+"_NAME"]=n; rep["EV"+i+"_DETAILS"]=d; rep["EV"+i+"_SEP"]=(n&&d)?"  \u00b7  ":""; }
    Object.keys(rep).forEach(k=>{ x=x.split("{{"+k+"}}").join(xmlEsc(rep[k])); });
    zip.file(p22,x); zip.file("ppt/media/image2.gif",g.bytes);
    const blob=await zip.generateAsync({type:"blob",compression:"DEFLATE",mimeType:"application/vnd.openxmlformats-officedocument.presentationml.presentation"});
    onProgress&&onProgress(1); return blob;
  }

  /* ---------- UI ---------- */
  function field(label, input, hint){ const l=mk("label","fld"); l.appendChild(mk("span","lab",label)); l.appendChild(input); if(hint) l.appendChild(mk("div","hint",hint)); return l; }
  function inp(type,key,ph){ const i=mk(type==="textarea"?"textarea":"input"); if(type!=="textarea") i.type=type; i.value=S[key]||""; if(ph) i.placeholder=ph;
    i.oninput=()=>{ S[key]=i.value; save(); renderOut(); }; return i; }
  function section(n,title,open){ const d=mk("details","sect"); if(open) d.open=true; const s=mk("summary"); s.innerHTML='<span class="step">'+n+'</span>'+title+'<span class="chev">›</span>'; d.appendChild(s); const b=mk("div","body"); d.appendChild(b); return [d,b]; }

  function renderForm(){
    const f=$q("#vnForm"); f.innerHTML="";
    let [d,b]=section(1,"Event",true);
    const sel=mk("select"); Object.keys(VENUES).forEach(k=>{ const o=mk("option",null,VENUES[k].label); o.value=k; if(S.venue===k) o.selected=true; sel.appendChild(o); });
    sel.onchange=()=>{ S.venue=sel.value; save(); renderForm(); renderOut(); };
    b.appendChild(field("Location",sel));
    if(S.venue==="other"){ b.appendChild(field("Venue line on the graphic",inp("text","venueLine","Hudson Grille · City, GA"))); b.appendChild(field("City for the Luma title",inp("text","city","City"))); }
    b.appendChild(field("Date",inp("date","date")));
    const r=mk("div","row2"); r.appendChild(field("Starts",inp("time","start"))); r.appendChild(field("Ends",inp("time","end"))); b.appendChild(r);
    b.appendChild(field("Theme (optional)",inp("text","theme","Agents"),"Adds “with Agents” to the Luma title."));
    f.appendChild(d);
    [d,b]=section(2,"Deck: What's Next slide",false);
    b.appendChild(field("Next Vibe Night line",inp("textarea","nextVN")));
    b.appendChild(field("Upcoming event 1",inp("text","ev1n","Event name"))); b.appendChild(inp("text","ev1d","Date, time – place"));
    b.appendChild(field("Upcoming event 2",inp("text","ev2n","Event name"))); b.appendChild(inp("text","ev2d","Date, time – place"));
    b.appendChild(field("Upcoming event 3",inp("text","ev3n","Event name"))); b.appendChild(inp("text","ev3d","Date, time – place"));
    b.appendChild(field("Upcoming event 4",inp("text","ev4n","Event name"))); b.appendChild(inp("text","ev4d","Date, time – place"));
    f.appendChild(d);
    [d,b]=section(3,"Luma copy",false);
    const ta=inp("textarea","copy"); ta.style.minHeight="260px"; b.appendChild(field("Description (kept month to month)",ta));
    const rs=mk("button","btn sm ghost","Restore the standard copy"); rs.onclick=()=>{ S.copy=DEFAULT_COPY; save(); renderForm(); renderOut(); }; b.appendChild(rs);
    f.appendChild(d);
    [d,b]=section(4,"Base GIF",false);
    b.appendChild(mk("div","hint","Uses your standard Vibe Night GIF. Only the date, time, venue, and calendar icon change. Upload a different 1200 × 1200 GIF here only if the design itself changes."));
    const up=mk("input"); up.type="file"; up.accept="image/gif"; up.onchange=async()=>{ const fl=up.files[0]; if(!fl) return; customGif=new Uint8Array(await fl.arrayBuffer()); lastGif=null; note("Using "+fl.name+" for this session"); renderOut(); };
    b.appendChild(up);
    f.appendChild(d);
  }
  function progressBtn(label, run){
    const wrap=mk("div"); const btn=mk("button","btn primary",label); btn.style.cssText="font-size:15px;padding:12px 18px";
    const bar=mk("div","vn-bar"); const fill=mk("i"); bar.appendChild(fill); bar.hidden=true;
    btn.onclick=async()=>{ btn.disabled=true; bar.hidden=false; fill.style.width="0%";
      try{ await run(p=>{ fill.style.width=Math.round(p*100)+"%"; }); }catch(e){ note((e&&e.message)||String(e)); }
      btn.disabled=false; bar.hidden=true; };
    wrap.appendChild(btn); wrap.appendChild(bar); return wrap;
  }
  function head(title, sub){ const h=mk("div","out-head"); const b=mk("div"); b.appendChild(mk("h2",null,title)); if(sub) b.appendChild(mk("div","sub",sub)); h.appendChild(b); return h; }
  function renderTabsVN(){
    const t=$q("#vnTabs"); t.innerHTML="";
    [["luma","Luma Page"],["gif","Graphic (GIF)"],["deck","PowerPoint"]].forEach(([id,lab])=>{
      const b=mk("button","tab"); b.innerHTML='<span class="dot"></span>'+lab; if(S.tab===id) b.setAttribute("data-on","1");
      b.onclick=()=>{ S.tab=id; save(); renderTabsVN(); renderOut(); }; t.appendChild(b); });
  }
  function renderOut(){
    const o=$q("#vnOut"); if(!o) return; o.innerHTML="";
    if(S.tab==="luma"){
      const h=head("Luma Event Page","Title, then the description. Date, time, and venue go in Luma's own fields."); const sp=mk("div","sp");
      const c1=mk("button","btn sm","Copy title"); c1.onclick=()=>copyIt(lumaTitle());
      const c2=mk("button","btn sm","Copy description"); c2.onclick=()=>copyIt(S.copy);
      sp.appendChild(c1); sp.appendChild(c2); h.appendChild(sp); o.appendChild(h);
      const d=mk("div","doc md"); const t=mk("h4",null,lumaTitle()); d.appendChild(t);
      const meta=[dateLine(),timeLine(),venueLine()].filter(Boolean).join("  ·  "); if(meta) d.appendChild(mk("p","muted",meta));
      S.copy.split(/\n{2,}/).forEach(p=>d.appendChild(mk("p",null,p))); o.appendChild(d);
    } else if(S.tab==="gif"){
      o.appendChild(head("Luma Graphic","Your standard Vibe Night GIF with this month's date, time, and venue. 1200 × 1200, 48 frames."));
      const d=mk("div","doc"); d.style.maxWidth="640px";
      if(!dateLine()) d.appendChild(mk("p","hint","Pick a date in step 1 first."));
      d.appendChild(progressBtn("Make the GIF", async(p)=>{ const g=await makeGif(p); renderOut(); }));
      if(lastGif){ const img=mk("img"); img.src=lastGif.url; img.alt="Vibe Night graphic preview"; img.className="vn-prev"; d.appendChild(img);
        const dl=mk("button","btn","⬇  Download GIF"); dl.onclick=()=>deliverFile(fileStem()+".gif", new Blob([lastGif.bytes],{type:"image/gif"})); d.appendChild(dl); }
      o.appendChild(d);
    } else {
      o.appendChild(head("Vibe Night Deck","Your 23-slide deck. The GIF on slide 1 and both Vibe Time slides and the What's Next slide update. Everything else stays as is."));
      const d=mk("div","doc"); d.style.maxWidth="640px";
      if(!dateLine()) d.appendChild(mk("p","hint","Pick a date in step 1 first."));
      d.appendChild(progressBtn("⬇  Build and download PowerPoint (.pptx)", async(p)=>{ const blob=await makeDeck(p); await deliverFile(fileStem()+".pptx", blob); }));
      d.appendChild(mk("div","hint","Builds the GIF first if needed, then the deck. Takes about 10 to 20 seconds on a phone."));
      o.appendChild(d);
    }
  }
  function copyIt(t){ try{ if(typeof copyText==="function") return copyText(t); }catch(e){} navigator.clipboard&&navigator.clipboard.writeText(t).then(()=>note("Copied")); }

  /* ---------- mode switch ---------- */
  const MODE_KEY="wsb_mode_v1";
  function setMode(m){
    try{ localStorage.setItem(MODE_KEY,m); }catch(e){}
    const vn=m==="vn";
    document.querySelector(".main").hidden=vn; $q("#vnApp").hidden=!vn;
    ["#genBtn","#resetBtn"].forEach(s=>{ const e=$q(s); if(e) e.hidden=vn; });
    document.querySelectorAll("#modeSw button").forEach(b=>b.setAttribute("data-on", b.dataset.mode===m?"1":"0"));
    const h1=document.querySelector(".brand h1"); if(h1) h1.innerHTML = vn ? 'Workshop Builder<span>Vibe Night - Atlanta</span>' : 'Workshop Builder<span>AI Fundamentals for Professionals - Atlanta</span>';
    if(vn){ renderForm(); renderTabsVN(); renderOut(); }
  }
  document.querySelectorAll("#modeSw button").forEach(b=>b.onclick=()=>setMode(b.dataset.mode));
  let m0="ws"; try{ m0=localStorage.getItem(MODE_KEY)||"ws"; }catch(e){}
  setMode(m0);
})();
