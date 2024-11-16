JQ := jq
PYTHON3 := python3
LIBREOFFICE := libreoffice

.SECONDARY:

all: $(shell $(JQ) <output/insn.json -cr '.[] | .slug + ".html"')

clean:
	$(RM) -r output/insn

output/insn/%.docx: extract-insn.py output/insn.json input.pdf
	$(PYTHON3) $^ $@

output/insn/%.html: output/insn/%.docx
	$(LIBREOFFICE) --convert-to "html:XHTML Writer File:UTF8" $< --outdir output/insn
