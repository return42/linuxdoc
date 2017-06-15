# -*- coding: utf-8; mode: makefile-gmake -*-

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx

GIT_URL   = https://github.com/return42/linuxdoc.git
PYOBJECTS = linuxdoc

all: clean pylint pytest build docs

PHONY += help
help:
	@echo  '  docs	- build documentation'
	@echo  '  clean	- remove most generated files'
	@echo  '  rqmts	- info about build requirements'
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

PHONY += api-doc
api-doc: $(PY_ENV)
	rm -rf docs/linuxdoc-api
	$(PY_ENV_BIN)/sphinx-apidoc --separate --maxdepth=0 -o docs/linuxdoc-api linuxdoc
	rm -f docs/linuxdoc-api/modules.rst

PHONY += docs
docs:  sphinx-doc api-doc
	$(call cmd,sphinx,html,docs,docs)

PHONY += clean
clean: pyclean docs-clean
	$(call cmd,common_clean)

PHONY += help-rqmts
rqmts: msg-sphinx-doc msg-pylint-exe msg-pip-exe


.PHONY: $(PHONY)

