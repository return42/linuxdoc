# -*- coding: utf-8; mode: python -*-
# pylint: disable=R0912,R0914,R0915,W0221

u"""
    rstKernelDoc
    ~~~~~~~~~~~~

    Implementation of the ``kernel-doc`` reST-directive.

    :copyright:  Copyright (C) 2016  Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    The ``kernel-doc`` (:py:class:`KernelDoc`) directive includes contend from
    linux kernel source code comments.

    Here is a short overview of the options:

    .. code-block:: rst

        .. kernel-doc:: <src-filename>
            :doc: <section title>
            :no-header:
            :export:
            :internal:
            :exp-method:  <method>
            :exp-ids:     <identifier [, identifiers [, ...]]>
            :known-attrs: <attr [, attrs [, ...]]>
            :functions: <function [, functions [, ...]]>
            :module:    <prefix-id>
            :man-sect:  <man sect-no>
            :snippets:  <snippet [, snippets [, ...]]>
            :language:  <snippet-lang>
            :linenos:
            :debug:

    The argument ``<src-filename>`` is required, it points to a source file in the
    kernel source tree. The pathname is relative to kernel's root folder.  The
    options have the following meaning, but be aware that not all combinations of
    these options make sense:

    ``doc <section title>``
        Include content of the ``DOC:`` section titled ``<section title>``.  Spaces
        are allowed in ``<section title>``; do not quote the ``<section title>``.

        The next option make only sense in conjunction with option ``doc``:

        ``no-header``
            Do not output DOC: section's title. Useful, if the surrounding context
            already has a heading, and the DOC: section title is only used as an
            identifier. Take in mind, that this option will not suppress any native
            reST heading markup in the comment (:ref:`reST-section-structure`).

    ``export [<src-fname-pattern> [, ...]]``
        Include documentation for all function, struct or whatever definition in
        ``<src-filename>``, exported using EXPORT_SYMBOL macro (``EXPORT_SYMBOL``,
        ``EXPORT_SYMBOL_GPL`` & ``EXPORT_SYMBOL_GPL_FUTURE``) either in
        ``<src-filename>`` or in any of the files specified by
        ``<src-fname-pattern>``.

        The ``<src-fname-pattern>`` (glob) is useful when the kernel-doc comments
        have been placed in header files, while EXPORT_SYMBOL are next to the
        function definitions.

    ``internal [<src-fname-pattern> [, ...]]``
        Include documentation for all documented definitions, **not** exported using
        EXPORT_SYMBOL macro either in ``<src-filename>`` or in any of the files
        specified by ``<src-fname-pattern>``.

    ``exp-method <method>``
        Change the way exported symbols are specified in source code.
        Default value ('macro') if not provided can be set globally by
        kernel_doc_exp_method in the sphinx configuration.
	``<method>`` must one of the following value:

        ``macro``
            Exported symbols are specified by macros (whose names are
            controlled by ```exp-ids` option) invoked in the source the
            following way: THIS_IS_AN_EXPORTED_SYMBOL(symbol)

        ``attribute``
            Exported symbols are specified definition using a specific
            attribute (controlled by ```exp-ids` option) either in their
            declaration or definition:
            THIS_IS_AN_EXPORTED_SYMBOL int symbol(void* some_arg) {...}

    ``exp-ids <identifier [, identifiers [, ...]]>``
        Use the specified list of identifiers instead of default value:
        EXPORT_SYMBOL, EXPORT_SYMBOL_GPL, EXPORT_SYMBOL_GPL_FUTURE. Default
        value can be overriden globally by sphinx configuration option:
        kernel_doc_exp_ids

    ``known-attrs <attr [, attrs [, ...]]>``
        Specified a list of function attribute that are known and must be
        hidden when displaying function prototype. When ``exp-method`` is
        set to 'attribute' the list in ``exp-ids`` is considered as known
        and added implicitely to this list of known attributes. The default
        list is empty and can be adjusted by the sphinx configuration option
        kernel_doc_known_attrs

    ``functions <name [, names [, ...]]>``
        Include documentation for each named definition.

    ``module <prefix-id>``
        The option ``:module: <id-prefix>`` sets a module-name. The module-name is
        used as a prefix for automatic generated IDs (reference anchors).

    ``man-sect <sect-no>``

      Section number of the manual pages (see man man-pages). The man-pages are build
      by the ``kernel-doc-man`` builder.

    ``snippets <name [, names [, ...]]>``
        Inserts the source-code passage(s) marked with the snippet ``name``. The
        snippet is inserted with a `code-block:: <http://www.sphinx-doc.org/en/stable/markup/code.html>`_
        directive.

        The next options make only sense in conjunction with option ``snippets``:

        ``language <highlighter>``
            Set highlighting language of the snippet code-block.

        ``linenos``
            Set line numbers in the snippet code-block.

    ``debug``
        Inserts a code-block with the generated reST source. This might sometimes
        helpful to see how the kernel-doc parser transforms the kernel-doc markup to
        reST markup.

    The following example shows how to insert documentation from the source file
    ``/drivers/gpu/drm/drm_drv.c``. In this example the documentation from the
    ``DOC:`` section with the title "driver instance overview" and the
    documentation of all exported symbols (EXPORT_SYMBOL) is included in the
    reST tree.

    .. code-block:: rst

        .. kernel-doc::  drivers/gpu/drm/drm_drv.c
            :export:
            :doc:        driver instance overview

    An other example is to use only one function description.

    .. code-block:: rst

        .. kernel-doc::  include/media/i2c/tvp7002.h
            :functions:  tvp7002_config
            :module:     tvp7002

    This will produce the following reST markup to include:

    .. code-block:: rst

        .. _`tvp514x.tvp514x_platform_data`:

        struct tvp514x_platform_data
        ============================

        .. c:type:: tvp514x_platform_data


        .. _`tvp514x.tvp514x_platform_data.definition`:

        Definition
        ----------

        .. code-block:: c

            struct tvp514x_platform_data {
                bool clk_polarity;
                bool hs_polarity;
                bool vs_polarity;
            }

        .. _`tvp514x.tvp514x_platform_data.members`:

        Members
        -------

        clk_polarity
            Clock polarity of the current interface.

        hs_polarity
            HSYNC Polarity configuration for current interface.

        vs_polarity
            VSYNC Polarity configuration for current interface.

    The last example illustrates, that the option ``:module: tvp514x`` is used
    as a prefix for anchors. E.g. ```ref:`tvp514x.tvp514x_platform_data.members¸```
    refers to the to the member description of ``struct tvp514x_platform_data``.
"""

# ==============================================================================
# imports
# ==============================================================================

import glob
from os import path
from io import StringIO

import six

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.utils import SystemMessage
from docutils.statemachine import ViewList

from sphinx.ext.autodoc import AutodocReporter

from . import kernel_doc as kerneldoc

# ==============================================================================
# common globals
# ==============================================================================

# The version numbering follows numbering of the specification
# (Documentation/books/kernel-doc-HOWTO).
__version__  = '1.0'

PARSER_CACHE = dict()

# ==============================================================================
def setup(app):
# ==============================================================================

    app.add_config_value('kernel_doc_raise_error', False, 'env')
    app.add_config_value('kernel_doc_verbose_warn', True, 'env')
    app.add_config_value('kernel_doc_mode', "reST", 'env')
    app.add_config_value('kernel_doc_mansect', None, 'env')
    app.add_config_value('kernel_doc_exp_method', None, 'env')
    app.add_config_value('kernel_doc_exp_ids', None, 'env')
    app.add_config_value('kernel_doc_known_attrs', None, 'env')
    app.add_directive("kernel-doc", KernelDoc)

    return dict(
        version = __version__
        , parallel_read_safe = True
        , parallel_write_safe = True
    )

# ==============================================================================
class KernelDocParser(kerneldoc.Parser):
# ==============================================================================

    def __init__(self, app, *args, **kwargs):
        super(KernelDocParser, self).__init__(*args, **kwargs)
        self.app = app

    # -------------------------------------------------
    # bind the parser logging to the sphinx application
    # -------------------------------------------------

    def error(self, message, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        self.errors += 1
        message = ("%(fname)s:%(line_no)s: [kernel-doc ERROR] : " + message) % replace
        self.app.warn(message)

    def warn(self, message, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        self.warnings += 1
        message = ("%(fname)s:%(line_no)s: [kernel-doc WARN] : " + message) % replace
        self.app.warn(message)

    def info(self, message, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        message = ("%(fname)s:%(line_no)s: [kernel-doc INFO] : " + message) % replace
        self.app.verbose(message)

    def debug(self, message, **replace):
        if self.app.verbosity < 2:
            return
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        message = ("%(fname)s:%(line_no)s: [kernel-doc DEBUG] : " + message) % replace
        self.app.debug(message)


# ==============================================================================
class FaultyOption(Exception):
    pass

class KernelDoc(Directive):
# ==============================================================================

    u"""KernelDoc (``kernel-doc``) directive"""

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True

    option_spec = {
        "doc"          : directives.unchanged_required # aka lines containing !P
        , "no-header"  : directives.flag

        , "export"     : directives.unchanged          # aka lines containing !E
        , "internal"   : directives.unchanged          # aka lines containing !I
        , "functions"  : directives.unchanged_required # aka lines containing !F
        , "exp-method" : directives.unchanged_required
        , "exp-ids"    : directives.unchanged_required
        , "known-attrs": directives.unchanged_required

        , "debug"      : directives.flag               # insert generated reST as code-block

        , "snippets"   : directives.unchanged_required
        , "language"   : directives.unchanged_required
        , "linenos"    : directives.flag

        # module name / used as id-prefix
        , "module"     : directives.unchanged_required
        , "man-sect"   : directives.nonnegative_int

        # The encoding of the source file with the kernel-doc comments. The
        # default is the config.source_encoding from sphinx configuration and
        # this default is utf-8-sig
        , "encoding"   : directives.encoding

    }

    def getParserOptions(self):

        fname     = self.arguments[0]
        src_tree  = kerneldoc.SRCTREE
        exp_files = []  # file pattern to search for EXPORT_SYMBOL
        exp_method  = self.options.get("exp-method", self.env.config.kernel_doc_exp_method)
        exp_ids     = self.options.get("exp-ids", self.env.config.kernel_doc_exp_ids)
        known_attrs = self.options.get("known-attrs", self.env.config.kernel_doc_known_attrs)

        if self.arguments[0].startswith("./"):
            # the prefix "./" indicates a relative pathname
            fname = self.arguments[0][2:]
            src_tree = path.dirname(path.normpath(self.doc.current_source))

        if "internal" in self.options and "export" in self.options:
            raise FaultyOption(
                "Options 'export' and 'internal' are orthogonal,"
                " can't use them togehter")

        if "snippets" in self.options:
            rest = set(self.options.keys()) - set(["snippets", "linenos", "language", "debug"])
            if rest:
                raise FaultyOption(
                    "kernel-doc 'snippets' has non of these options: %s"
                    % ",".join(rest))

        if self.env.config.kernel_doc_mode not in ["reST", "kernel-doc"]:
            raise FaultyOption(
                "unknow kernel-doc mode: %s" % self.env.config.kernel_doc_mode)

        # set parse adjustments

        ctx  = kerneldoc.ParserContext()
        opts = kerneldoc.ParseOptions(
            rel_fname       = fname
            , src_tree      = src_tree
            , id_prefix     = self.options.get("module", "").strip()
            , encoding      = self.options.get("encoding", self.env.config.source_encoding)
            , verbose_warn  = self.env.config.kernel_doc_verbose_warn
            , markup        = self.env.config.kernel_doc_mode
            , man_sect      = self.options.get("man-sect", None)
            , exp_method    = exp_method
            , exp_ids       = (exp_ids or "").replace(","," ").split()
            , known_attrs   = (known_attrs or "").replace(","," ").split()
            ,)

        if ("doc" not in self.options
            and opts.man_sect is None):
            opts.man_sect = self.env.config.kernel_doc_mansect

        opts.set_defaults()

        if not path.exists(opts.fname):
            raise FaultyOption(
                "kernel-doc refers to nonexisting document %s" % opts.fname)

        # always skip preamble and epilog in kernel-doc directives
        opts.skip_preamble = True
        opts.skip_epilog   = True

        if ("doc" not in self.options
            and "export" not in self.options
            and "internal" not in self.options
            and "functions" not in self.options
            and "snippets" not in self.options):
            # if no explicit content is selected, then print all, including all
            # DOC sections
            opts.use_all_docs = True

        if "doc" in self.options:
            opts.no_header = bool("no-header" in self.options)
            opts.use_names.append(self.options.get("doc"))

        if "export" in self.options:
            # gather exported symbols and add them to the list of names
            kerneldoc.Parser.gather_context(kerneldoc.readFile(opts.fname), ctx, opts)
            exp_files.extend((self.options.get('export') or "").replace(","," ").split())
            opts.error_missing = True

        elif "internal" in self.options:
            # gather exported symbols and add them to the ignore-list of names
            kerneldoc.Parser.gather_context(kerneldoc.readFile(opts.fname), ctx, opts)
            exp_files.extend((self.options.get('internal') or "").replace(","," ").split())

        if "functions" in self.options:
            opts.error_missing = True
            opts.use_names.extend(
                self.options["functions"].replace(","," ").split())

        for pattern in exp_files:
            if pattern.startswith("./"): # "./" indicates a relative pathname
                pattern = path.join(
                    path.dirname(path.normpath(self.doc.current_source))
                    , pattern[2:])
            else:
                pattern = path.join(kerneldoc.SRCTREE, pattern)

            if (not glob.has_magic(pattern)
                and not path.lexists(pattern)):
                # if pattern is a filename (is not a glob pattern) and this file
                # does not exists, an error is raised.
                raise FaultyOption("file not found: %s" % pattern)

            for fname in glob.glob(pattern):
                self.env.note_dependency(path.abspath(fname))
                kerneldoc.Parser.gather_context(kerneldoc.readFile(fname), ctx, opts)

        if "export" in self.options:
            if not ctx.exported_symbols:
                raise FaultyOption("using option :export: but there are no exported symbols")
            opts.use_names.extend(ctx.exported_symbols)

        if "internal" in self.options:
            opts.skip_names.extend(ctx.exported_symbols)

        return opts

    def errMsg(self, msg):
        msg = six.text_type(msg)
        error = self.state_machine.reporter.error(
            msg
            , nodes.literal_block(self.block_text, self.block_text)
            , line = self.lineno )

        # raise exception on error?
        if self.env.config.kernel_doc_raise_error:
            raise SystemMessage(error, 4)

        # insert oops/todo admonition, this is the replacement of the escape
        # sequences "!C<filename> " formerly used in the DocBook-SGML template
        # files.
        todo = ("\n\n.. todo::"
                "\n\n    Oops: Document generation inconsistency."
                "\n\n    The template for this document tried to insert"
                " structured comment at this point, but an error occoured."
                " This dummy section is inserted to allow generation to continue.::"
                "\n\n")

        for l in error.astext().split("\n"):
            todo +=  "        " + l + "\n"
        todo += "\n\n"
        self.state_machine.insert_input(todo.split("\n"), self.arguments[0] )

    def parseSource(self, opts):
        parser = PARSER_CACHE.get(opts.fname, None)

        if parser is None:
            self.env.note_dependency(opts.fname)
            #self.env.app.info("parse kernel-doc comments from: %s" % opts.fname)
            parser = KernelDocParser(self.env.app, opts, kerneldoc.NullTranslator())
            parser.parse()
            PARSER_CACHE[opts.fname] = parser
        else:
            parser.setOptions(opts)

        return parser

    def run(self):

        # pylint: disable=W0201
        self.parser = None
        self.doc    = self.state.document
        self.env    = self.doc.settings.env
        self.nodes  = []

        try:
            if not self.doc.settings.file_insertion_enabled:
                raise FaultyOption('docutils: file insertion disabled')
            opts = self.getParserOptions()
            self.parser = self.parseSource(opts)
            self.nodes.extend(self.getNodes())

        except FaultyOption as exc:
            self.errMsg(exc)

        return self.nodes


    def getNodes(self):

        translator = kerneldoc.ReSTTranslator()
        lines      = ""
        content    = WriterList(self.parser)
        node       = nodes.section()

        # translate

        if "debug" in self.options:
            rstout = StringIO()
            self.parser.options.out = rstout
            self.parser.parse_dump_storage(translator=translator)
            code_block = "\n\n.. code-block:: rst\n    :linenos:\n"
            for l in rstout.getvalue().split("\n"):
                code_block += "\n    " + l
            lines = code_block + "\n\n"

        elif "snippets" in self.options:
            selected  = self.options["snippets"].replace(","," ").split()
            names     = self.parser.ctx.snippets.keys()
            not_found = [ s for s in selected if s not in names]
            found     = [ s for s in selected if s in names]
            if not_found:
                self.errMsg("selected snippets(s) not found:\n    %s"
                            % "\n    ,".join(not_found))

            if found:
                code_block = "\n\n.. code-block:: %s\n" % self.options.get("language", "c")
                if "linenos" in self.options:
                    code_block += "    :linenos:\n"
                snipsnap = ""
                while found :
                    snipsnap += self.parser.ctx.snippets[found.pop(0)] + "\n\n"
                for l in snipsnap.split("\n"):
                    code_block += "\n    " + l
                lines = code_block + "\n\n"

        else:
            self.parser.options.out = content
            self.parser.parse_dump_storage(translator=translator)

        # check translation

        if "functions" in self.options:
            selected  = self.options["functions"].replace(","," ").split()
            names     = translator.translated_names
            not_found = [ s for s in selected if s not in names]
            if not_found:
                self.errMsg(
                    "selected section(s) not found:\n    %s"
                    % "\n    ,".join(not_found))

        if "export" in self.options:
            selected  = self.parser.options.use_names
            names     = translator.translated_names
            not_found = [ s for s in selected if s not in names]
            if not_found:
                self.errMsg(
                    "exported definitions not found:\n    %s"
                    % "\n    ,".join(not_found))

        # add lines to content list
        reSTfname = self.state.document.current_source

        content.flush()
        if lines:
            for l in lines.split("\n"):
                content.append(l, reSTfname, self.lineno)

        buf = self.state.memo.title_styles, self.state.memo.section_level, self.state.memo.reporter
        self.state.memo.reporter = AutodocReporter(content, self.state.memo.reporter)
        self.state.memo.title_styles, self.state.memo.section_level = [], 0
        try:
            self.state.nested_parse(content, 0, node, match_titles=1)
        finally:
            self.state.memo.title_styles, self.state.memo.section_level, self.state.memo.reporter = buf

        return node.children


# ==============================================================================
class WriterList(ViewList):
# ==============================================================================
    u"""docutils ViewList with write method."""

    def __init__(self, parser, *args, **kwargs):
        ViewList.__init__(self, *args, **kwargs)
        self.parser = parser

        self.last_offset = -1
        self.line_buffer = ""

    def write(self, cont):
        if self.last_offset != self.parser.ctx.offset:
            self.flush()
            self.line_buffer = ""
            self.last_offset = self.parser.ctx.offset

        self.line_buffer += cont

    def flush(self):
        for _i, l in enumerate(self.line_buffer.split("\n")):
            self.append(l, self.parser.options.fname, self.last_offset)
        self.line_buffer = ""
