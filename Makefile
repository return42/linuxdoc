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
install: pyinstall

PHONY += uninstall
uninstall: pyuninstall

PHONY += docs
docs:  docs-man $(API_DOC)
	$(call cmd,sphinx,html,docs,docs)

PHONY += docs-live
docs-live: docs-man
	$(call cmd,sphinx_autobuild,html,docs,docs)

PHONY += docs-man
docs-man: pyenv-install sphinx-doc $(API_DOC)
	$(call cmd,sphinx,kernel-doc-man,docs,docs,man)
	find $(DOCS_DIST)/man -name '*.[0-9]' -exec gzip -nf {} +

#PHONY += slides
#slides:  sphinx-doc
#	$(call cmd,sphinx,html,$(SLIDES),$(SLIDES),slides)

PHONY += $(API_DOC)
$(API_DOC): $(PY_ENV)
	$(Q)rm -rf ./$(API_DOC)
	$(Q)$(PY_ENV_BIN)/sphinx-apidoc --separate --maxdepth=0 -o $(API_DOC) linuxdoc
	$(Q)rm -f $(API_DOC)/modules.rst

PHONY += clean
clean: pyclean docs-clean
	@rm -rf ./$(API_DOC)
	$(call cmd,common_clean)

PHONY += rqmts
rqmts: msg-python-exe msg-pip-exe msg-virtualenv-exe

PHONY += zero_pylint
zero_pylint: pylint-exe
	$(call cmd,pylint,$(PYOBJECTS)) | grep '^[\*\*\*\*\*\*|linuxdoc]' > 0_pylint_py$(PY)


## srctree variable
## ----------------
##
## Path where Kernel's sources cloned, default is ``../linux``.::
##
##     git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git linux
##
srctree ?= ../linux

# zero build's CWD is ./build/0_build_worktree: srctree has to be abspath
srctree ::= $(abspath $(srctree))
export srctree

PHONY += diff_linux
diff_linux:
	git -C $(srctree) diff > docs/downloads/patch_linux.patch

PHONY += patch_linux
patch_linux:
	git -C $(srctree) apply $(PWD)/docs/downloads/patch_linux.patch

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
docs.xml:  pyenv-install sphinx-doc $(API_DOC)
	$(call cmd,sphinx,xml,docs,docs)

KERNEL_DOC=$(srctree)/Documentation

## zero.src2rst
## ------------
##
## To track changes of the kernel-doc parser (generated output), add linux
## autodoc sources to reST as one zero.build target.  Require Kernel's sources
## at `srctree variable`_.
##
PHONY += zero.src2rst
zero.src2rst: $(PY_ENV) src-reST-Files
	rm -rf $(AUTODOC_FOLDER)
	$(AUTODOC_SCRIPT)  --markup kernel-doc --rst-files $(0_BUILD_DEST)/src-reST-Files.txt $(srctree) $(AUTODOC_FOLDER)

zero.build:: zero.src2rst

# kernel's sphinx-books
AUTODOC_SCRIPT := $(PY_ENV_BIN)/kernel-autodoc
AUTODOC_FOLDER := $(0_BUILD_DEST)/autodoc.linux

PHONY += src-reST-Files
src-reST-Files: $(PY_ENV)
	$(PY_ENV_BIN)/$(PYTHON) ./kernel-docgrep $(KERNEL_DOC) > $(0_BUILD_DEST)/src-reST-Files.txt



# FIXME: media not yet work
#KERNEL_BOOKS   = $(filter-out media,$(patsubst $(KERNEL_DOC)/%/conf.py,%,$(wildcard $(KERNEL_DOC)/*/conf.py)))
#KERNEL_0_BUILD = $(patsubst %,books/%.zero, $(KERNEL_BOOKS))
#
# zero.build:: $(KERNEL_0_BUILD)
#
#PHONY += $(KERNEL_0_BUILD)
#$(KERNEL_0_BUILD):
#	@echo "  ZERO-BUILD   $@"
#	$(call cmd,kernel_book,xml,$(patsubst books/%.zero,%,$@),xml,$(KERNEL_DOC))
#
#
# $2 sphinx builder e.g. "html"
# $3 name of the book / e.g. "gpu", used as:
#    * dest folder relative to $(DIST_BOOKS) and
#    * cache folder relative to $(DOCS_BUILD)/$3.doctrees
# $4 dest subfolder e.g. "man" for man pages at gpu/man
# $5 reST source folder,
#    e.g. "$(BOOKS_MIGRATED_FOLDER)" for the migrated books
#
# quiet_cmd_kernel_book = $(shell echo "     $2" | tr '[:lower:]' '[:upper:]')     --> file://$(abspath $(0_BUILD_DEST)/$3/$4)
#       cmd_kernel_book = SPHINX_CONF=$(abspath $5/$3/conf.py) \
# 	$(SPHINXBUILD) \
# 	$(ALLSPHINXOPTS) \
# 	-b $2 \
# 	-c docs \
# 	-d $(DOCS_BUILD)/$3.doctrees \
# 	$(abspath $5/$3) \
# 	$(abspath $(0_BUILD_DEST)/$3/$4)

.PHONY: $(PHONY)

