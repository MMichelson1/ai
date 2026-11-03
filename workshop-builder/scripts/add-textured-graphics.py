#!/usr/bin/env python3
"""Textured graphics (repeatable): clean, handcrafted Luma and 16:9 covers.

- New default style: a Threads-color background (deep, rich, or light linen) with a handmade texture
  (linen, paper, or woven) and an optional running-stitch border. No people, no cartoon scene.
- Big, clear title. Host logo (AI Collective, Stitchs, or an uploaded Threads logo) upper left.
- A logo band at the bottom: the venue, plus up to two sponsors.
- The old illustrated scene stays available as "Illustrated (old look)".
"""
import sys, pathlib

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
s = p.read_text()
if "function renderGraphicTexture" in s:
    print("already applied"); sys.exit(0)

def sub(a, b, n=1):
    global s
    c = s.count(a)
    assert c == n, (a[:90], c)
    s = s.replace(a, b)

# defaults + saved preferences
sub('artId:null, cover:true});', 'artId:null, cover:true, style:"texture", shade:"deep", texture:"linen", stitch:false, sponsors:[]});')
sub('s.gfx={series:g.series, person:g.person, partner:g.partner,', 's.gfx={series:g.series, person:g.person, partner:g.partner, style:g.style, shade:g.shade, texture:g.texture, stitch:g.stitch,')

# sponsors in the logo library
sub('    if(target==="partner"){ state.gfx.partner="upl:"+L.id; } else { state.deckLogo="upl:"+L.id; persistBrand(); }',
    '    if(target==="partner"){ state.gfx.partner="upl:"+L.id; }\n    else if(/^sponsor[12]$/.test(target)){ const i=+target.slice(-1)-1; state.gfx.sponsors=(state.gfx.sponsors||[]).slice(); state.gfx.sponsors[i]="upl:"+L.id; }\n    else { state.deckLogo="upl:"+L.id; persistBrand(); }')
sub('  if(state.gfx && state.gfx.partner==="upl:"+id) state.gfx.partner="improving";',
    '  if(state.gfx && state.gfx.partner==="upl:"+id) state.gfx.partner="improving";\n  if(state.gfx && Array.isArray(state.gfx.sponsors)) state.gfx.sponsors=state.gfx.sponsors.map(k=>k==="upl:"+id?"":k);')

