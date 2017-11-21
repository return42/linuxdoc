#!/usr/bin/env python3
# -*- coding: utf-8; mode: python -*-
# pylint: disable=C0103

u"""
    lint
    ~~~~

    Implementation of the ``kernel-lintdoc`` command.

    :copyright:  Copyright (C) 2016  Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    The ``kernel-doclint`` command *lints* documentation from Linux kernel's
    source code comments, see ``--help``::

        $ kernel-lintdoc --help

    .. note::

       The kernel-lintdoc command is under construction, no stable release
       yet. The command-line arguments might be changed/extended in the near
       future."""

# ------------------------------------------------------------------------------
# imports
# ------------------------------------------------------------------------------

import sys
import argparse

#import six

import os
from . import kernel_doc as kerneldoc

# ------------------------------------------------------------------------------
# config
# ------------------------------------------------------------------------------

MSG    = lambda msg: sys.__stderr__.write("INFO : %s\n" % msg)
ERR    = lambda msg: sys.__stderr__.write("ERROR: %s\n" % msg)
FATAL  = lambda msg: sys.__stderr__.write("FATAL: %s\n" % msg)

epilog = u"""This implementation of uses the kernel-doc parser
from the linuxdoc extension, for detail informations read
http://return42.github.io/sphkerneldoc/books/kernel-doc-HOWTO"""

# ------------------------------------------------------------------------------
def main():
# ------------------------------------------------------------------------------

    CLI = argparse.ArgumentParser(
        description = ("Lint *kernel-doc* comments from source code")
        , epilog = epilog
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    CLI.add_argument(
        "srctree"
        , help    = "File or folder of source code."
        , type    = lambda x: os.path.abspath(x))

    CLI.add_argument(
        "--sloppy"
        , action  = "store_true"
        , help    = "Sloppy linting, reports only severe errors.")

    CLI.add_argument(
        "--markup"
        , choices = ["reST", "kernel-doc"]
        , default = "reST"
        , help    = (
            "Markup of the comments. Change this option only if you know"
            " what you do. New comments must be marked up with reST!"))

    CLI.add_argument(
        "--verbose", "-v"
        , action  = "store_true"
        , help    = "verbose output with log messages to stderr" )

    CLI.add_argument(
        "--debug"
        , action  = "store_true"
        , help    = "debug messages to stderr" )

    CMD = CLI.parse_args()
    kerneldoc.DEBUG = CMD.debug
    kerneldoc.VERBOSE = CMD.verbose

    if not CMD.srctree.EXISTS:
        ERR("%s does not exists or is not a folder" % CMD.srctree)
        sys.exit(42)

    if CMD.srctree.ISDIR:
        for fname in CMD.srctree.reMatchFind(r"^.*\.[ch]$"):
            if fname.startswith(CMD.srctree/"Documentation"):
                continue
            lintdoc_file(fname, CMD)
    else:
        fname = CMD.srctree
        CMD.srctree = CMD.srctree.DIRNAME
        lintdoc_file(fname, CMD)

# ------------------------------------------------------------------------------
def lintdoc_file(fname, CMD):
# ------------------------------------------------------------------------------

    fname = fname.relpath(CMD.srctree)
    opts = kerneldoc.ParseOptions(
        rel_fname       = fname
        , src_tree      = CMD.srctree
        , verbose_warn  = not (CMD.sloppy)
        , markup        = CMD.markup )

    parser = kerneldoc.Parser(opts, kerneldoc.NullTranslator())
    try:
        parser.parse()
    except Exception: # pylint: disable=W0703
        FATAL("kernel-doc comments markup of %s seems buggy / can't parse" % opts.fname)
        return
