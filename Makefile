# -*- coding: utf-8; mode: makefile-gmake -*-

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx

GIT_URL   = https://github.com/return42/linuxdoc.git
PYOBJECTS = linuxdoc
DOC       = docs
API_DOC   = $(DOC)/$(PYOBJECTS)-api

all: clean pylint pytest build docs

PHONY += help
help:
	@echo  '  docs	    - build documentation'
	@echo  '  docs-live - autobuild HTML documentation while editing'
	@echo  '  clean	    - remove most generated files'
	@echo  '  rqmts	    - info about build requirements'
	@echo  ''
	@echo  '  install   - developer install'
	@echo  '  uninstall - developer uninstall'
	@echo  ''
	@$(MAKE) -s -f utils/makefile.include make-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.python python-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.sphinx docs-help

PHONY += install
install: pyinstall

PHONY += uninstall
uninstall: pyuninstall

PHONY += docs
docs:  sphinx-doc $(API_DOC)
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live:  sphinx-live
	$(call cmd,sphinx_autobuild,html,docs,docs)

$(API_DOC): $(PY_ENV)
	$(PY_ENV_BIN)/sphinx-apidoc --separate --maxdepth=0 -o docs/linuxdoc-api linuxdoc
	rm -f $(API_DOC)/modules.rst

PHONY += clean
clean: pyclean docs-clean
	rm -rf ./$(API_DOC)
	$(call cmd,common_clean)

PHONY += help-rqmts
rqmts: msg-sphinx-doc msg-pylint-exe msg-pip-exe


.PHONY: $(PHONY)

