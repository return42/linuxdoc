# SPDX-License-Identifier: AGPL-3.0-or-later
"""
lint
~~~~

Implementation of the :ref:`linuxdoc.lintdoc` command.

:copyright:  Copyright (C) 2023  Markus Heiser
:license:    AGPL-3.0-or-later; see LICENSE for details.

The command ``linuxdoc.lint`` *lint* the kernel-doc comments in the source
code::

    $ linuxdoc.lint --help

"""

import sys
import argparse

from fspath import FSPath
from . import kernel_doc

CMD = None

MSG    = lambda msg: sys.__stderr__.write("INFO : %s\n" % msg)
ERR    = lambda msg: sys.__stderr__.write("ERROR: %s\n" % msg)
FATAL  = lambda msg: sys.__stderr__.write("FATAL: %s\n" % msg)

EPILOG = """This command uses the kernel-doc parser from the linuxdoc Sphinx
extension, for details see: https://return42.github.io/linuxdoc/cmd-line.html"""

DESCRIPTION = """Lint the kernel-doc markup comments in the source code files."""

# ------------------------------------------------------------------------------
def main():
# ------------------------------------------------------------------------------

    global CMD  # pylint: disable=global-statement

    cli = get_cli()
    CMD = cli.parse_args()

    kernel_doc.DEBUG = CMD.debug
    kernel_doc.VERBOSE = CMD.verbose

    if not CMD.srctree.EXISTS:
        ERR("%s does not exists or is not a folder" % CMD.srctree)
        sys.exit(42)

    if CMD.srctree.ISDIR:
        for fname in CMD.srctree.reMatchFind(r"^.*\.[ch]$"):
            lintdoc_file(fname)
    else:
        fname = CMD.srctree
        CMD.srctree = CMD.srctree.DIRNAME
        lintdoc_file(fname)


def get_cli():

    cli = argparse.ArgumentParser(
        description = ("")
        , epilog = EPILOG
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    cli.add_argument(
        "srctree"
        , help    = "File or folder of source code."
        , type    = lambda x: FSPath(x).ABSPATH
    )
    cli.add_argument(
        "--sloppy"
        , action  = "store_true"
        , help    = "Sloppy linting, reports only severe errors."
    )
    cli.add_argument(
        "--markup"
        , choices = ["reST", "kernel-doc"]
        , default = "reST"
        , help    = (
            "Markup of the comments.  Change this option only if you know"
            " what you do. New comments must be marked up with reST!"
        )
    )
    cli.add_argument(
        "--verbose", "-v"
        , action  = "store_true"
        , help    = "verbose output with log messages to stderr"
    )
    cli.add_argument(
        "--debug"
        , action  = "store_true"
        , help    = "debug messages to stderr"
    )
    return cli


# ------------------------------------------------------------------------------
def lintdoc_file(fname):
# ------------------------------------------------------------------------------

    "lint documentation from fname"

    fname = fname.relpath(CMD.srctree)
    opts = kernel_doc.ParseOptions(
        fname           = fname
        , src_tree      = CMD.srctree
        , verbose_warn  = not (CMD.sloppy)
        , markup        = CMD.markup
    )
    parser = kernel_doc.Parser(opts, kernel_doc.NullTranslator())
    try:
        parser.parse()
    except Exception:  # pylint: disable=broad-except
        FATAL("kernel-doc comments markup of %s seems buggy / can't parse" % opts.fname)
        return
