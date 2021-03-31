# -*- coding: utf-8; mode: python -*-
# pylint: disable=missing-docstring, invalid-name
# SPDX-License-Identifier: GPL-2.0
"""\
rstKernelDoc
~~~~~~~~~~~~

Implementation of the ``kernel-doc`` reST-directive.

The ``kernel-doc`` (:py:class:`KernelDoc`) directive includes contend from
linux kernel source code comments.

"""

# ==============================================================================
# imports
# ==============================================================================

import glob
import logging
from os import path
from io import StringIO

import six

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.utils import SystemMessage
from docutils.statemachine import ViewList
from sphinx.util.docutils import switch_source_input

from fspath import OS_ENV
from . import kernel_doc as kerneldoc

# ==============================================================================
# common globals
# ==============================================================================

__version__  = '3.0'

PARSER_CACHE = dict()

app_log = logging.getLogger('application')

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
    app.add_config_value('kernel_doc_srctree', kerneldoc.SRCTREE, 'env')
    app.add_directive("kernel-doc", KernelDoc)

    return dict(
        version = __version__
        , parallel_read_safe = True
        , parallel_write_safe = True
    )

# ==============================================================================
class KernelDocParser(kerneldoc.Parser):
# ==============================================================================

    # pylint: disable=deprecated-method

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    # -------------------------------------------------
    # bind the parser logging to the sphinx application
    # -------------------------------------------------

    # pylint: disable=arguments-differ

    def error(self, message, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        self.errors += 1
        message = ("%(fname)s:%(line_no)s: [kernel-doc ERROR] : " + message) % replace
        app_log.warn(message)

    def warn(self, message, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        self.warnings += 1
        message = ("%(fname)s:%(line_no)s: [kernel-doc WARN] : " + message) % replace
        app_log.warn(message)

    def info(self, message, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        message = ("%(fname)s:%(line_no)s: [kernel-doc INFO] : " + message) % replace
        app_log.info(message)

    def debug(self, message, **replace):
        if self.app.verbosity < 2:
            return
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        message = ("%(fname)s:%(line_no)s: [kernel-doc DEBUG] : " + message) % replace
        app_log.debug(message)


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

        # see https://github.com/PyCQA/pylint/issues/289

        "doc"          : directives.unchanged_required # aka lines containing !P
        , "no-header"  : directives.flag

        , "export"     : directives.unchanged          # aka lines containing !E
        , "internal"   : directives.unchanged          # aka lines containing !I
        , "functions"  : directives.unchanged_required # aka lines containing !F
        , "symbols"    : directives.unchanged_required
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

    def getParserOptions(self):  # pylint: disable=too-many-branches, too-many-statements

        fname     = self.arguments[0]
        src_tree  = path.dirname(path.normpath(self.doc.current_source))
        exp_files = []  # file pattern to search for EXPORT_SYMBOL
        exp_method  = self.options.get("exp-method", self.env.config.kernel_doc_exp_method)
        exp_ids     = self.options.get("exp-ids", self.env.config.kernel_doc_exp_ids)
        known_attrs = self.options.get("known-attrs", self.env.config.kernel_doc_known_attrs)

        if self.arguments[0].startswith("/"):
            # Absolute path names are relative to srctree, which is taken from
            # environment, configuration or current directory (in this order).
            fname = self.arguments[0][1:]
            src_tree = OS_ENV.get("srctree", self.env.config.kernel_doc_srctree)

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
            fname           = fname
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

        if ( "doc" not in self.options
             and opts.man_sect is None):
            opts.man_sect = self.env.config.kernel_doc_mansect

        opts.set_defaults()

        if not path.exists(opts.fname):
            raise FaultyOption(
                "kernel-doc refers to nonexisting document %s" % opts.fname)

        # always skip preamble and epilog in kernel-doc directives
        opts.skip_preamble = True
        opts.skip_epilog   = True

        if ( "doc" not in self.options
             and "export" not in self.options
             and "internal" not in self.options
             and "functions" not in self.options
             and "snippets" not in self.options ):
            # if no explicit content is selected, then print all, including all
            # DOC sections
            opts.use_all_docs = True

        if "doc" in self.options:
            opts.no_header = bool("no-header" in self.options)
            opts.use_names.append(self.options.get("doc"))

        if "export" in self.options and self.options.get('export'):
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

            if pattern[0] == '/':
                pattern = pattern[1:]
            pattern = path.join(opts.src_tree, pattern)

            if ( not glob.has_magic(pattern)
                 and not path.lexists(pattern) ):
                # if pattern is a filename (is not a glob pattern) and this file
                # does not exists, an error is raised.
                raise FaultyOption("file (pattern) not found: %s" % pattern)

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
            #app_log.info("parse kernel-doc comments from: %s" % opts.fname)
            parser = KernelDocParser(self.env.app, opts, kerneldoc.NullTranslator())
            parser.parse()
            PARSER_CACHE[opts.fname] = parser
        else:
            parser.setOptions(opts)

        return parser

    def run(self):

        # FIXME: think about again; these members has been added for convenience
        self.parser = None                     # pylint: disable=attribute-defined-outside-init
        self.doc    = self.state.document      # pylint: disable=attribute-defined-outside-init
        self.env    = self.doc.settings.env    # pylint: disable=attribute-defined-outside-init
        self.nodes  = []                       # pylint: disable=attribute-defined-outside-init

        if "symbols" in self.options and "functions" in self.options:
            error = self.state_machine.reporter.error(
                ('Error in "%s" directive: used option :symbols:'
                 ' and its alias :functions:'  % self.name),
                nodes.literal_block(self.block_text, self.block_text),
                line = self.lineno
            )
            raise SystemMessage(error, 4)

        if "symbols" in self.options:
            self.options['functions'] = self.options['symbols']

        try:
            if not self.doc.settings.file_insertion_enabled:
                raise FaultyOption('docutils: file insertion disabled')
            opts = self.getParserOptions()
            # FIXME: think about again; these members has been added for convenience
            self.parser = self.parseSource(opts) # pylint: disable=attribute-defined-outside-init
            self.nodes.extend(self.getNodes())

        except FaultyOption as exc:
            self.errMsg(exc)

        return self.nodes


    def getNodes(self):  # pylint: disable=too-many-branches, too-many-statements, too-many-locals

        translator = kerneldoc.ReSTTranslator()
        lines      = ""
        content    = WriterList(self.parser)

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

        node = nodes.section()
        # necessary so that the child nodes get the right source/line set
        node.document = self.state.document
        with switch_source_input(self.state, content):
            # hack around title style bookkeeping
            buf = self.state.memo.title_styles, self.state.memo.section_level
            self.state.memo.title_styles, self.state.memo.section_level = [], 0
            try:
                self.state.nested_parse(content, 0, node, match_titles=1)
            finally:
                self.state.memo.title_styles, self.state.memo.section_level = buf
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
