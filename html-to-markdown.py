#!/usr/bin/env python3

import bs4
import cssutils
import json
import markdownify
import re
import os
import sys

_, inf, outf = sys.argv

with open(inf) as file:
    soup = bs4.BeautifulSoup(file.read(), 'lxml-xml')

selectors = {}
for styles in soup.select('style'):
    css = cssutils.parseString(styles.encode_contents(), validate=False)
    for rule in css:
        if rule.type == rule.STYLE_RULE:
            selectors[rule.selectorText] = {item.name: item.value for item in rule.style}

for sel, sty in selectors.items():
    if not sel.startswith(".text-"):
        continue

    matches = soup.find_all("span", class_=sel[1:])
    for match in matches:
        assert sty.get("color") in ["#000", "#075fa8", "#6331af"]
        if sty.get("text-decoration") == "underline":
            match.wrap(soup.new_tag("u"))
        if sty.get("font-style") == "italic":
            match.wrap(soup.new_tag("i"))
        if sty.get("font-weight") == "bold":
            match.wrap(soup.new_tag("b"))
        if sty.get("color") == "#075fa8":
            assert sty["font-size"] in ["8pt", "9pt", "9.5pt", "10pt", "11pt", "12pt"]
            if sty["font-size"] == "12pt":
                global_name = match.get_text().replace('—', ' -- ')
                match.name = "h1"
                match.string.replace_with("Synopsis")
            elif sty["font-size"] in ["10pt", "11pt"]:
                match.name = "h1"
            elif sty["font-size"] in ["8pt", "9pt", "9.5pt"]:
                match.name = "h2"
            if match.parent.name == "p":
                match.parent.unwrap()
        if sty.get("font-family") == "NeoSansIntel" and sty.get("font-size") == "8pt":
            for el in match.parents:
                match.decompose()
                if el.get_text().strip():
                    break
                match = el

def merge_siblings(name, cond):
    for match in soup.find_all(name):
        psi = next((sib for sib in match.previous_siblings if sib.get_text().strip()), None)
        if psi and psi.name == name and cond(match):
            match.name = "span"
            psi.append(match.extract())

merge_siblings("h1", lambda _: True)
merge_siblings("h2", lambda _: True)
merge_siblings("h3", lambda _: True)
merge_siblings("p", lambda match: next((ch.islower() for ch in match.get_text() + 'A' if ch.isalpha()), None))

for table in soup.find_all("table"):
    if len(table.find_all("img")) != 0:
        table.decompose()
        continue

    tr = next((el for el in table.children if el.name == "tr"), None)
    if not tr or any(el.name == "thead" for el in table.children):
        continue
    thead = soup.new_tag("thead")
    for el in tr.children:
        if el.name == "td":
            el.name = "th"
    thead.append(tr)
    table.insert(0, thead)

for header in soup.find_all(string="Operation"):
    header = header.parent
    pre = soup.new_tag("pre")
    for sib in list(header.next_siblings):
        if sib.name == "h1":
            break
        pre.append(sib.extract())
    for el in list(pre.descendants):
        if not el.get_text() and not el.name == "br":
            el.decompose()
        if el.name == "p":
            el.insert_after(soup.new_tag("br"))
            el.unwrap()
        if el.name == "span" and "style" not in el.attrs:
            el.unwrap()
        if el.name == "span" and "style" in el.attrs:
            sty = {item.name: item.value for item in cssutils.parseStyle(el.attrs["style"], validate=False)}
            assert sty['position'] == "absolute" and sty['left'][-2:] == "cm"
            el.insert_before(' ' * max(0, int(float(sty['left'][:-2]) / .4 + .5)))
            el.unwrap()
    # TODO: Do not replace LF if '(text) LF (text)'; replace only "blank" '(space) LF (space)'
    # TODO: Prettier automatic formatting
    for nl in pre.find_all(string="\n"):
        nl.replace_with('')
    for br in pre.find_all("br"):
        br.replace_with("\n")
    header.insert_after(pre)

with open("/tmp/a.html", "w") as file: print(soup, file=file)
md = markdownify.MarkdownConverter().convert_soup(soup)
md = '\n'.join(line if line.strip() else "" for line in md.split('\n'))
md = re.sub('\n{2,}', '\n\n', md, flags=re.MULTILINE)
md = md.replace('\n\n\\- no title specified\n\n', '', 1)
md = fr'''---
title: {outf.replace("output/insn/", "").replace(".md", "")}
section: 7intel
header: Intel ISA Reference
footer: Intel Software Developer's Manual
date: January 1, 1970
---

Name
====

{global_name}

''' + md
with open(outf, 'w') as file:
    print(md, file=file)
