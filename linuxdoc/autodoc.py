# SPDX-License-Identifier: AGPL-3.0-or-later
"""
autodoc
~~~~~~~

Implementation of the ``linuxdoc.autodoc`` command.

:copyright:  Copyright (C) 2023 Markus Heiser
:license:    AGPL-3.0-or-later; see LICENSE for details.

The command ``linuxdoc.autodoc`` extracts the kernel-doc comments from the
source code and uses them to create documentation of the source code in the reST
markup::

    $ linuxdoc.autodoc --help

"""

import sys
import argparse
import multiprocessing

import six

from fspath import FSPath
from . import kernel_doc as kerneldoc
from .kernel_doc import Container

CMD = None

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

EPILOG = """This command uses the kernel-doc parser from the linuxdoc Sphinx
extension, for details see: https://return42.github.io/linuxdoc/cmd-line.html"""

DESCRIPTION = """The linuxdoc.autodoc tool can be used to generate documentation
in the reST markup from the kernel-doc markup comments in the source files.
This tool can be used to create an analogous document structure in reST markup
from the folder structure of the source code.  """

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

    if not CMD.force and CMD.doctree.EXISTS:
        ERR("%s is in the way, remove it first" % CMD.doctree)
        sys.exit(42)

    if CMD.markup == "kernel-doc" and CMD.rst_files:
        CMD.rst_files = CMD.rst_files.readFile().splitlines()
    else:
        CMD.rst_files = []

    if CMD.threads > 1:
        # pylint: disable=consider-using-with
        pool = multiprocessing.Pool(CMD.threads)
        pool.map(autodoc_file, gather_filenames(CMD))
        pool.close()
        pool.join()
    else:
        for fname in gather_filenames(CMD):
            autodoc_file(fname)

    insert_index_files(CMD.doctree)

def get_cli():

    cli = argparse.ArgumentParser(
        description = DESCRIPTION
        , epilog = EPILOG
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cli.add_argument(
        "srctree"
        , help    = "Folder of source code."
        , type    = lambda x: FSPath(x).ABSPATH
    )
    cli.add_argument(
        "doctree"
        , help    = "Folder to place reST documentation."
        , type    = lambda x: FSPath(x).ABSPATH
    )
    cli.add_argument(
        "--sloppy"
        , action  = "store_true"
        , help    = "Sloppy comment check, reports only severe errors."
    )
    cli.add_argument(
        "--force"
        , action  = "store_true"
        , help    = "Don't stop if doctree exists."
    )
    cli.add_argument(
        "--threads"
        , type    =  int
        , default = multiprocessing.cpu_count()
        , help    = "Use up to n threads."
    )
    cli.add_argument(
        "--markup"
        , choices = ["reST", "kernel-doc"]
        , default = "reST"
        , help    = (
            "Markup of the comments.  Change this option only if you know what"
            " you do and make use of --rst-files if you also have some files in"
            " your source tree with reST markup.  The markup of new comments must"
            " be reST!"
        )
    )
    cli.add_argument(
        "--rst-files"
        , type    = lambda x: FSPath(x).ABSPATH
        , help    = (
            "File that list source files, which has comments in reST markup."
            " Use linuxdoc.grepdoc command to generate those file."
        )
    )

    return cli


# ------------------------------------------------------------------------------
def gather_filenames(cmd):
# ------------------------------------------------------------------------------

    "yield .c & .h filenames"

    for fname in cmd.srctree.reMatchFind(r"^.*\.[ch]$"):
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
        fname           = fname
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
