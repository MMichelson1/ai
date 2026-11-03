#!/usr/bin/env python3
"""Split the marketing ICP in two (repeatable; a second run changes nothing).

- "Marketing Professionals" becomes "Digital Marketing Professionals" (content unchanged).
- New "Marketing Strategy Professionals": B2B-first marketing strategy and CX. Positioning, a niche built
  on your own expertise, a real customer problem, prove it is real, size it, reach the people who have it, and build a
  tribe that recommends you.
- Saved workshops and saved ICP edits under the old name move to the new digital name.
"""
import json, sys, pathlib

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "index.html")
s = p.read_text()
OLD, DIG, NEW = "Marketing Professionals", "Digital Marketing Professionals", "Marketing Strategy Professionals"

if NEW in s:
    print("already applied"); sys.exit(0)

def sub(a, b, count=1):
    global s
    n = s.count(a)
    assert n == count, (a[:80], n)
    s = s.replace(a, b)

# ---------- rename every keyed occurrence ----------
sub('"Marketing Professionals","Merchandising"', '"Marketing Strategy Professionals","Merchandising"')
sub('"CX Design","CX Management","Enterprise Teams"', '"CX Design","CX Management","Digital Marketing Professionals","Enterprise Teams"')
sub('  "Marketing Professionals":{noun:"marketer", short:"Marketing"},',
    '  "Digital Marketing Professionals":{noun:"digital marketer", short:"DigitalMarketing"},\n'
    '  "Marketing Strategy Professionals":{noun:"marketing strategist", short:"MarketingStrategy"},')
sub('  "Marketing Professionals":{\n    titles:', '  "Digital Marketing Professionals":{\n    titles:')
sub(' "Marketing Professionals": [\n', ' "Digital Marketing Professionals": [\n')
sub('"Marketing Professionals":{"analogy"', '"Digital Marketing Professionals":{"analogy"')
sub('  "Marketing Professionals":["megaphone","trend","image","target","chat","pie"],',
    '  "Digital Marketing Professionals":["megaphone","trend","image","target","chat","pie"],\n'
    '  "Marketing Strategy Professionals":["search","users","target","chat","heart","trend"],')
sub('  "Marketing Professionals":{t:"stage"},',
    '  "Digital Marketing Professionals":{t:"stage"},\n'
    '  "Marketing Strategy Professionals":{t:"team", wall:"journey"},')
assert '"Marketing Professionals"' not in s, "a keyed occurrence was missed"

# ---------- new ICP ----------
icp = {
 "titles": "Marketing Director, Marketing Consultant, Product Marketing Manager, Brand Strategist, Founder new to marketing, Business owner doing their own marketing",
 "pains": ["Not knowing which customer problems are real", "Not sure how big the market is or who the real competition is",
           "Positioning that sounds like every competitor", "Turning deep expertise into a niche you can own",
           "Product, packaging, and service messages that don't land", "Social posts, emails, and event networking with no plan behind them",
           "New to marketing and not sure where to start"],
 "winning": ["A clear niche built on real customer problems", "Positioning buyers remember and repeat",
             "One message carried through social, email, and events", "A simple marketing plan a founder can run alone",
             "Customers who recommend you to their peers"],
 "tools": ["Google Workspace", "LinkedIn", "HubSpot or Mailchimp", "Canva", "Zoom", "Qualtrics or SurveyMonkey", "Excel"],
 "claude": ["Your positioning sounds like every competitor → three positioning options built on your expertise and what buyers are trying to solve, with the trade-offs",
            "Product and service descriptions list features nobody asked about → messaging, packaging copy, and a one-page sell sheet built on the problem you solve",
            "Social posts and emails feel random → a month of LinkedIn posts and a short email sequence that all carry the same positioning"],
 "gemini": ["Win and loss notes sit in a Sheet → Gemini in Sheets shows the real reasons deals were won and lost",
            "Event contacts land in a Sheet and go cold → Gemini drafts a personal follow-up for each one in Gmail",
            "Strategy notes live in five Docs → one positioning brief pulled together in Docs"],
 "perplexity": ["Not sure the market is big enough → a sourced estimate of how many companies or people have the problem, by industry and size",
                "Not sure who you really compete with → a sourced scan of competitors and substitutes, how each positions, and what their customers say",
                "Not sure where your buyers gather → a sourced list of the associations, events, publications, and LinkedIn groups they trust"],
 "notebooklm": ["Discovery calls and customer interviews pile up → ask what problems people describe and how they solve them today",
                "Reviews, win and loss notes, and support tickets hold the truth → ask why customers buy, stay, leave, and recommend",
                "Your niche is hiding in your past work → upload your case studies and ask which problems you solve best, and for whom"],
 "lovable": ["You want proof of demand before you build → a simple offer page with a sign-up that measures interest",
             "Business cards from events sit in a drawer → an event follow-up tracker you can update from your phone",
             "Your best customers have no place to connect → a member hub where your tribe shares ideas and refers peers"],
 "cowork": ["Research files are scattered across drives → one research library organized by customer segment and problem",
            "You need a marketing plan and don't know where to start → a one-page plan from customer need to channels, built from your notes",
            "Great customer quotes get lost → a quote bank sorted by problem and buyer, ready for posts and emails"],
}
def js(v): return json.dumps(v, ensure_ascii=False)
block = '  "Marketing Strategy Professionals":{\n' + ",\n".join("    %s:%s" % (k, js(v)) for k, v in icp.items()) + "\n  },\n"
sub('  "Digital Marketing Professionals":{\n    titles:', block + '  "Digital Marketing Professionals":{\n    titles:')

