# x86 manual pages

Inspired by [Felix Cloutier's site](https://felixcloutier.com/x86).

Refer to [Intel® 64 and IA-32 Architectures Software Developer’s Manual](https://software.intel.com/en-us/download/intel-64-and-ia-32-architectures-sdm-combined-volumes-1-2a-2b-2c-2d-3a-3b-3c-3d-and-4) for anything serious. 

## Building

```shell
$ unoserver &
$ ln -s 325462-sdm-vol-1-2abcd-3abcd-4.pdf input.pdf
$ make -j4
```

TODO: convert insane HTMLs to sane format

## Dependencies

python-pdf2docx, qpdf, libreoffice, jq, python-unoserver, python-beautifulsoup4, python-cssutils, python-lxml, scdoc
