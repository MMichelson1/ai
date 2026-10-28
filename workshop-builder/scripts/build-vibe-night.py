#!/usr/bin/env python3
"""Inject Vibe Night mode into workshop-builder/index.html (safe to re-run).

Sources live in workshop-builder/vibe-night/:
  base.gif        the standard Vibe Night GIF (only date, time, venue get repainted)
  template.pptx   the Vibe Night deck, images shrunk, What's Next text as {{TOKENS}}
  vibe-night.js   the Vibe Night mode code
  vnlib.js        bundled gifuct-js + gifenc + JSZip (MIT)
  *.woff2         Poppins Bold and Carlito Bold (SIL OFL 1.1)

Usage: python3 scripts/build-vibe-night.py
To refresh the deck: python3 scripts/shrink.py NEW.pptx /tmp/s.pptx && python3 scripts/prep_template.py /tmp/s.pptx vibe-night/template.pptx
"""
import base64, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
WB = os.path.dirname(HERE)
VN = os.path.join(WB, "vibe-night")
IDX = os.path.join(WB, "index.html")

def b64(name):
    with open(os.path.join(VN, name), "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def rd(name):
    with open(os.path.join(VN, name), encoding="utf-8") as f:
        return f.read()

CSS = """<style id="vn-style">
.main[hidden],#vnApp[hidden],#genBtn[hidden],#resetBtn[hidden]{display:none!important}
.modesw{display:inline-flex;border:1px solid var(--border-strong);border-radius:8px;overflow:hidden;margin-right:4px}
.modesw button{font:inherit;font-size:12.5px;font-weight:600;color:var(--muted);background:transparent;border:none;padding:6px 11px;cursor:pointer}
.modesw button[data-on="1"]{background:var(--p1-ink);color:#fff}
.vn-bar{height:6px;border-radius:4px;background:var(--surface2);margin-top:10px;overflow:hidden;max-width:420px}
.vn-bar i{display:block;height:100%;width:0;background:var(--p1);transition:width .2s}
.vn-prev{display:block;width:100%;max-width:520px;border-radius:8px;margin:14px 0;border:1px solid var(--border)}
#vnApp .doc .btn{margin-top:4px}
#vnApp input[type=time]{width:100%;font-family:inherit;font-size:13.5px;color:var(--text);background:var(--field);border:1px solid var(--border-strong);border-radius:var(--radius-sm);padding:9px 11px}
#vnApp input[type=file]{margin-top:10px;font-size:13px;color:var(--muted)}
</style>"""

MODESW = '<div class="modesw" id="modeSw"><button data-mode="ws">Workshop</button><button data-mode="vn">Vibe Night</button></div>'

APP = """<div class="main" id="vnApp" hidden>
    <section class="pane-form"><div class="scroll" id="vnForm"></div></section>
    <section class="pane-out"><div class="tabs" id="vnTabs"></div><div class="out-wrap" id="vnOut"></div></section>
  </div>"""

def main():
    s = open(IDX, encoding="utf-8").read()
    # strip any previous injection (each pattern removes exactly what the last run added)
    s = re.sub(r"<!-- VN:CSS -->.*?<!-- /VN:CSS -->\n", "", s, flags=re.S)
    s = re.sub(r"<!-- VN:SW -->.*?<!-- /VN:SW -->\n      ", "", s, flags=re.S)
    s = re.sub(r"\n  <!-- VN:APP -->.*?<!-- /VN:APP -->\n", "", s, flags=re.S)
    s = re.sub(r"<!-- VN:JS -->.*?<!-- /VN:JS -->\n", "", s, flags=re.S)

    def once(old, new, label):
        nonlocal s
        if s.count(old) != 1:
            sys.exit("anchor not found exactly once: " + label)
        s = s.replace(old, new)

    once("</head>\n<body>", "<!-- VN:CSS -->" + CSS + "<!-- /VN:CSS -->\n</head>\n<body>", "head")
    once('<button class="btn ghost sm" id="themeBtn"', "<!-- VN:SW -->" + MODESW + "<!-- /VN:SW -->\n      " + '<button class="btn ghost sm" id="themeBtn"', "theme button")
    once('</div>\n<div class="toast" id="toast"></div>',
         "\n  <!-- VN:APP -->" + APP + "<!-- /VN:APP -->\n</div>\n<div class=\"toast\" id=\"toast\"></div>", "app end")
    js = ("<!-- VN:JS --><script>/* gifuct-js, gifenc, JSZip (MIT) */\n" + rd("vnlib.js") + "\n</script>\n<script>window.VN_ASSETS={"
          + 'gif:"' + b64("base.gif") + '",pptx:"' + b64("template.pptx") + '",poppins:"' + b64("poppins-700.woff2")
          + '",carlito:"' + b64("carlito-bold.woff2") + '"};</script>\n<script>\n' + rd("vibe-night.js") + "\n</script><!-- /VN:JS -->\n")
    idx = s.rfind("</body>")
    s = s[:idx] + js + s[idx:]

    # --- route every download through one helper (Claude downloads capability, else browser download) ---
    s = s.replace("""async function saveFile(filename, data){
  if(window.claude && window.claude.downloads && typeof window.claude.downloads.save==="function"){
    try{ await window.claude.downloads.save({filename, data}); toast("Saved "+filename); return; }
    catch(e){ /* fall through to blob */ }
  }
  try{""", """async function saveFile(filename, data){
  if(window.__deliverFile){ return window.__deliverFile(filename, new Blob([data],{type:"text/plain"})); }
  try{""")
    s = s.replace("""function downloadBlob(fn, blob){
  const u=""", """function downloadBlob(fn, blob){
  if(window.__deliverFile){ window.__deliverFile(fn, blob); return; }
  const u=""")
    s = s.replace("""    if(window.claude&&window.claude.downloads&&typeof window.claude.downloads.save==="function"){
      window.claude.downloads.save({filename:fn,data:html}).then(()=>toast("Saved "+fn)).catch(()=>{""",
                  """    if(window.__deliverFile){ window.__deliverFile(fn, blob); return; }
    if(false){
      (function(){""")
    s = s.replace("""  const body = PPTX_BODY.replace('"/mnt/user-data/outputs/" + META.file', "META.file");""",
                  """  const body = PPTX_BODY.replace('pres.writeFile({ fileName: "/mnt/user-data/outputs/" + META.file })', 'pres.write({ outputType: "blob" }).then(function (b) { return window.__deliverFile ? window.__deliverFile(META.file, b) : pres.writeFile({ fileName: META.file }); })');""")
    if "window.claude.downloads" in s:
        sys.exit("old downloads code still present")
    open(IDX, "w", encoding="utf-8").write(s)
    print("index.html", os.path.getsize(IDX), "bytes")

main()
