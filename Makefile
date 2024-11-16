MKDIR_P := mkdir -p
QPDF := qpdf
PYTHON3 := python3

.PHONY: instructions
.SECONDARY:

all: instructions

clean:
	$(RM) -r output

output/pdf-toc.json: input.pdf
	$(QPDF) input.pdf --json --json-key=outlines --json-key=pages output/pdf-toc.json

output/toc.json: convert-toc.py output/pdf-toc.json
	$(PYTHON3) $^ $@

output/insn.json: prepare-insn.py output/toc.json
	$(PYTHON3) $^ $@

instructions: output/insn.json
	$(MKDIR_P) output/insn
	$(MAKE) -f insn.mk
