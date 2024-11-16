#!/usr/bin/env python3

import json
import sys

_, inf, outf = sys.argv

with open(inf, 'r') as file:
    toc = json.load(file)

# Find TOC entries for instructions
volume = next(i for i, el in enumerate(toc["kids"]) if "Instruction Set Reference" in el["title"])
toc = toc["kids"][volume]
chapters = [i for i, el in enumerate(toc["kids"]) if "Instruction Set Reference" in el["title"]]

outline = []

for chapter in chapters:
    c_toc = toc["kids"][chapter]
    if "Unique" in c_toc["title"]:
        insn_toc = c_toc
    else:
        insns = next(i for i, el in enumerate(c_toc["kids"]) if "Instructions (" in el["title"])
        insn_toc = c_toc["kids"][insns]
    last = toc["kids"][chapter + 1]["page"]

    for i, insn in enumerate(insn_toc["kids"]):
        mnem, desc = insn["title"].split('—')
        mnem = ''.join(mnem.split())
        if i + 1 == len(insn_toc["kids"]):
            next_insn = {'page': last}
        else:
            next_insn = insn_toc["kids"][i + 1]
        outline.append({
            'from': insn['page'],
            'to': next_insn['page'],
            'mnem': mnem,
            'slug': f"output/insn/{mnem.replace('/', '+')}",
            'desc': desc,
        })

assert all(el['from'] and el['from'] < el['to'] and el['mnem'] and el['desc'] for el in outline)

with open(outf, 'w') as file:
    json.dump(outline, file)
