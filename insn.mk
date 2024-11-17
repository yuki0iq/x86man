JQ := jq
PYTHON3 := python3
UNOCONVERT := unoconvert

.SECONDARY:

all: $(shell $(JQ) <output/insn.json -cr '.[] | .slug + ".html"')

clean:
	$(RM) -r output/insn

output/insn/%.docx: extract-insn.py output/insn.json input.pdf
	$(PYTHON3) $^ $@

output/insn/%.html: output/insn/%.docx
	$(UNOCONVERT) --convert-to "html" --output-filter "XHTML Writer File" --host-location local $< $@

output/insn/%.md: html-to-markdown.py output/insn/%.html
	$(PYTHON3) $^ $@
