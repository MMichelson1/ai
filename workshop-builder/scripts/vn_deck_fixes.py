#!/usr/bin/env python3
"""One-time layout and copy fixes to the Vibe Night deck template (Oct 27, 2026 review).

Usage: python3 scripts/vn_deck_fixes.py vibe-night/template.pptx vibe-night/template.pptx

1  QR code no longer overlaps "3. SUBSCRIBE" (Wi-Fi image smaller, text and QR moved up)
5  big C logo faded to 10% so the text reads over it
8  "Subscribe to: Luma.com/AICATL" stays on one line above the orange rule
13 Comet row becomes Perplexity
14 Agent vs App: more room so the examples never touch the divider lines
16 starter prompt in plain language (no code-style green text)
19 App Starter Ideas rebuilt: titles on their own line, plain-language prompts, rules between rows
"""
import io, sys, copy
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
p = Presentation(src)
S = lambda n: p.slides[n - 1]
def shp(n, sid): return next(s for s in S(n).shapes if s.shape_id == sid)
def place(sh, l=None, t=None, w=None, h=None):
    if l is not None: sh.left = Inches(l)
    if t is not None: sh.top = Inches(t)
    if w is not None: sh.width = Inches(w)
    if h is not None: sh.height = Inches(h)
def remove(sh): sh._element.getparent().remove(sh._element)
def set_text(sh, txt):
    runs = sh.text_frame.paragraphs[0].runs
    runs[0].text = txt
    for r in runs[1:]: r.text = ""

WHITE, ORANGE, SOFT = RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xF5, 0xA6, 0x23), RGBColor(0xA8, 0xA6, 0xD0)

def write_paras(sh, paras, size, space_after=6):
    """paras: list of [(text, bold, color, italic), ...] runs per paragraph. Calibri, left aligned, no bullets."""
    tf = sh.text_frame; tf.word_wrap = True
    body = tf._txBody
    for extra in tf.paragraphs[1:]: body.remove(extra._p)
    first = tf.paragraphs[0]
    for r in list(first.runs): first._p.remove(r._r)
    for i, runs in enumerate(paras):
        para = first if i == 0 else tf.add_paragraph()
        para.space_after = Pt(space_after); para.space_before = Pt(0)
        for text, bold, color, italic in runs:
            r = para.add_run(); r.text = text
            f = r.font; f.size = Pt(size); f.bold = bold; f.italic = italic; f.name = "Calibri"; f.color.rgb = color

# ---- slide 1: right column spacing
place(shp(1, 23), t=0.30)
place(shp(1, 22), t=0.95)
wifi = shp(1, 4); place(wifi, l=6.35, t=1.55, w=2.08, h=1.59)
sub = shp(1, 21); place(sub, t=3.25, h=0.62); sub.text_frame.vertical_anchor = 1  # top
place(shp(1, 3), l=6.86, t=3.98, w=1.05, h=1.05)

# ---- slide 5: fade the big C logo to 10% (baked into the image so every app shows it the same)
logo = shp(5, 58)
part = logo.part.related_part(logo._element.blipFill.blip.rEmbed)
im = Image.open(io.BytesIO(part.blob)).convert("RGB")
faded = Image.eval(im, lambda v: int(255 - 0.10 * (255 - v)))
buf = io.BytesIO(); faded.save(buf, "JPEG", quality=85)
part._blob = buf.getvalue()

# ---- slide 8: keep the title on one line
title = shp(8, 100)
for para in title.text_frame.paragraphs:
    for r in para.runs:
        if r.font.size: r.font.size = Pt(round(r.font.size.pt * 0.82))

# ---- slide 13: Comet -> Perplexity
set_text(shp(13, 196), "Perplexity")
set_text(shp(13, 197), "perplexity.ai")
set_text(shp(13, 198), "Real-time search with sources. Great for travel research.")

# ---- slide 14: room between examples and the rules
for sid, t in [(209, 1.98), (210, 2.42), (211, 2.98), (214, 1.98), (215, 2.42), (216, 2.98)]:
    place(shp(14, sid), t=t, h=0.52)
for sid in (209, 210, 211, 214, 215, 216):
    for r in shp(14, sid).text_frame.paragraphs[0].runs: r.font.size = Pt(14)
for sid in (212, 217):
    sh = shp(14, sid); place(sh, t=3.52, h=0.78); sh.text_frame.vertical_anchor = 1
place(shp(14, 207), t=1.38, h=2.92)
place(shp(14, 218), t=4.40)
place(shp(14, 219), t=4.50)

# ---- slide 16: plain-language starter prompt
set_text(shp(16, 241), "YOUR STARTER PROMPT  —  SAY IT IN PLAIN ENGLISH")
for sid in range(245, 253): remove(shp(16, sid))
box = shp(16, 244); place(box, l=0.72, t=1.52, w=8.55, h=2.85); box.text_frame.vertical_anchor = 1
write_paras(box, [
    [("Who it's for:  ", True, ORANGE, False), ("Me, planning a 4-day trip to [your city].", False, WHITE, False)],
    [("Why:  ", True, ORANGE, False), ("I want one plan with everything in it, not ten open tabs.", False, WHITE, False)],
    [("What I need:  ", True, ORANGE, False), ("Flights, a hotel in a good neighborhood, how to get around, restaurants, shows, and the must-dos for each day.", False, WHITE, False)],
    [("How I want it:  ", True, ORANGE, False), ("Ask me a few questions first. Then give me a day-by-day plan I can read on my phone.", False, WHITE, False)],
    [("Type it the way you'd say it to a friend. Change anything that doesn't fit you.", False, SOFT, True)],
], size=17, space_after=9)

# ---- slide 19: rebuild the three rows
ideas = [
    ("\U0001F3C3  Health Tracker", "Build me a simple app for my iPhone to log my workouts: what I did, how long, and how I felt. I want to stay consistent, so show a weekly summary and my streak."),
    ("\U0001F4DE  Sales Activity Tracker", "Build a web app for me, a salesperson, to log calls, meetings, and follow-ups with notes. Show my week at a glance so nothing slips, and let me export it to a spreadsheet."),
    ("\U0001F3AE  Mini Game", "Build a word guessing game my family can play in the browser. Five-letter words, six guesses. Color the letters so kids can see what's right. Make it bright and fun."),
]
heads, descs, prompts, rules = [292, 296, 300], [293, 297, 301], [294, 298, 302], [291, 295, 299]
for i, (name, prompt) in enumerate(ideas):
    top = 1.48 + i * 1.08
    place(shp(19, rules[i]), t=top - 0.08)
    h = shp(19, heads[i]); place(h, l=0.5, t=top, w=7.7, h=0.36); h.text_frame.word_wrap = False
    write_paras(h, [[(name, True, ORANGE, False)]], size=16, space_after=0)
    pr = shp(19, prompts[i]); place(pr, l=0.5, t=top + 0.36, w=7.7, h=0.62); pr.text_frame.vertical_anchor = 1
    write_paras(pr, [[(prompt, False, WHITE, False)]], size=13, space_after=0)
    remove(shp(19, descs[i]))

p.save(out)
print("saved", out)
