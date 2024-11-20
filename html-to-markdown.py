#!/usr/bin/env python3

import bs4
import cssutils
import io
import json
import pandas
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
        if sty.get("color") == "#075fa8" and "https://" not in match.get_text():
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
        if sty.get("text-decoration") == "underline":
            match.wrap(soup.new_tag("u"))
        if sty.get("font-style") == "italic":
            match.wrap(soup.new_tag("i"))
        if sty.get("font-weight") == "bold":
            match.wrap(soup.new_tag("b"))
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
        if not el.get_text() and not el.name == "br" and not isinstance(el, bs4.Comment):
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
    # TODO: Prettier automatic formatting
    for br in pre.find_all("br"):
        br.replace_with("\n")
    header.insert_after(pre)

soup.smooth()

for header in soup.find_all(string=lambda x: "Intrinsic Equivalent" in x):
    header = next((el for el in header.parents if el.name == "h1"), None)
    if header is None:
        continue
    pre = soup.new_tag("pre")
    for sib in list(header.next_siblings):
        if sib.name == "h1":
            break
        pre.append(sib.extract())
    for br in pre.find_all("br"):
        br.replace_with("\n")
    header.insert_after(pre)


soup.smooth()

def is_table_well(soup):
    count = set()
    for row in soup.find_all("tr"):
        count.add(len(row.find_all("th")) + len(row.find_all("td")))
    return len(count) == 1

with open("/tmp/a.html", "w") as file: print(soup, file=file)

def convert(soup):
    def batch(children):
        for child in children:
            yield from convert(child)

    def escape(s):
        return s.replace('\\', r'\\').replace('_', r'\_').replace('*', r'\*').replace('#', r'\#')

    if isinstance(soup, bs4.Comment):
        pass

    elif isinstance(soup, bs4.NavigableString):
        yield escape(str(soup))

    elif soup.name in "h1 h2 h3 h4 h5 h6".split():
        yield "#" * int(soup.name[1:])
        yield " "
        yield from batch(soup.contents)
        yield "\n\n"

    elif soup.name == "pre":
        yield "\n```\n"
        yield from batch(soup.contents)
        yield "\n```\n"

    elif soup.name == "p":
        yield "\n\n"
        yield from batch(soup.contents)
        yield "\n"

    elif soup.name == "u":
        yield "_"
        yield from batch(soup.contents)
        yield "_"

    elif soup.name == "b":
        yield "*"
        yield from batch(soup.contents)
        yield "*"

    elif soup.name == "i":
        yield "*"
        yield from batch(soup.contents)
        yield "*"

    elif soup.name == "table":
        yield "\n\n"

        if is_table_well(soup):
            yield from batch(soup.contents)
        else:
            df = pandas.read_html(io.StringIO(str(soup)))[0]
            table = df.transpose().to_dict()

            for i, col in enumerate(df.columns):
                if i == 0:
                    yield "[[ "
                else:
                    yield ":[ "
                yield "*"
                yield str(col)
                yield "*\n"

            for _, line in sorted(table.items()):
                for j, col in enumerate(df.columns):
                    if j == 0:
                        yield "|  "
                    else:
                        yield ":  "
                    yield str(line[col]).replace('\n', ' ').strip()
                    yield "\n"

    elif soup.name in ["td", "th"]:
        text = soup.get_text().strip()
        colspan = 1
        if 'colspan' in soup.attrs:
            colspan = int(soup['colspan'])

        if soup.name == "th":
            if not soup.previous_sibling:
                yield "[[ "
            elif not soup.next_sibling and text == "Description":
                yield ":< "
            else:
                yield ":[ "

            yield from ('\n:[ ' for _ in range(1, colspan))
            yield "*"
        else:
            yield "|  " if not soup.previous_sibling else ":  "

        if "64" in text and "32" in text and soup.name == "th":
            yield "64/32"
        elif "CPUID" in text and "Feature" in text and soup.name == "th":
            yield "CPUID"
        elif "Compat" in text and "Leg" in text and soup.name == "th":
            yield "Compat"
        else:
            yield from map(lambda x: x.replace('\n', ' ').strip(), batch(soup.contents))

        if soup.name == "th":
            yield "*"
        else:
            yield from ('\n:  ' for _ in range(1, colspan))
        yield "\n"

    else:
        yield from batch(soup.contents)

name = outf[outf.rfind("/") + 1:outf.rfind(".")].replace('+', '_').replace(',', '_')
md = f'''{name}(7intel) "Intel Software Developer's manual" "Intel x86 ISA reference"

{''.join(convert(soup.find("body")))}

# UNOFFICIAL

This UNOFFICIAL, mechanically-separated, non-verified reference is provided for convenience, but it may be inc..pl.te or broK3n in various obvious or non-obvious ways. Refer to official manual for anything serious.
'''

with open(outf, 'w') as file:
    print(md, file=file)
