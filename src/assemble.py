#!/usr/bin/env python3
"""Inject the DAYS literal into template.html -> index.html."""
import json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.join(os.path.dirname(BASE), "scratchpad")

cards = json.load(open(os.path.join(SCR, "content.json"), encoding="utf-8"))
prac = json.load(open(os.path.join(SCR, "practice.json"), encoding="utf-8"))

def j(o, indent):
    s = json.dumps(o, ensure_ascii=False, indent=2)
    pad = " " * indent
    return ("\n" + pad).join(s.split("\n"))

lines = []
for day in sorted(cards, key=int):
    parts = [f"  cards: {j(cards[day], 4)}"]
    if day == "1":  # day 1 also carries the practice material -> sets practiceDay
        for k in ("reading", "writing", "speaking"):
            parts.append(f"  {k}: {j(prac[k], 4)}")
    lines.append(f"{day}: {{\n" + ",\n".join(parts) + "\n},")

days_js = "\n".join(lines)

tpl = open(os.path.join(BASE, "template.html"), encoding="utf-8").read()
assert "/*__DAYS__*/" in tpl
out = tpl.replace("/*__DAYS__*/", days_js)

dest = os.path.join(BASE, "index.html")
open(dest, "w", encoding="utf-8").write(out)
print(f"index.html  {len(out)/1024:.1f} KB")

# sanity: the append marker must still sit immediately after the DAYS literal
m = re.search(r"const DAYS = \{", out)
end = out.index("\n};", m.end())
tail = out[end:end + 200]
assert "DECK APPEND POINT" in out[end:end + 400], "append marker misplaced"
print("DECK APPEND POINT present after DAYS literal")
