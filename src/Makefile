#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

SOURCES := $(shell find . -name '*.py')

lint_and_test: export PYTHONPATH=$PYTHONPATH:lib
all: lint build FORCE

build:
	(rm -rf out && \
	 mkdir -p out && \
	 cd out && \
	 pyinstaller -F ../bin/sd2)

lint: FORCE
	pylint -E $(SOURCES)

clean:
	rm -rf ./dist

FORCE:
