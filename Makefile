# -*- coding: utf-8; mode: makefile-gmake -*-

include utils/makefile.include
include utils/makefile.python
include utils/makefile.sphinx

GIT_URL = https://github.com/return42/linuxdoc.git
PYOBJECTS = linuxdoc

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
help-rqmts: msg-sphinx-doc msg-pylint-exe msg-pip-exe

PHONY += help
help:
	@echo  'Makefile:'
	@echo  '  un/install	- install/uninstall project in editable mode'
	@echo  '  docs		- build documentation'
	@echo  '  clean		- remove most generated files'
	@echo  '  test		- run nose test'
	@echo  '  help-rqmts 	- info about build requirements'
	@echo  ''
	@$(MAKE) -s -f utils/makefile.include make-help
	@echo  ''
	@$(MAKE) -s -f utils/makefile.python python-help

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
docs:  sphinx-doc
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-clean
docs-clean:
	$(call cmd,sphinx_clean)

PHONY += clean
clean: docs-clean pyclean
	$(call cmd,clean)

PHONY += test
test:
	$(call cmd,test)

.PHONY: $(PHONY)

