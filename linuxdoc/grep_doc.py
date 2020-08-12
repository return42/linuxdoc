#!/usr/bin/env python3
# -*- coding: utf-8; mode: python -*-
u"""
    grep_doc
    ~~~~~~~~

    Implementation of the ``kernel-grepdoc`` command.

    :copyright:  Copyright (C) 2018 Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    The ``kernel-grepdoc`` command *greps* informations from Linux kernel's
    (reST) documentation, see ``--help``::

        $ kernel-grepdoc --help
"""

# ------------------------------------------------------------------------------
# imports
# ------------------------------------------------------------------------------

import argparse
import re
import sys

from fspath import FSPath

DESCRIPTION = """ The 'kernel-grepdoc' command scans ``*.rst`` files from kernel's
``./Documentation`` source tree and filters all 'kernel-doc' directives.  The
source files which are used in those 'kernel-doc' directives are printed out as
list.  This list can be used to identify which files from the source tree has
already been ported to reST markup and which not.  You will need those sort of
list to distinguish between source files in *reST* and those in *vintage*
kernel-doc mode."""

# ------------------------------------------------------------------------------
# config
# ------------------------------------------------------------------------------

PRINT  = lambda msg: sys.__stdout__.write("%s\n" % msg)
ERR    = lambda msg: sys.__stderr__.write("ERROR: %s\n" % msg)

KERNEL_DOC_RE = re.compile(r'^\s*..\s+kernel-doc::\s+([a-zA-Z0-9_\-\.\/]+)')

# ------------------------------------------------------------------------------
def main(): # pylint: disable=missing-docstring
# ------------------------------------------------------------------------------

    CLI = argparse.ArgumentParser(  # pylint: disable=invalid-name
        description = DESCRIPTION
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    CLI.add_argument(
        "srctree"
        , help    = "Linux's source tree"
        , type    = lambda x: FSPath(x).ABSPATH)

    CMD = CLI.parse_args()  # pylint: disable=invalid-name

    if not CMD.srctree.EXISTS:
        ERR("%s does not exists." % CMD.srctree)
        sys.exit(42)

    if not CMD.srctree.ISDIR:
        ERR("%s is not a folder." % CMD.srctree)
        sys.exit(42)

    rst_sources = set()
    doc_tree = CMD.srctree/"Documentation"
    for fname in doc_tree.reMatchFind(r"^.*\.rst$"):
        if fname.BASENAME == 'kernel-documentation.rst':
            continue
        #MSG("scan %s" % fname)
        for line in fname.openTextFile():
            _m = KERNEL_DOC_RE.search(line)
            if _m:
                rst_sources.add(_m.group(1))

    rst_sources = list(rst_sources)
    rst_sources.sort()
    PRINT("\n".join(rst_sources))
