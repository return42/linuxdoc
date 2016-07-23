# -*- coding: utf-8; mode: makefile-gmake -*-

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx

GIT_URL = https://github.com/return42/linuxdoc.git

DOCS_DIST = gh-pages
$(DOCS_DIST):
	git clone $(GIT_URL) $(DOCS_DIST)
	cd $(DOCS_DIST);\
		git push origin :gh-pages ;\
		git checkout --orphan gh-pages;\
		git rm -rf .
	$(call cmd,sphinx,html,docs,docs)
	cd $(DOCS_DIST);\
	        touch .nojekyll ;\
		git add --all . ;\
		git commit -m "gh-pages: updated" ;\
		git push origin gh-pages

all: clean docs build pylint

PHONY += help-rqmts
help-rqmts: msg-sphinx-builder msg-pylint-exe msg-pip-exe

PHONY += help
help:
	@echo  '  un/install	- install/uninstall project in editable mode'
	@echo  '  pybuild	- build python packages'
	@echo  '  docs		- build documentation'
	@echo  '  clean		- remove most generated files'
	@echo  '  pylint	- run pylint *linting*'
	@echo  '  test		- run nose test'
	@echo  '  help-rqmts 	- info about build requirements'
	@echo  ''
	@echo  '  make V=0|1 [targets] 0 => quiet build (default), 1 => verbose build'
	@echo  '  make V=2   [targets] 2 => give reason for rebuild of target'
	@echo  '  make PYTHON=python2 use special python interpreter'


quiet_cmd_clean = CLEAN     $@
      cmd_clean = \
	rm -rf tests/build ;\
	find . -name '*.orig' -exec rm -f {} +     ;\
	find . -name '*.rej' -exec rm -f {} +      ;\
	find . -name '*~' -exec rm -f {} +         ;\
	find . -name '*.bak' -exec rm -f {} +      ;\

PHONY += install uninstall
install: pip-exe
	$(call cmd,pyinstall,.)
uninstall: pip-exe
	$(call cmd,pyuninstall,linuxdoc)

PHONY += docs
docs:  sphinx-builder
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-clean
docs-clean:
	$(call cmd,sphinx_clean)

PHONY += clean
clean: docs-clean pyclean
	$(call cmd,clean)

PHONY += pylint
pylint: pylint-exe
	$(call cmd,pylint,linuxdoc)

PHONY += test
test:
	$(call cmd,test)

.PHONY: $(PHONY)