kit = [
 {"tool":"Claude","problem":"Positioning that sounds like everyone else",
  "context":"I help [type of customer] with [what we do]. My background is [your expertise]. Our best customers are [who].",
  "sources":"Paste our current description, descriptions of 3 competitors, and notes from customer conversations.",
  "good":"Three positioning options. Each names the niche (exactly who), the problem we solve, why we are the ones to solve it, and what we stop saying. Note the trade-off of each.",
  "stop":"Stop at three options. Use only what I gave you. Ask me questions if anything is unclear."},
 {"tool":"Perplexity","problem":"Market size and real competition",
  "context":"We help [type of customer] that struggle with [problem].",
  "sources":"Search industry reports, government data, associations, competitor sites, and news. Cite everything.",
  "good":"An estimate of how many companies or people have this problem, the 5 competitors and substitutes they use today, how each positions itself, and where these buyers gather, each with a source link.",
  "stop":"Stop at the estimate and the lists. Show the math. Flag weak sources."},
 {"tool":"Notebook","problem":"Why customers buy and recommend",
  "context":"I want to know why our best customers chose us and why they tell others.",
  "sources":"Upload interview notes, reviews, testimonials, and win and loss notes.",
  "good":"The reasons people buy, stay, and recommend us, in their words, with quotes and sources, plus the moments where we nearly lost them.",
  "stop":"Stop at the findings. No copywriting yet."},
 {"tool":"Gemini","problem":"Following up after a networking event",
  "context":"I met [number] people at [event]. I want each to hear from me within two days.",
  "sources":"The Sheet of contacts with a note on what we talked about.",
  "good":"A short, personal Gmail draft for each person that mentions our conversation and offers one useful next step. No sales pitch.",
  "stop":"Stop at drafts. Send nothing."},
 {"tool":"Claude Cowork","problem":"A first marketing plan",
  "context":"I'm building the marketing plan for [product or service].",
  "sources":"My notes and research in [folder path].",
  "good":"A 2-page plan: the customer and their problem, proof it is real, market size and competitors, our positioning, product and service messages, and a 90-day plan for social, email, and events.",
  "stop":"Stop at the draft plan for my review."},
]
kit_txt = ' "Marketing Strategy Professionals": ' + json.dumps(kit, indent=1, ensure_ascii=False).replace("\n", "\n ") + ",\n"
sub(' "Digital Marketing Professionals": [\n', kit_txt + ' "Digital Marketing Professionals": [\n')

teach = {"analogy":"Think of AI as a marketing department on call: research, writing, and analysis on demand. It still needs the fundamentals from you: who the customer is, what problem you solve, and why you. Those come from talking to real customers.",
 "notFor":["Replacing real conversations with customers","Inventing customer needs or market sizes with no source","Deciding your strategy for you"],
 "bad":"Write a marketing plan.",
 "agent":"A positioning assistant: give it your expertise, your best customers, and your competitors, and it drafts niche and positioning options for you to test with real buyers.",
 "auto":"Event ends → you add contacts and notes to a Sheet → AI drafts a personal follow-up email and LinkedIn note for each → you approve → they send.",
 "graph":"Connect accounts, buyer roles, problems, deals, and referrals, so AI can show which problem wins deals and drives word of mouth."}
sub('"Digital Marketing Professionals":{"analogy"', '"Marketing Strategy Professionals":' + js(teach) + ',"Digital Marketing Professionals":{"analogy"')

# ---------- migrate saved data under the old name ----------
sub('function renameOldTools(){\n',
    'function renameOldTools(){\n'
    '  if(state.audience==="Marketing Professionals") state.audience="Digital Marketing Professionals";\n'
    '  if(state.audience2==="Marketing Professionals") state.audience2="Digital Marketing Professionals";\n')
sub('function loadStore(){ try{ return JSON.parse(localStorage.getItem(LS_KEY)||"{}"); }catch(e){ return {}; } }',
    'function loadStore(){ try{ const o=JSON.parse(localStorage.getItem(LS_KEY)||"{}");\n'
    '  // "Marketing Professionals" was renamed "Digital Marketing Professionals"; move saved ICP edits once.\n'
    '  if(o.overrides && o.overrides["Marketing Professionals"]){ if(!o.overrides["Digital Marketing Professionals"]) o.overrides["Digital Marketing Professionals"]=o.overrides["Marketing Professionals"]; delete o.overrides["Marketing Professionals"]; try{ localStorage.setItem(LS_KEY, JSON.stringify(o)); }catch(e){} }\n'
    '  return o; }catch(e){ return {}; } }')

p.write_text(s)
print("applied")
