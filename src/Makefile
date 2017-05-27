#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################


SOURCES := $(shell find . -name '*.py')

lint: export PYTHONPATH=$PYTHONPATH:lib
build: export PYTHONPATH=$PYTHONPATH:lib

all: lint build FORCE

build: clean
	(mkdir -p out && \
	 cd out && \
	 pyinstaller -F ../bin/sd2)

lint: FORCE
	pylint -E $(SOURCES)

clean:
	rm -rf out

FORCE:
