# SPDX-License-Identifier: AGPL-3.0-or-later
"""
rest
~~~~

Implementation of the ``linuxdoc.rest`` command.

:copyright:  Copyright (C) 2023 Markus Heiser
:license:    AGPL-3.0-or-later; see LICENSE for details.

The ``linuxdoc.rest`` command parses kernel-doc comments from source code and
print the reST to stdout::

    $ linuxdoc.rest --help

"""

from fspath import FSPath
import argparse
from . import kernel_doc

CMD = None

EPILOG = """This command uses the kernel-doc parser from the linuxdoc Sphinx
extension, for details see: https://return42.github.io/linuxdoc/cmd-line.html"""

DESCRIPTION = """ The linuxdoc.rest command converts the kernel-doc markup
comments in the source code files to reST markup.  """

# ------------------------------------------------------------------------------
def main():
# ------------------------------------------------------------------------------

    global CMD  # pylint: disable=global-statement

    cli = get_cli()
    CMD = cli.parse_args()

    kernel_doc.VERBOSE = CMD.verbose
    kernel_doc.DEBUG   = CMD.debug

    if CMD.quiet:
        kernel_doc.STREAM.log_out = kernel_doc.DevNull

    retVal = 0

    src_tree = FSPath.getCWD()
    for fname in CMD.files:
        fname = FSPath(fname)
        translator = kernel_doc.ReSTTranslator()
        opts = kernel_doc.ParseOptions(
            fname           = fname.relpath(src_tree)
            , src_tree      = src_tree
            , id_prefix     = CMD.id_prefix
            , skip_preamble = CMD.skip_preamble
            , skip_epilog   = CMD.skip_epilog
            , out           = kernel_doc.STREAM.appl_out
            , markup        = CMD.markup
            , verbose_warn  = not (CMD.sloppy)
            , exp_method    = CMD.symbols_exported_method
            , exp_ids       = CMD.symbols_exported_identifiers
            , known_attrs   = CMD.known_attrs
        )
        opts.set_defaults()

        if CMD.list_exports or CMD.list_internals:
            translator = kernel_doc.ListTranslator(CMD.list_exports, CMD.list_internals)
            opts.gather_context = True

        elif CMD.use_names:
            opts.use_names  = CMD.use_names

        elif CMD.exported or CMD.internal:
            # gather exported symbols ...
            src   = kernel_doc.readFile(opts.fname)
            ctx   = kernel_doc.ParserContext()
            kernel_doc.Parser.gather_context(src, ctx, opts)

            opts.error_missing = False
            opts.use_names     = ctx.exported_symbols
            opts.skip_names    = []

            if CMD.internal:
                opts.use_names  = []
                opts.skip_names = ctx.exported_symbols
        else:
            # if non section is choosen by use-name, internal or exclude, then
            # use all DOC: sections
            opts.use_all_docs = True

        parser = kernel_doc.Parser(opts, translator)
        parser.parse()
        parser.close()
        if parser.errors:
            retVal = 1

    return retVal


def get_cli():

    cli = argparse.ArgumentParser(
        description = DESCRIPTION
        , epilog = EPILOG
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    cli.add_argument(
        "files"
        , nargs   = "+"
        , help    = "source file(s) to parse."
    )
    cli.add_argument(
        "--id-prefix"
        , default = ""
        , help    = (
            "A prefix for automatic generated IDs.  The IDs are automaticly"
            " gernerated based on the declaration and/or section names.  The"
            " prefix is also used as namespace in Sphinx's C-domain"
        )
    )
    cli.add_argument(
        "--verbose", "-v"
        , action  = "store_true"
        , help    = "verbose output with log messages to stderr"
    )
    cli.add_argument(
        "--sloppy"
        , action  = "store_true"
        , help    = "Sloppy linting, reports only severe errors."
    )
    cli.add_argument(
        "--debug"
        , action  = "store_true"
        , help    = "debug messages to stderr"
    )
    cli.add_argument(
        "--quiet", "-q"
        , action  = "store_true"
        , help    = "no messages to stderr"
    )
    cli.add_argument(
        "--skip-preamble"
        , action  = "store_true"
        , help    = "skip preamble in the output"
    )
    cli.add_argument(
        "--skip-epilog"
        , action  = "store_true"
        , help    = "skip epilog in the output"
    )
    cli.add_argument(
        "--list-internals"
        , choices = kernel_doc.Parser.DOC_TYPES + ["all"]
        , nargs   = "+"
        , help    = "List symbols, titles or whatever is documented, but *not* exported."
    )
    cli.add_argument(
        "--list-exports"
        , action  = "store_true"
        , help    = "List all exported symbols."
    )
    cli.add_argument(
        "--use-names"
        , nargs   = "+"
        , help    = (
            "Print reST markup of functions, structs or whatever title/object"
        )
    )
    cli.add_argument(
        "--exported"
        , action  = "store_true"
        , help    = "Print documentation of all exported symbols."
    )
    cli.add_argument(
        "--internal"
        , action  = "store_true"
        , help    = (
            "Print documentation of all symbols that are documented,"
            " but not exported"
        )
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
        "--symbols-exported-method"
        , default = kernel_doc.DEFAULT_EXP_METHOD
        , help    = (
            "Indicate the way by which an exported symbol"
            " is exported. Must be either 'macro' or 'attribute'."
        )
    )
    cli.add_argument(
        "--symbols-exported-identifiers"
        , nargs   = "+"
        , default = kernel_doc.DEFAULT_EXP_IDS
        , help    = "Identifiers list that specifies an exported symbol."
    )
    cli.add_argument(
        "--known-attrs"
        , default = []
        , nargs   = "+"
        , help    = (
            "Provides a list of known attributes that has to be"
            " hidden when displaying function prototypes"
        )
    )

    return cli
