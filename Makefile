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
	@$(PY_ENV_BIN)/pip install $(PIP_VERBOSE) -e .
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live:  sphinx-live $(API_DOC)
	@$(PY_ENV_BIN)/pip install $(PIP_VERBOSE) -e .
	$(call cmd,sphinx_autobuild,html,docs,docs)

#PHONY += slides
#slides:  sphinx-doc
#	$(call cmd,sphinx,html,$(SLIDES),$(SLIDES),slides)

$(API_DOC): $(PY_ENV)
	$(PY_ENV_BIN)/sphinx-apidoc --separate --maxdepth=0 -o docs/linuxdoc-api linuxdoc
	@rm -f $(API_DOC)/modules.rst

PHONY += clean
clean: pyclean docs-clean
	@rm -rf ./$(API_DOC)
	$(call cmd,common_clean)

PHONY += rqmts
rqmts: msg-python-exe msg-pip-exe msg-virtualenv-exe

PHONY += zero_pylint
zero_pylint: pylint-exe
	$(call cmd,pylint,$(PYOBJECTS)) | grep '^[\*\*\*\*\*\*|linuxdoc]' > 0_pylint_py$(PY)

# ------------------------------------------------------------------------------
# zero.build: add linux kernel's sphinx-books
# ------------------------------------------------------------------------------

# user linux Kernel documentation as build-reference
srctree ?= /share/linux
export srctree

KERNEL_DOC=$(srctree)/Documentation
# FIXME: media not yet work
KERNEL_BOOKS   = $(filter-out media,$(patsubst $(srctree)/Documentation/%/conf.py,%,$(wildcard $(KERNEL_DOC)/*/conf.py)))
KERNEL_0_BUILD = $(patsubst %,books/%.zero, $(KERNEL_BOOKS))

zero.build:: $(KERNEL_0_BUILD)

PHONY += $(KERNEL_0_BUILD)
$(KERNEL_0_BUILD):
	@echo "  ZERO-BUILD   $@"
	$(call cmd,kernel_book,xml,$(patsubst books/%.zero,%,$@),xml,$(KERNEL_DOC))

# $(KERNEL_0_BUILD):
# 	@echo "test123" > $(0_BUILD_DEST)/$@
# 	@mkdir -p $(0_BUILD_DEST)/books


# $2 sphinx builder e.g. "html"
# $3 name of the book / e.g. "gpu", used as:
#    * dest folder relative to $(DIST_BOOKS) and
#    * cache folder relative to $(DOCS_BUILD)/$3.doctrees
# $4 dest subfolder e.g. "man" for man pages at gpu/man
# $5 reST source folder,
#    e.g. "$(BOOKS_MIGRATED_FOLDER)" for the migrated books

quiet_cmd_kernel_book = $(shell echo "     $2" | tr '[:lower:]' '[:upper:]')     --> file://$(abspath $(0_BUILD_DEST)/$3/$4)
      cmd_kernel_book = SPHINX_CONF=$(abspath $5/$3/conf.py) \
	$(SPHINXBUILD) \
	$(ALLSPHINXOPTS) \
	-b $2 \
	-c docs \
	-d $(DOCS_BUILD)/$3.doctrees \
	$(abspath $5/$3) \
	$(abspath $(0_BUILD_DEST)/$3/$4)

.PHONY: $(PHONY)
