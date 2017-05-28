#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################


SOURCES := $(shell find . -name '*.py')

TOP=$(realpath .)
SD2OS=$(shell uname)
OUT=out/$(shell uname)

lint: export PYTHONPATH=$PYTHONPATH:lib
build: export PYTHONPATH=$PYTHONPATH:lib

all: lint build FORCE

build: clean
	(mkdir -p $(OUT) && \
	 cd $(OUT) && \
	 pyinstaller -F $(TOP)/bin/sd2 && \
	 cp dist/sd2 dist/sd2-$(SD2OS))
	 pwd
	 find . -name

lint: FORCE
	pylint -E $(SOURCES)

clean:
	rm -rf out

FORCE:
