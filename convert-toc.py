#!/usr/bin/env python3

import json
import sys

_, inf, outf = sys.argv

with open(inf, 'r') as file:
    toc = json.load(file)

assert toc['version'] == 2

outline = toc['outlines'][0]
pages = {page["object"]: page["pageposfrom1"] for page in toc['pages']}

def convert(outline):
    dest = outline['dest']
    if type(dest) == type({'':1}):
        dest = dest['/D']
    if type(dest) == type([]):
        dest = dest[0]
    return {
        'page': pages.get(dest),
        'title': outline['title'],
        'kids': [convert(kid) for kid in outline['kids']]
    }

outline = convert(outline)

# TODO: Add "last page" to TOC

with open(outf, 'w') as file:
    json.dump(outline, file)
