MKDIR_P := mkdir -p
QPDF := qpdf
PYTHON3 := python3

all:

clean:
	$(RM) -r output

output: %:
	$(MKDIR_P) $@

output/pdf-toc.json: output input.pdf
	$(QPDF) input.pdf --json --json-key=outlines --json-key=pages output/pdf-toc.json

output/toc.json: convert-toc.py output/pdf-toc.json
	$(PYTHON3) $^ $@

output/insn.json: prepare-insn.py output/toc.json
	$(PYTHON3) $^ $@

output/insn: insn.mk output/insn.json
	$(MAKE) -f $<
