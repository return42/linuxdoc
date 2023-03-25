#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
grep_doc
~~~~~~~~

Implementation of the ``linuxdoc.grepdoc`` command.

:copyright:  Copyright (C) 2018 Markus Heiser
:license:    AGPL-3.0-or-later; see LICENSE for details.

The ``linuxdoc.grepdoc`` command *greps* ``.. kernel-doc::`` directives from reST
files::

    $  linuxdoc.grepdoc --help

"""

import argparse
import re
import sys

from fspath import FSPath

CMD = None

PRINT  = lambda msg: sys.__stdout__.write("%s\n" % msg)
ERR    = lambda msg: sys.__stderr__.write("ERROR: %s\n" % msg)

KERNEL_DOC_RE = re.compile(r'^\s*..\s+kernel-doc::\s+([a-zA-Z0-9_\-\.\/]+)')

DESCRIPTION = """The linuxdoc.grepdoc command searches '*.rst' files and filters
all

    .. kernel-doc:: <source files>

directives.  The names of the <source files> used in these kernel-doc directives
are printed out line by line."""


# ------------------------------------------------------------------------------
def main():
# ------------------------------------------------------------------------------

    global CMD  # pylint: disable=global-statement

    cli = get_cli()
    CMD = cli.parse_args()

    if not CMD.srctree.EXISTS:
        ERR("%s does not exists." % CMD.srctree)
        sys.exit(42)

    if not CMD.srctree.ISDIR:
        ERR("%s is not a folder." % CMD.srctree)
        sys.exit(42)

    rst_sources = set()
    doc_tree = CMD.srctree
    for fname in doc_tree.reMatchFind(r"^.*\.rst$"):
        for line in fname.openTextFile():
            _m = KERNEL_DOC_RE.search(line)
            if _m:
                rst_sources.add(_m.group(1))

    rst_sources = list(rst_sources)
    rst_sources.sort()
    PRINT("\n".join(rst_sources))

def get_cli():

    cli = argparse.ArgumentParser(
        description = DESCRIPTION
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cli.add_argument(
        "srctree"
        , help    = "source tree"
        , type    = lambda x: FSPath(x).ABSPATH
    )

    return cli
