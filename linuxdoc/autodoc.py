#!/usr/bin/env python3
# -*- coding: utf-8; mode: python -*-
u"""
    autodoc
    ~~~~~~~

    Implementation of the ``kernel-autodoc`` command.

    :copyright:  Copyright (C) 2018 Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    The ``kernel-autodoc`` command extracts documentation from Linux kernel's
    source code comments, see ``--help``::

        $ kernel-autodoc --help

"""

# ------------------------------------------------------------------------------
# imports
# ------------------------------------------------------------------------------

import sys
import argparse
import multiprocessing

import six

from fspath import FSPath
from . import kernel_doc as kerneldoc
from .kernel_doc import Container


# ------------------------------------------------------------------------------
# config
# ------------------------------------------------------------------------------

MARKUP = "kernel-doc" # "reST"
MSG    = lambda msg: sys.__stderr__.write("INFO : %s\n" % msg)
ERR    = lambda msg: sys.__stderr__.write("ERROR: %s\n" % msg)
FATAL  = lambda msg: sys.__stderr__.write("FATAL: %s\n" % msg)

TEMPLATE_INDEX="""\
.. -*- coding: utf-8; mode: rst -*-

================================================================================
%(title)s
================================================================================

.. toctree::
    :maxdepth: 1

"""

EPILOG = u"""This implementation of autodoc uses the kernel-doc parser from the linuxdoc
extension, for details see: https://return42.github.io/linuxdoc/cmd-line.html"""

CMD = None

# ------------------------------------------------------------------------------
def main():
# ------------------------------------------------------------------------------

    "Parse *kernel-doc* comments from source code (main)"

    global CMD  # pylint: disable=global-statement

    CLI = argparse.ArgumentParser(  # pylint: disable=invalid-name
        description = ("Parse *kernel-doc* comments from source code")
        , epilog = EPILOG
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    CLI.add_argument(
        "srctree"
        , help    = "Folder of source code."
        , type    = lambda x: FSPath(x).ABSPATH)

    CLI.add_argument(
        "doctree"
        , help    = "Folder to place reST documentation."
        , type    = lambda x: FSPath(x).ABSPATH)

    CLI.add_argument(
        "--sloppy"
        , action  = "store_true"
        , help    = "Sloppy comment check, reports only severe errors.")

    CLI.add_argument(
        "--force"
        , action  = "store_true"
        , help    = "Don't stop if doctree exists.")

    CLI.add_argument(
        "--threads"
        , type    =  int
        , default = multiprocessing.cpu_count()
        , help    = "Use up to n threads.")

    CLI.add_argument(
        "--markup"
        , choices = ["reST", "kernel-doc"]
        , default = "reST"
        , help    = (
            "Markup of the comments. Change this option only if you know"
            " what you do. New comments must be marked up with reST!"))

    CLI.add_argument(
        "--rst-files"
        , type    = lambda x: FSPath(x).ABSPATH
        , help    = (
            "File that list source files, which has comments in reST markup."
            " Use kernel-grepdoc command to generate those file."))

    CMD = CLI.parse_args()

    if not CMD.srctree.EXISTS:
        ERR("%s does not exists." % CMD.srctree)
        sys.exit(42)

    if not CMD.srctree.ISDIR:
        ERR("%s is not a folder." % CMD.srctree)
        sys.exit(42)

    if not CMD.force and CMD.doctree.EXISTS:
        ERR("%s is in the way, remove it first" % CMD.doctree)
        sys.exit(42)

    if CMD.markup == "kernel-doc" and CMD.rst_files:
        CMD.rst_files = CMD.rst_files.readFile().splitlines()
    else:
        CMD.rst_files = []

    if CMD.threads > 1:
        pool = multiprocessing.Pool(CMD.threads)
        pool.map(autodoc_file, gather_filenames(CMD))
        pool.close()
        pool.join()
    else:
        for fname in gather_filenames(CMD):
            autodoc_file(fname)

    insert_index_files(CMD.doctree)

# ------------------------------------------------------------------------------
def gather_filenames(cmd):
# ------------------------------------------------------------------------------

    "yield .c & .h filenames"

    for fname in cmd.srctree.reMatchFind(r"^.*\.[ch]$"):
        if fname.startswith(CMD.srctree/"Documentation"):
            continue
        yield fname

# ------------------------------------------------------------------------------
def autodoc_file(fname):
# ------------------------------------------------------------------------------

    "generate documentation from fname"

    fname  = fname.relpath(CMD.srctree)
    markup = CMD.markup

    if CMD.markup == "kernel-doc" and fname in CMD.rst_files:
        markup = "reST"

    opts = kerneldoc.ParseOptions(
        rel_fname       = fname
        , src_tree      = CMD.srctree
        , verbose_warn  = not (CMD.sloppy)
        , use_all_docs  = True
        , markup        = markup )

    parser = kerneldoc.Parser(opts, kerneldoc.NullTranslator())
    try:
        parser.parse()
    except Exception:  # pylint: disable=broad-except
        FATAL("kernel-doc markup of %s seems buggy / can't parse" % opts.fname)
        return

    if not parser.ctx.dump_storage:
        # no kernel-doc comments found
        MSG("parsed: NONE comments: %s" % opts.fname)
        return

    MSG("parsed: %4d comments: %s" % (len(parser.ctx.dump_storage), opts.fname))

    try:
        rst = six.StringIO()
        translator = kerneldoc.ReSTTranslator()
        opts.out   = rst

        # First try to output reST, this might fail, because the kernel-doc
        # parser part is to tollerant ("bad lines", "function name and function
        # declaration are different", etc ...).
        parser.parse_dump_storage(translator=translator)

        out_file = CMD.doctree / fname.replace(".","_") + ".rst"
        out_file.DIRNAME.makedirs()
        with out_file.openTextFile(mode="w") as out:
            out.write(rst.getvalue())

    except Exception:  # pylint: disable=broad-except
        FATAL("kernel-doc markup of %s seems buggy / can't parse" % opts.fname)
        return

# ------------------------------------------------------------------------------
def insert_index_files(root_folder):
# ------------------------------------------------------------------------------

    "From root_folder traverse over subfolders and generate all index.rst files "

    for folder, dirnames, filenames in root_folder.walk():
        ctx = Container( title = folder.FILENAME )
        dirnames.sort()
        filenames.sort()
        index_file = folder / "index.rst"
        MSG("create index: %s" % index_file)
        with index_file.openTextFile(mode="w") as index:
            index.write(TEMPLATE_INDEX % ctx)
            for _d in dirnames:
                index.write("    %s/index\n" % _d.FILENAME)
            for _f in filenames:
                if _f.FILENAME == "index":
                    continue
                index.write("    %s\n" % _f.FILENAME)
