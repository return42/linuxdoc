# -*- coding: utf-8; mode: makefile-gmake -*-

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx
include utils/makefile.0

GIT_URL   = https://github.com/return42/linuxdoc.git
PYOBJECTS = linuxdoc
DOC       = docs
#SLIDES    = docs/slides
API_DOC   = $(DOC)/$(PYOBJECTS)-api

all: clean pylint pytest build docs

PHONY += help help-min help-all

help: help-min
	@echo  ''
	@echo  'to get more help:  make help-all'

help-min:
	@echo  '  docs      - build documentation'
	@echo  '  docs-live - autobuild HTML documentation while editing'
	@echo  '  clean     - remove most generated files'
	@echo  '  install   - developer install (./local)'
	@echo  '  uninstall - uninstall (./local)'
	@echo  '  rqmts	    - info about build requirements'
	@echo  ''
	$(Q)$(MAKE) -e -s make-help

help-all: help-min
	@echo  ''
	$(Q)$(MAKE) -e -s docs-help
	@echo  ''
	$(Q)$(MAKE) -e -s python-help

PHONY += install
install: pyenvinstall

PHONY += uninstall
uninstall: pyenvuninstall

PHONY += docs
docs:  docs-man $(API_DOC)
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live: pyenvinstall docs-man
	$(call cmd,sphinx_autobuild,html,$(DOCS_FOLDER),$(DOCS_FOLDER))

PHONY += docs-man
docs-man: pyenvinstall $(API_DOC)
	$(call cmd,sphinx,kernel-doc-man,docs,docs,man)
	find $(DOCS_DIST)/man -name '*.[0-9]' -exec gzip -nf {} +

#PHONY += slides
#slides:  pyenvinstall
#	$(call cmd,sphinx,html,$(SLIDES),$(SLIDES),slides)

PHONY += project
project: pyenvinstall $(API_DOC)
	@echo '  PROJECT   requirements.txt'
	$(Q)- rm -f requirements.txt
	$(Q)$(PY_ENV_BIN)/python -c "from linuxdoc.__pkginfo__ import *; print(requirements_txt)" > ./requirements.txt
	$(Q)$(PY_ENV_BIN)/python -c "from linuxdoc.__pkginfo__ import *; print(README)" > README.rst

PHONY += $(API_DOC)
$(API_DOC): $(PY_ENV)
	$(Q)rm -rf ./$(API_DOC)
	$(Q)$(PY_ENV_BIN)/sphinx-apidoc --separate --maxdepth=0 -o $(API_DOC) linuxdoc linuxdoc/cdomainv2.py linuxdoc/cdomainv3.py
	$(Q)rm -f $(API_DOC)/modules.rst

PHONY += clean
clean: pyclean docs-clean
	@rm -rf ./$(API_DOC)
	$(call cmd,common_clean)

PHONY += rqmts
rqmts: msg-python-exe msg-pip-exe

PHONY += zero_pylint
zero_pylint: pylint-exe
	$(call cmd,pylint,$(PYOBJECTS)) | grep '^[\*\*\*\*\*\*|linuxdoc]' > 0_pylint_py$(PY)


## ------------------------------------------------------------------------------
## zero.build: add linux kernel's sphinx-books
## ------------------------------------------------------------------------------
##
## A simple zero build workflow to compare builds from linuxdoc current working
## tree with build commit at HEAD~~~:
##
## 1. initialize:               ``make 0.drop``
## 2. build HEAD~~~ and commit: ``make COMMIT='HEAD~~~' zero 0.commit``
## 3. build with working tree:  ``make zero 0.status``
##
## The ``0.status`` will show you differences between both builds.  To see
## detail changes use::
##
##    git -C ./0_build diff
##

## zero.docxml
## ------------
##
## To track changes in the builder (generated output), add XML output of ./docs
## as zero.build target.
##
PHONY += zero.docxml
zero.doc2xml:
	cp -f ./Makefile $(0_BUILD_WTREE) || exit 0 > /dev/null
	cd $(0_BUILD_WTREE); $(MAKE) DOCS_DIST=$(abspath $(0_BUILD_DEST))/doc2xml docs.xml
	find $(0_BUILD_DEST)/doc2xml -type f -exec sed -i "s/build\/0_build_worktree\///g" {} \;

zero.build:: zero.doc2xml

PHONY += docs
docs.xml:  pyenvinstall $(API_DOC)
	$(call cmd,sphinx,xml,docs,docs)


.PHONY: $(PHONY)