# renderer
sub("async function renderGraphic(fmtKey){\n", r'''/* ---- textured style: a Threads-color ground with a handmade texture, big title, logo band ---- */
function gfxRand(seed){ let a=seed>>>0; return ()=>{ a=(a+0x6D2B79F5)>>>0; let t=a; t=Math.imul(t^(t>>>15),t|1); t^=t+Math.imul(t^(t>>>7),t|61); return ((t^(t>>>14))>>>0)/4294967296; }; }
function gfxMix(hex,toHex,t){ const a=parseInt(hex.slice(1),16), b=parseInt(toHex.slice(1),16); const ch=(x,y)=>Math.round(x+(y-x)*t); const r=ch(a>>16,b>>16), g=ch((a>>8)&255,(b>>8)&255), bl=ch(a&255,b&255); return "#"+((1<<24)+(r<<16)+(g<<8)+bl).toString(16).slice(1); }
const GFX_LINEN="#F3ECDF";
function gfxGround(){
  const g=state.gfx||{}, lead=gfxLead(), shade=g.shade||"deep";
  if(shade==="light") return {bg:GFX_LINEN, ink:GFX_INK, soft:GFX_MUTED, accent:lead.text, dark:false};
  const bg = shade==="rich" ? gfxMix(lead.c,"#000000",0.12) : gfxMix(lead.c,"#120E0A",0.62);
  return {bg, ink:"#FFFFFF", soft:"rgba(255,255,255,0.78)", accent:gfxMix(lead.c,"#FFFFFF",shade==="rich"?0.72:0.5), dark:true};
}
function gfxTexture(ctx, x0, y0, w, h, base, kind, seed){
  ctx.fillStyle=base; ctx.fillRect(x0,y0,w,h);
  const R=gfxRand(seed);
  // soft light falloff, like cloth under a lamp
  const gr=ctx.createRadialGradient(x0+w*0.3, y0+h*0.25, 0, x0+w*0.5, y0+h*0.5, Math.max(w,h)*0.8);
  gr.addColorStop(0,"rgba(255,255,255,0.07)"); gr.addColorStop(1,"rgba(0,0,0,0.16)");
  ctx.fillStyle=gr; ctx.fillRect(x0,y0,w,h);
  ctx.save(); ctx.beginPath(); ctx.rect(x0,y0,w,h); ctx.clip();
  if(kind==="linen"){
    for(let y=y0; y<y0+h; y+=3){ ctx.fillStyle=(R()<0.5?"rgba(255,255,255,":"rgba(0,0,0,")+(0.025+R()*0.045)+")"; ctx.fillRect(x0,y,w,1+(R()<0.2?1:0)); }
    for(let x=x0; x<x0+w; x+=3){ ctx.fillStyle=(R()<0.5?"rgba(255,255,255,":"rgba(0,0,0,")+(0.02+R()*0.04)+")"; ctx.fillRect(x,y0,1,h); }
    for(let i=0;i<w*h/2600;i++){ const y=y0+R()*h, x=x0+R()*w, l=20+R()*90; ctx.fillStyle="rgba(255,255,255,"+(0.03+R()*0.05)+")"; ctx.fillRect(x,y,l,1); }
  } else if(kind==="woven"){
    const c=16;
    for(let y=y0, r=0; y<y0+h; y+=c, r++){ for(let x=x0, k=0; x<x0+w; x+=c, k++){
      const horiz=((r+k)%2)===0;
      for(let i=1;i<c;i+=3){ ctx.fillStyle=(R()<0.55?"rgba(255,255,255,":"rgba(0,0,0,")+(0.03+R()*0.05)+")"; if(horiz) ctx.fillRect(x,y+i,c-1,1.4); else ctx.fillRect(x+i,y,1.4,c-1); }
      ctx.fillStyle="rgba(0,0,0,0.05)"; if(horiz) ctx.fillRect(x,y+c-1,c,1); else ctx.fillRect(x+c-1,y,1,c);
    } }
  } else {
    // handmade paper: fibers and flecks
    for(let i=0;i<w*h/900;i++){ const x=x0+R()*w, y=y0+R()*h, a=R()*Math.PI, l=6+R()*26; ctx.strokeStyle=(R()<0.6?"rgba(255,255,255,":"rgba(0,0,0,")+(0.03+R()*0.06)+")"; ctx.lineWidth=0.8+R()*0.8; ctx.beginPath(); ctx.moveTo(x,y); ctx.quadraticCurveTo(x+Math.cos(a)*l*0.5+R()*6-3, y+Math.sin(a)*l*0.5+R()*6-3, x+Math.cos(a)*l, y+Math.sin(a)*l); ctx.stroke(); }
  }
  // fine grain over everything
  for(let i=0;i<w*h/220;i++){ ctx.fillStyle=(R()<0.5?"rgba(255,255,255,":"rgba(0,0,0,")+(0.03+R()*0.05)+")"; ctx.fillRect(x0+R()*w, y0+R()*h, 1.2, 1.2); }
  ctx.restore();
}
function gfxStitchLine(ctx, pts, color, width, closed){
  ctx.save(); ctx.strokeStyle=color; ctx.lineWidth=width; ctx.lineCap="round"; ctx.setLineDash([width*4.5, width*3.2]);
  ctx.beginPath(); pts.forEach((pt,i)=>i?ctx.lineTo(pt[0],pt[1]):ctx.moveTo(pt[0],pt[1])); if(closed) ctx.closePath(); ctx.stroke(); ctx.restore();
}
function gfxSponsorLogos(){ const g=state.gfx||{}; return (g.sponsors||[]).filter(Boolean).slice(0,2).map(k=>logoLib().find(x=>"upl:"+x.id===k)).filter(Boolean); }
async function gfxLogoChip(ctx, L, x, y, maxW, maxH, onDark, alignRight){
  if(!L) return 0;
  let img; try{ img=await gfxImg(L.data); }catch(e){ return 0; }
  let w=maxW, h=w*L.ratio; if(h>maxH){ h=maxH; w=h/L.ratio; }
  const left = alignRight ? x-w : x;
  if(onDark && !L.reverse){ const pad=Math.round(maxH*0.16); ctx.save(); gfxRound(ctx,left-pad,y-pad,w+2*pad,h+2*pad,14); ctx.fillStyle=GFX_LINEN; ctx.fill(); ctx.restore(); }
  ctx.drawImage(img, left, y, w, h); return w;
}
function gfxFitLines(ctx, text, maxW, sizeMax, sizeMin, maxLines){
  for(let S=sizeMax; S>=sizeMin; S-=2){ ctx.font=GF_SANS(800,S); const ls=gfxWrap(ctx,text,maxW); if(ls.length<=maxLines && !ls.some(l=>ctx.measureText(l).width>maxW)) return {S, lines:ls}; }
  ctx.font=GF_SANS(800,sizeMin); return {S:sizeMin, lines:gfxWrap(ctx,text,maxW)};
}
async function renderGraphicTexture(fmtKey){
  const F=GFX_FMT[fmtKey], g=Object.assign(GFX_DEFAULT(), state.gfx||{}), G=gfxGround(), wide=fmtKey==="wide";
  const cv=document.createElement("canvas"); cv.width=F.w; cv.height=F.h; const ctx=cv.getContext("2d");
  const seed=gfxHash(gfxSeedKey()+"|"+(g.texture||"linen"));
  gfxTexture(ctx,0,0,F.w,F.h,G.bg,g.texture||"linen",seed);
  const m=wide?96:80;
  if(g.stitch) gfxStitchLine(ctx,[[m*0.45,m*0.45],[F.w-m*0.45,m*0.45],[F.w-m*0.45,F.h-m*0.45],[m*0.45,F.h-m*0.45]], G.dark?"rgba(255,255,255,0.42)":gfxMix(gfxLead().c,GFX_LINEN,0.35), wide?4:3.5, true);

  // logo band: the venue, then up to two sponsors, on linen so any logo reads
  const venue=partnerLogo(), sponsors=gfxSponsorLogos();
  const items=[]; if(venue) items.push({L:venue, grp:"Hosted at"}); sponsors.forEach(L=>items.push({L, grp:"Sponsored by"}));
  const bandH = items.length ? (wide?210:230) : 0, bandTop=F.h-bandH;
  if(bandH){
    gfxTexture(ctx,0,bandTop,F.w,bandH,GFX_LINEN,"paper",seed+7);
    gfxStitchLine(ctx,[[0,bandTop+1],[F.w,bandTop+1]], gfxMix(gfxLead().c,GFX_LINEN,0.15), wide?5:4.5, false);
    const n=items.length, cellW=(F.w-2*m)/n, logoMaxW=Math.min(wide?380:320, cellW-60), logoMaxH=wide?96:92;
    for(let i=0;i<n;i++){
      const it=items[i], cx=m+cellW*(i+0.5);
      const first=items.findIndex(x=>x.grp===it.grp), last=items.length-1-items.slice().reverse().findIndex(x=>x.grp===it.grp);
      if(i===first){ const lx=m+cellW*((first+last)/2+0.5); ctx.fillStyle=GFX_MUTED; ctx.font=GF_SANS(600,24); ctx.textAlign="center"; ctx.fillText(it.grp.toUpperCase().split("").join(String.fromCharCode(8202)), lx, bandTop+(wide?58:62)); ctx.textAlign="left"; }
      let img; try{ img=await gfxImg(it.L.data); }catch(e){ continue; }
      let w=logoMaxW, h=w*it.L.ratio; if(h>logoMaxH){ h=logoMaxH; w=h/it.L.ratio; }
      const top=bandTop+(wide?82:88)+(logoMaxH-h)/2; ctx.drawImage(img, cx-w/2, top, w, h);
    }
  }

  // host logo, upper left
  await gfxLogoChip(ctx, brandLogo(G.dark), m, m, wide?360:300, wide?150:130, G.dark, false);

  const series=(g.series||"AI Fundamentals")+" for", prof=gfxLabel();
  const dateLine=g.showEvent?gfxDateLine():"", city=g.showEvent?gfxCity():"";
  const presenter = wide && g.coverLine && state.lead && state.lead.name ? "with "+state.lead.name : "";
  const art=gfxArt(); let artImg=null; if(art && wide){ try{ artImg=await gfxImg(art.data); }catch(e){} }

  if(!wide){
    const maxW=F.w-2*m-20, fit=gfxFitLines(ctx, prof, maxW, 132, 68, 3);
    const lh=Math.round(fit.S*1.06), seriesS=Math.round(Math.max(44, fit.S*0.42));
    const blockH=seriesS*1.5 + fit.lines.length*lh + 40 + (dateLine?72:0) + (city?50:0);
    const areaTop=m+150, areaBot=(bandH?bandTop:F.h-m)-30;
    let y=Math.max(areaTop, areaTop+((areaBot-areaTop)-blockH)/2) + seriesS;
    ctx.textAlign="center"; ctx.textBaseline="alphabetic";
    ctx.fillStyle=G.soft; ctx.font=GF_SANS(600,seriesS); ctx.fillText(series, F.w/2, y);
    y+=Math.round(seriesS*0.5);
    ctx.fillStyle=G.ink; ctx.font=GF_SANS(800,fit.S);
    fit.lines.forEach(l=>{ y+=lh; ctx.fillText(l, F.w/2, y); });
    y+=Math.round(fit.S*0.3)+22; gfxStitchLine(ctx,[[F.w/2-110,y],[F.w/2+110,y]], G.accent, 5, false); y+=10;
    if(dateLine){ y+=56; ctx.fillStyle=G.ink; ctx.font=GF_SANS(800,46); ctx.fillText(dateLine, F.w/2, y); }
    if(city){ y+=50; ctx.fillStyle=G.accent; ctx.font=GF_SANS(600,36); ctx.fillText(city, F.w/2, y); }
    ctx.textAlign="left";
  } else {
    const hasArt=!!artImg, colW=hasArt?1000:F.w-2*m-80;
    const fit=gfxFitLines(ctx, prof, colW, hasArt?132:156, 70, hasArt?3:2);
    const lh=Math.round(fit.S*1.05), seriesS=Math.round(Math.max(46, fit.S*0.4));
    const blockH=seriesS*1.5 + fit.lines.length*lh + 40 + (dateLine?72:0) + ((city||presenter)?52:0);
    const areaTop=m+170, areaBot=(bandH?bandTop:F.h-m)-34;
    let y=Math.max(areaTop, areaTop+((areaBot-areaTop)-blockH)/2) + seriesS;
    const x=m+6;
    ctx.fillStyle=G.soft; ctx.font=GF_SANS(600,seriesS); ctx.fillText(series, x, y);
    y+=Math.round(seriesS*0.5);
    ctx.fillStyle=G.ink; ctx.font=GF_SANS(800,fit.S);
    fit.lines.forEach(l=>{ y+=lh; ctx.fillText(l, x, y); });
    y+=Math.round(fit.S*0.3)+22; gfxStitchLine(ctx,[[x,y],[x+260,y]], G.accent, 6, false); y+=10;
    if(dateLine){ y+=58; ctx.fillStyle=G.ink; ctx.font=GF_SANS(800,48); ctx.fillText(dateLine, x, y); }
    const sub2=[city, presenter].filter(Boolean).join("   ·   ");
    if(sub2){ y+=52; ctx.fillStyle=G.accent; ctx.font=GF_SANS(600,38); ctx.fillText(sub2, x, y); }
    if(hasArt){
      const px=1160, py=m+40, pw=F.w-px-m, ph=(bandH?bandTop:F.h-m)-py-40;
      ctx.save(); gfxRound(ctx,px,py,pw,ph,22); ctx.clip();
      const r=art.ratio, sc=Math.max(pw/1, ph/r); const dw=Math.max(pw, ph/r), dh=dw*r;
      ctx.drawImage(artImg, px+(pw-dw)/2, py+(ph-dh)/2, dw, dh); ctx.restore();
      gfxStitchLine(ctx,[[px-14,py-14],[px+pw+14,py-14],[px+pw+14,py+ph+14],[px-14,py+ph+14]], G.dark?"rgba(255,255,255,0.45)":gfxLead().c, 4, true);
    }
  }
  return cv;
}
async function renderGraphic(fmtKey){
  await gfxFonts();
  const st=(state.gfx&&state.gfx.style)||"texture";
  return st==="scene" ? renderGraphicScene(fmtKey) : renderGraphicTexture(fmtKey);
}
async function renderGraphicScene(fmtKey){
''')

# ---------------------------------------------------------------- graphics tab controls
sub('box.appendChild(el("div","sub","Luma cover (1200 × 1200) and 16:9 deck cover in the Threads / Stitchs look"));',
    'box.appendChild(el("div","sub","Luma cover (1200 × 1200) and 16:9 deck cover, also the PowerPoint title slide"));')
sub('sceneCard.appendChild(tiles); out.appendChild(sceneCard);', 'sceneCard.appendChild(tiles); if(g.style==="scene") out.appendChild(sceneCard);')
sub('const pl=el("span","lab","Person color"); pl.style.cssText="display:block;margin-top:14px"; pf.appendChild(pl);',
    'const pl=el("span","lab","Person color"); pl.style.cssText="display:block;margin-top:14px"; if(g.style==="scene") pf.appendChild(pl);')
sub('    pf.appendChild(ps);\n', '    if(g.style==="scene") pf.appendChild(ps);\n')
sub('other people in group scenes get a mix from the same family."; pf.appendChild(ph);',
    'other people in group scenes get a mix from the same family."; if(g.style==="scene") pf.appendChild(ph);')
sub('    pf.appendChild(row);\n\n    // lead color:', r'''    pf.appendChild(row);

    // look: textured (default) or the old illustrated scene
    const segRow=(label, opts, cur, on, hint)=>{ const l=el("span","lab",label); l.style.cssText="display:block;margin-top:14px"; pf.appendChild(l);
      const r=el("div"); r.style.cssText="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:6px";
      opts.forEach(o=>{ const b=el("button","dd",o[1]); b.setAttribute("data-on",cur===o[0]?"1":"0"); b.onclick=()=>{ on(o[0]); saveGfxPrefs(); rerenderOut(); }; r.appendChild(b); });
      pf.appendChild(r); if(hint){ const h=el("div","hint",hint); h.style.marginTop="6px"; pf.appendChild(h); } };
    segRow("Look", [["texture","Textured"],["scene","Illustrated (old look)"]], g.style||"texture", v=>{ g.style=v; }, null);
    if(g.style!=="scene"){
      segRow("Background shade", [["deep","Deep"],["rich","Rich"],["light","Light linen"]], g.shade||"deep", v=>{ g.shade=v; }, "Deep and Rich use the lead color below with white type. Light linen uses cream with the lead color as the accent.");
      segRow("Texture", [["linen","Linen"],["paper","Handmade paper"],["woven","Woven"]], g.texture||"linen", v=>{ g.texture=v; }, null);
      segRow("Stitched border", [["off","Off"],["on","On"]], g.stitch?"on":"off", v=>{ g.stitch=(v==="on"); }, "A subtle running stitch around the edge.");
    }

    // lead color:''')
# sponsors after the venue picker
sub('    pf.appendChild(logoPicker("partner"));\n', r'''    pf.appendChild(logoPicker("partner"));
    if(g.style!=="scene"){
      const sl=el("span","lab","Sponsors (up to 2, in the logo band)"); sl.style.cssText="display:block;margin-top:14px"; pf.appendChild(sl);
      [0,1].forEach(i=>{
        const cur=(g.sponsors||[])[i]||"";
        const r=el("div"); r.style.cssText="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:6px";
        r.appendChild(el("span","hint","Sponsor "+(i+1)+":"));
        [["","None"]].concat(logoLib().map(L=>["upl:"+L.id,L.name])).forEach(o=>{ const b=el("button","dd",o[1]); b.setAttribute("data-on",cur===o[0]?"1":"0");
          b.onclick=()=>{ g.sponsors=(g.sponsors||[]).slice(); g.sponsors[i]=o[0]; rerenderOut(); }; r.appendChild(b); });
        r.appendChild(logoUploadButton("⬆ Upload", "sponsor"+(i+1)));
        pf.appendChild(r);
      });
      const sh2=el("div","hint"); sh2.style.marginTop="6px"; sh2.textContent="The venue and sponsors sit on a linen band at the bottom, so any logo color reads. Sponsors are saved with each workshop."; pf.appendChild(sh2);
    }
''')
sub('ih.textContent = gfxArt() ? "Using your image: "+gfxArt().name+"." : "Using the built-in scene for this profession: a day at their desk with the props of their job.";',
    'ih.textContent = gfxArt() ? "Using your image: "+gfxArt().name+"."+(g.style!=="scene"?" It shows on the right side of the 16:9 cover. The Luma square stays clean.":"") : (g.style!=="scene"?"Optional. Add a photo and it sits on the right side of the 16:9 cover, framed in a stitch. The Luma square stays clean.":"Using the built-in scene for this profession: a day at their desk with the props of their job.");')
sub('const back=el("button","btn ghost sm","Back to the built-in scene");', 'const back=el("button","btn ghost sm",g.style!=="scene"?"Remove my image":"Back to the built-in scene");')

p.write_text(s)
print("applied")
