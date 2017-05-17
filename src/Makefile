#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

SOURCES := $(shell find . -name '*.py')

lint_and_test: export PYTHONPATH=$PYTHONPATH:lib
all: lint FORCE

lint: FORCE
	pylint -E $(SOURCES)

FORCE:
