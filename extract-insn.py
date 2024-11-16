#!/usr/bin/env python3

import json
import os
import pdf2docx
import sys

_, tocf, inf, _, outf = sys.argv

with open(tocf, 'r') as file:
    toc = json.load(file)

cv = pdf2docx.Converter(inf)
insn = next(el for el in toc if el["slug"] == outf[:outf.rfind('.')])
start = insn["from"] - 1
end = insn["to"] - 1
mnem = insn["mnem"]
desc = insn["desc"]
cv.convert(outf, start=start, end=end)
cv.close()
