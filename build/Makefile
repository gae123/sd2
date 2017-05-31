#############################################################################
# Copyright (c) 2017 SiteWare Corp. All right reserved
#############################################################################

TOP := $(realpath ..)
SD2OS := $(shell uname)
OUT := $(TOP)/out/$(SD2OS)

export PYTHONPATH := $(PYTHONPATH):lib

PYTHON_SOURCES := $(shell find $(TOP) -name '*.py')
PYTHON_CHECKED := $(patsubst %.py,$(OUT)/checked/%.py.checked,$(PYTHON_SOURCES))
JSON_SOURCES := $(shell find $(TOP) -name '*.json')
JSON_CHECKED := $(patsubst %.json,$(OUT)/checked/%.json.checked,$(JSON_SOURCES))
BASH_SOURCES := $(shell find $(TOP) -name '*.sh')
BASH_CHECKED := $(patsubst %.sh,$(OUT)/checked/%.sh.checked,$(BASH_SOURCES))
DOCKER_SOURCES := $(shell find $(TOP) -name 'Dockerfile')
DOCKER_CHECKED := $(patsubst %,$(OUT)/checked/%.checked,$(DOCKER_SOURCES))
SOURCES_CHECKED := $(PYTHON_CHECKED) $(JSON_CHECKED) $(BASH_CHECKED) $(DOCKER_CHECKED)


all: $(SOURCES_CHECKED) $(OUT)/.lint build FORCE

build:
	( rm -rf $(OUT)/install && \
	 mkdir -p $(OUT)/install && \
	 cd $(OUT)/install && \
	 ~/.local/bin/pyinstaller -F $(TOP)/src/bin/sd2 && \
	 cp dist/sd2 dist/sd2-$(SD2OS))

$(OUT)/.lint: $(PYTHON_SOURCES)
	pylint -E $(PYTHON_SOURCES)
	touch $@

$(SOURCES_CHECKED): $(OUT)/checked/%.checked: %
	echo Checking $(<F) for tabs and long lines
	$(TOP)/build/check_code_style.py $<
	mkdir -p $(@D)
	touch $@

clean:
	rm -rf $(OUT)

FORCE:
