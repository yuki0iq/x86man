JQ := jq
MKDIR_P := mkdir -p
PYTHON3 := python3
LIBREOFFICE := libreoffice

all: $(shell $(JQ) <output/insn.json -cr '.[] | .slug + ".html"')

clean:
	$(RM) -r output/insn

output/insn: %:
	$(MKDIR_P) $@

output/insn/%.docx: extract-insn.py output/insn.json input.pdf output/insn
	$(PYTHON3) $^ $@

output/insn/%.html: output/insn/%.docx
	$(LIBREOFFICE) --convert-to "html:XHTML Writer File:UTF8" $< --outdir output/insn
