#############################################################################
# Copyright (c) 2017-2020 SiteWare Corp. All right reserved
#############################################################################
SD2_VERSION := 0.22.0

TOP := $(realpath ..)
SD2OS := $(shell uname)
OUT := $(TOP)/out/$(SD2OS)

export PYTHONPATH := $(PYTHONPATH):$(TOP)/src/lib
export PATH := $(PATH):$(HOME)/.local/bin

PYTHON_SOURCES := $(shell find $(TOP)/src -name '*.py')
PYTHON_CHECKED := $(patsubst %.py,$(OUT)/checked/%.py.checked,$(PYTHON_SOURCES))
PYTHON_CHECKED := $(filter-out %sd2_config_schema.py.checked,$(PYTHON_CHECKED))
JSON_SOURCES := $(shell find $(TOP)/src -name '*.json')
JSON_CHECKED := $(patsubst %.json,$(OUT)/checked/%.json.checked,$(JSON_SOURCES))
BASH_SOURCES := $(shell find $(TOP)/src -name '*.sh')
BASH_CHECKED := $(patsubst %.sh,$(OUT)/checked/%.sh.checked,$(BASH_SOURCES))
DOCKER_SOURCES := $(shell find $(TOP)/src -name 'Dockerfile')
DOCKER_CHECKED := $(patsubst %,$(OUT)/checked/%.checked,$(DOCKER_SOURCES))
SOURCES_CHECKED := $(PYTHON_CHECKED) $(JSON_CHECKED) $(BASH_CHECKED) $(DOCKER_CHECKED)

all: all-sd2 \
	 build-sd2ui \
     FORCE

all-sd2: $(TOP)/src/lib/sd2/sd2_config_schema.py \
     $(TOP)/src/lib/sd2/version.py \
     $(SOURCES_CHECKED) \
     $(OUT)/.lint \
	 $(OUT)/.lint-py3k \
     build \
	 FORCE

build:
	(rm -rf $(OUT)/install && \
	 mkdir -p $(OUT)/install && \
	 cd $(OUT)/install && \
	 pyinstaller -F $(TOP)/src/bin/sd2 && \
	 cp dist/sd2 dist/sd2-$(SD2OS))


build-sd2ui:
ifeq ($(shell uname),Darwin)
	(cd $(TOP)/macos && \
     xcodebuild build \
	)
else
	echo No sd2ui for this platform
endif

test: build
	(cd $(TOP)/src && \
	 pytest)

$(OUT)/.lint-py3k: $(PYTHON_SOURCES)
	pylint --py3k $(PYTHON_SOURCES)
	touch $@

$(OUT)/.lint: $(PYTHON_SOURCES)
	pylint -E $(PYTHON_SOURCES)
	touch $@

$(SOURCES_CHECKED): $(OUT)/checked/%.checked: %
	echo Checking $(<F) for tabs and long lines
	$(TOP)/build/check_code_style.py $<
	mkdir -p $(@D)
	touch $@

$(TOP)/src/lib/sd2/version.py: $(TOP)/build/Makefile
	rm -rf $@
	echo "version='$(SD2_VERSION)'" > $@
	chmod -w $@

$(TOP)/src/lib/sd2/sd2_config_schema.py: $(TOP)/src/lib/sd2/sd2_config_schema.json
	rm -f $@
	echo '#Geneareted file. Do not modify' >> $@
	echo "sd2_config_schema = '''" >> $@
	cat $< >> $@
	echo "'''" >> $@
	chmod -w $@

push: test all
	(git tag -d rel_$(SD2_VERSION) && git push origin :refs/tags/rel_$(SD2_VERSION)) || true
	git tag rel_$(SD2_VERSION)
	git push origin HEAD && git push --tags

unpush:
	git tag -d rel_$(SD2_VERSION) && git push origin :refs/tags/rel_$(SD2_VERSION)

clean:
	rm -rf $(OUT) $(TOP)/src/lib/sd2/sd2_config_schema.py
	rm -rf $(TOP)/src/lib/sd2/version.py
ifeq ($(shell uname),Darwin)
	(cd $(TOP)/macos && \
     xcodebuild clean \
	)
endif

FORCE:
