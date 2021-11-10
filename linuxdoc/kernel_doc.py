#!/usr/bin/env python3
# -*- coding: utf-8; mode: python -*-
# SPDX-License-Identifier: GPL-2.0
#
# pylint: disable=missing-docstring, arguments-differ, invalid-name
# pylint: disable=too-many-arguments, too-many-locals, too-many-branches
# pylint: disable=too-many-nested-blocks, too-many-lines
# pylint: disable=too-many-statements, useless-object-inheritance

"""
    kernel_doc
    ~~~~~~~~~~

    Implementation of the ``kernel-doc`` parser.

    The kernel-doc parser extracts documentation from Linux kernel's source code
    comments. This implements the :ref:`kernel-doc markup <kernel-doc-intro>`.

    This module provides an API -- which could be used by a sphinx-doc generator
    extension -- and a command-line interface, see ``--help``::

        $ kernel-doc --help

    But, the command-line is only for test, normally you don't need it.

    Compared with the Perl kernel-doc script, this implementation has additional
    features like *parse options* for a smooth integration of reStructuredText
    (reST) markup in the kernel's source code comments.  In combination with the
    (separate) *kernel-doc* reST directive (which uses this module), the
    documentation generation becomes more clear and flexible.

    The architecture of the parser is simple and consists of three types of
    objects (three classes).

    * class Parser: The parser parses the source-file and dumps extracted
      kernel-doc data.

    * subclasses of class TranslatorAPI: to translate the dumped kernel-doc data
      into output formats. There exists two implementations:

      - class NullTranslator: translates nothing, just parse

      - class ReSTTranslator(TranslatorAPI): translates dumped kernel-doc data
        to reST markup.

    * class ParseOptions: a container full with options to control parsing an
      translation.

    With the NullTranslator a source file is parsed only once while different
    output could be generated (multiple times) just by changing the Translator
    (e.g. with the ReSTTranslator) and the option container.

    With parsing the source files only once, the building time is reduced n-times.

"""

# ==============================================================================
# imports
# ==============================================================================

import argparse
import codecs
import collections
import copy
import os
import re
import sys
import textwrap

import six

from fspath import OS_ENV
from . import compat

# ==============================================================================
# common globals
# ==============================================================================

# The version numbering follows numbering of the specification
# (Documentation/books/kernel-doc-HOWTO).
__version__  = '1.0'

# ==============================================================================
# regular expresssions and helper used by the parser and the translator
# ==============================================================================

class RE(object):
    u"""regular expression that stores last match (like Perl's ``=~`` operator)"""

    def __init__(self, *args, **kwargs):
        self.re = re.compile(*args, **kwargs)
        self.last_match = None

    def match(self, *args, **kwargs):
        self.last_match = self.re.match(*args, **kwargs)
        return self.last_match

    def search(self, *args, **kwargs):
        self.last_match = self.re.search(*args, **kwargs)
        return self.last_match

    def __getattr__(self, attr):
        return getattr(self.re, attr)

    def __getitem__(self, group):
        if group < 0 or group > self.groups - 1:
            raise IndexError("group index out of range (max %s groups)" % self.groups )
        if self.last_match is None:
            raise IndexError("nothing has matched / no groups")
        return self.last_match.group(group + 1)

# these regular expresions has been *stolen* from the kernel-doc perl script.

doc_start        = RE(r"^/\*\*\s*$")  # Allow whitespace at end of comment start.
doc_end          = RE(r"\s*\*+/")
doc_com          = RE(r"\s*\*\s*")
doc_com_section  = RE(r"\s*\*\s{1,8}") # more than 8 spaces (one tab) as prefix is not a new section comment
doc_com_body     = RE(r"\s*\* ?")
doc_decl         = RE(doc_com.pattern + r"(\w+)")
#doc_decl_ident   = RE(r"\s*([\w\s]+?)\s*[\(\)]\s*[-:]")
doc_decl_ident   = RE(doc_com.pattern + r"(struct|union|enum|typedef|function)\b\s*(\w+)(\(\))?")
doc_decl_purpose = RE(r"[-:](.*)$")

# except pattern like "http://", a whitespace is required after the colon
doc_sect_except  = RE(doc_com.pattern + r"[^\s@](.*)?:[^\s]")

#doc_sect = RE(doc_com.pattern + r"([" + doc_special.pattern + r"]?[\w\s]+):(.*)")
# "section header:" names must be unique per function (or struct,union, typedef,
# enum). Additional condition: the header name should have 3 characters at least!
doc_sect  = RE(
    doc_com_section.pattern
    + r"("
    + r"@\w[^:]*"                                 # "@foo: lorem" or
    + r"|" + r"@\w[.\w]+[^:]*"                    # "@foo.bar: lorem" or
    + r"|" + r"\@\.\.\."                          # ellipsis "@...: lorem" or
    + r"|" + r"\w[\w\s]+\w"                       # e.g. "Return: lorem"
    + r")"
    + r":(.*?)\s*$")   # this matches also strings like "http://..." (doc_sect_except)

doc_sect_reST = RE(
    doc_com_section.pattern
    + r"("
    + r"@\w[^:]*"                                 # "@foo: lorem" or
    + r"|" + r"@\w[.\w]+[^:]*"                    # "@foo.bar: lorem" or
    + r"|" + r"\@\.\.\."                          # ellipsis "@...: lorem" or
    # a tribute to vintage markups, when in reST mode ...
    + r"|description|context|returns?|notes?|examples?|introduction|intro"
    + r")"
    + r":(.*?)\s*$"    # this matches also strings like "http://..." (doc_sect_except)
    , flags = re.IGNORECASE)

reST_sect = RE(
    doc_com_section.pattern
    + r"("
    r"\w[\w\s]+\w"
    + r")"
    + r":\s*$")

doc_content      = RE(doc_com_body.pattern + r"(.*)")
doc_block        = RE(doc_com.pattern + r"DOC:\s*(.*)?")

# state: 5 - gathering documentation outside main block
doc_state5_start = RE(r"^\s*/\*\*\s*$")
doc_state5_sect  = RE(r"\s*\*\s*(@\s*[\w][\w\.]*\s*):(.*)")

doc_state5_end   = RE(r"^\s*\*/\s*$")
doc_state5_oneline = RE(r"^\s*/\*\*\s*(@[\w\s]+):\s*(.*)\s*\*/\s*$")

# match expressions used to find embedded type information
type_enum_full    = RE(r"(?<=\s)\&(enum)\s*([_\w]+)")
type_struct_full  = RE(r"(?<=\s)\&(struct)\s*([_\w]+)")
type_typedef_full = RE(r"(?<=\s)\&(typedef)\s*([_\w]+)")
type_union_full   = RE(r"(?<=\s)\&(union)\s*([_\w]+)")
type_member       = RE(r"(?<=\s)\&([_\w]+)((\.|->)[_\w]+)")
type_member_func  = RE(type_member.pattern + r"\(\)")
type_func         = RE(r"(?<=\s)(\w+)(?<!\\)\(\)")
type_constant     = RE(r"(?<=\s)\%([-_\w]+)")
type_param        = RE(r"(?<=\s)\@(\w*((\.\w+)|(->\w+))*(\.\.\.)?)")
type_env          = RE(r"(?<=\s)(\$\w+)")
type_struct       = RE(r"(?<=\s)\&((struct\s*)*[_\w]+)")

esc_type_prefix  = RE(r"\\([\@\%\&\$\(])")

CR_NL            = RE(r"[\r\n]")
C99_comments     = RE(r"//.*$")
C89_comments     = RE(r"/\*.*?\*/")

C_STRUCT         = RE(r"struct\s+(\w+)\s*{(.*)}")
C_UNION          = RE(r"union\s+(\w+)\s*{(.*)}")
C_STRUCT_UNION   = RE(r"(struct|union)\s+(\w+)\s*{(.*)}")
C_ENUM           = RE(r"enum\s+(\w+)\s*{(.*)}")
C_TYPEDEF        = RE(r"typedef.*\s+(\w+)\s*;")

# typedef of a function pointer
_typedef_type    = r"((?:\s+[\w\*]+\b){1,8})\s*"
_typedef_ident   = r"\*?\s*(\w\S+)\s*"
_typedef_args    = r"\s*\((.*)\);"
C_FUNC_TYPEDEF   = RE(r"typedef" + _typedef_type + r"\(" + _typedef_ident + r"\)" + _typedef_args)
C_FUNC_TYPEDEF_2 = RE(r"typedef" + _typedef_type + _typedef_ident + _typedef_args)

MACRO            = RE(r"^#")
MACRO_define     = RE(r"^#\s*define\s+")

SYSCALL_DEFINE   = RE(r"^\s*SYSCALL_DEFINE.*\(")
SYSCALL_DEFINE0  = RE(r"^\s*SYSCALL_DEFINE0")

TP_PROTO                 = RE(r"TP_PROTO\((.*?)\)")
TRACE_EVENT              = RE(r"TRACE_EVENT")
TRACE_EVENT_name         = RE(r"TRACE_EVENT\((.*?),")
DEFINE_EVENT             = RE(r"DEFINE_EVENT")
DEFINE_EVENT_name        = RE(r"DEFINE_EVENT\((.*?),(.*?),")
DEFINE_SINGLE_EVENT      = RE(r"DEFINE_SINGLE_EVENT")
DEFINE_SINGLE_EVENT_name = RE(r"DEFINE_SINGLE_EVENT\((.*?),")

FUNC_PROTOTYPES = [
    # RE(r"^(\w+)\s+\(\*([a-zA-Z0-9_]+)\)\s*\(([^\(]*)\)") # match: void (*foo) (int bar);
    RE(r"^()([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^(\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^(\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^(\w+\s+\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^(\w+\s+\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^(\w+\s+\w+\s+\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^(\w+\s+\w+\s+\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\(]*)\)")
    , RE(r"^()([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+\s+\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+\s+\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+\s+\w+\s+\w+)\s+([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+\s+\w+\s+\w+\s*\*+)\s*([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
    , RE(r"^(\w+\s+\w+\s*\*\s*\w+\s*\*+\s*)\s*([a-zA-Z0-9_~:]+)\s*\(([^\{]*)\)")
]

# MODULE_AUTHOR("..."); /  MODULE_DESCRIPTION("..."); / MODULE_LICENSE("...");
#
MODULE_INFO = RE(r'^\s*(MODULE_)(AUTHOR|DESCRIPTION|LICENSE)\s*\(\s*"([^"]+)"', flags=re.M)

WHITESPACE = RE(r"\s+", flags=re.UNICODE)

def normalize_ws(string):
    u"""strip needles whitespaces.

    Substitute consecutive whitespaces with one single space and strip
    trailing/leading whitespaces"""

    string = WHITESPACE.sub(" ", string)
    return string.strip()

ID_CHARS = RE(r"[^A-Za-z0-9\._]")

def normalize_id(ID):
    u"""substitude invalid chars of the ID with ``-`` and mak it lowercase"""
    return ID_CHARS.sub("-", ID).lower()


RST_DIRECTIVE_PATTERN = r"""
  \.\.[ ]+          # explicit markup start
  (%s)              # directive name
  [ ]?              # optional space
  ::                # directive delimiter
  ([ ]+|$)          # whitespace or end of line
  """

RST_CODE_BLOCK = RE(RST_DIRECTIVE_PATTERN % 'code-block', re.VERBOSE | re.UNICODE)
RST_LITERAL_BLOCK = RE(r'(?<!\\)(\\\\)*::$')
RST_INDENT = RE(r"^(\s*)[^\s]")

def map_row(row, map_table):
    for regexpr, substitute in map_table:
        if substitute is not None:
            # python has only fixed width lookbehind: add temporarily leading space
            row = regexpr.sub(substitute, " " + row)[1:]
    return row

def highlight_parser(text, map_table):
    # FIXME: document this
    block_indent = 0
    row_indent = 0
    state = 'highlight' # [highlight|literal]
    out = []
    in_rows = text.splitlines()

    while in_rows:
        row = in_rows.pop(0)

        if not row.strip(): # pass-through empty lines & continue
            out.append(row)
            continue

        RST_INDENT.search(row)
        indent = len(RST_INDENT[0].expandtabs())

        if state == 'highlight':
            out.append(map_row(row, map_table))
            # prepare next state
            if (RST_LITERAL_BLOCK.search(row) or RST_CODE_BLOCK.search(row)):
                state = 'literal'
                block_indent = row_indent + 1
            continue

        if state == 'literal':
            if indent < block_indent:
                # this is a new block, push row back onto the stack and repeat
                # the loop
                state = 'highlight'
                block_indent = indent
                in_rows.insert(0, row)
                continue

            out.append(row)

    return "\n".join(out)


# ==============================================================================
# helper
# ==============================================================================

def openTextFile(fname, mode="r", encoding="utf-8", errors="strict"):
    return codecs.open(fname, mode=mode, encoding=encoding, errors=errors)

def readFile(fname, encoding="utf-8", errors="strict"):
    with openTextFile(fname, encoding=encoding, errors=errors) as f:
        return f.read()

class Container(dict):
    @property
    def __dict__(self):
        return self
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, val):
        self[attr] = val

class DevNull(object): # pylint: disable=too-few-public-methods
    """A dev/null file descriptor."""
    def write(self, *args, **kwargs):
        pass
DevNull = DevNull()

SRCTREE        = OS_ENV.get("srctree", os.getcwd())
GIT_REF        = ("Linux kernel source tree:"
                  " `%(rel_fname)s <https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/"
                  "%(rel_fname)s>`__")
DEFAULT_EXP_METHOD = "macro"
DEFAULT_EXP_IDS    = ['EXPORT_SYMBOL', 'EXPORT_SYMBOL_GPL', 'EXPORT_SYMBOL_GPL_FUTURE']

# ==============================================================================
# Logging stuff
# ==============================================================================

STREAM = Container(
    # pipes used by the application & logger
    appl_out   = sys.__stdout__
    , log_out  = sys.__stderr__
    , )

VERBOSE = False
DEBUG   = False
INSPECT = False

class SimpleLog(object):

    LOG_FORMAT = "%(logclass)s: %(message)s\n"

    def error(self, message, **replace):
        message = message % replace
        replace.update(dict(message = message, logclass = "ERROR"))
        STREAM.log_out.write(self.LOG_FORMAT % replace)

    def warn(self, message, **replace):
        message = message % replace
        replace.update(dict(message = message, logclass = "WARN"))
        STREAM.log_out.write(self.LOG_FORMAT % replace)

    def info(self, message, **replace):
        if not VERBOSE:
            return
        message = message % replace
        replace.update(dict(message = message, logclass = "INFO"))
        STREAM.log_out.write(self.LOG_FORMAT % replace)

    def debug(self, message, **replace):
        if not DEBUG:
            return
        message = message % replace
        replace.update(dict(message = message, logclass = "DEBUG"))
        STREAM.log_out.write(self.LOG_FORMAT % replace)

LOG = SimpleLog()

# ==============================================================================
def main():
    # pylint: disable=global-statement
# ==============================================================================

    global VERBOSE, DEBUG

    epilog = (u"This implementation uses the kernel-doc parser"
              " from the linuxdoc extension, for detail informations read"
              " https://return42.github.io/linuxdoc/cmd-line.html#kernel-doc")

    CLI = argparse.ArgumentParser(
        description = (
            "Parse *kernel-doc* comments from source code"
            " and print them (with reST markup) to stdout." )
        , epilog = epilog
        , formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    CLI.add_argument(
        "files"
        , nargs   = "+"
        , help    = "source file(s) to parse.")

    CLI.add_argument(
        "--id-prefix"
        , default = ""
        , help    = (
            "A prefix for automatic generated IDs. The IDs are automaticly"
            " gernerated based on the declaration and / or section names. The"
            " prefix is also used as namespace in Sphinx's C-domain"))

    CLI.add_argument(
        "--verbose", "-v"
        , action  = "store_true"
        , help    = "verbose output with log messages to stderr" )

    CLI.add_argument(
        "--sloppy"
        , action  = "store_true"
        , help    = "Sloppy linting, reports only severe errors.")

    CLI.add_argument(
        "--debug"
        , action  = "store_true"
        , help    = "debug messages to stderr" )

    CLI.add_argument(
        "--quiet", "-q"
        , action  = "store_true"
        , help    = "no messages to stderr" )

    CLI.add_argument(
        "--skip-preamble"
        , action  = "store_true"
        , help    = "skip preamble in the output" )

    CLI.add_argument(
        "--skip-epilog"
        , action  = "store_true"
        , help    = "skip epilog in the output" )

    CLI.add_argument(
        "--list-internals"
        , choices = Parser.DOC_TYPES + ["all"]
        , nargs   = "+"
        , help    = "list symbols, titles or whatever is documented, but *not* exported" )

    CLI.add_argument(
        "--list-exports"
        , action  = "store_true"
        , help    = "list all exported symbols" )

    CLI.add_argument(
        "--use-names"
        , nargs   = "+"
        , help    = "print documentation of functions, structs or whatever title/object")

    CLI.add_argument(
        "--exported"
        , action  = "store_true"
        , help    = "print documentation of all exported symbols")

    CLI.add_argument(
        "--internal"
        , action  = "store_true"
        , help    = ("print documentation of all symbols that are documented,"
                     " but not exported" ))

    CLI.add_argument(
        "--markup"
        , choices = ["reST", "kernel-doc"]
        , default = "reST"
        , help    = (
            "Markup of the comments. Change this option only if you know"
            " what you do. New comments must be marked up with reST!"))

    CLI.add_argument(
        "--symbols-exported-method"
        , default = DEFAULT_EXP_METHOD
        , help    = (
            "Indicate the way by which an exported symbol an exported symbol"
            " is exported. Must be either 'macro' or 'attribute'."))

    CLI.add_argument(
        "--symbols-exported-identifiers"
        , nargs   = "+"
        , default = DEFAULT_EXP_IDS
        , help    = "identifiers list that specifies an exported symbol")

    CLI.add_argument(
        "--known-attrs"
        , default = ""
        , nargs   = "+"
        , help    = ("provides a list of known attributes that has to be"
                     " hidden when displaying function prototypes"))

    CMD     = CLI.parse_args()
    VERBOSE = CMD.verbose
    DEBUG   = CMD.debug

    if CMD.quiet:
        STREAM.log_out = DevNull  # pylint: disable=attribute-defined-outside-init

    LOG.debug(u"CMD: %(CMD)s", CMD=CMD)

    retVal     = 0

    for fname in CMD.files:
        translator = ReSTTranslator()
        opts = ParseOptions(
            fname           = fname
            , id_prefix     = CMD.id_prefix
            , skip_preamble = CMD.skip_preamble
            , skip_epilog   = CMD.skip_epilog
            , out           = STREAM.appl_out
            , markup        = CMD.markup
            , verbose_warn  = not (CMD.sloppy)
            , exp_method    = CMD.symbols_exported_method
            , exp_ids       = CMD.symbols_exported_identifiers
            , known_attrs   = CMD.known_attrs
            ,)
        opts.set_defaults()

        if CMD.list_exports or CMD.list_internals:
            translator = ListTranslator(CMD.list_exports, CMD.list_internals)
            opts.gather_context = True

        elif CMD.use_names:
            opts.use_names  = CMD.use_names

        elif CMD.exported or CMD.internal:
            # gather exported symbols ...
            src   = readFile(opts.fname)
            ctx   = ParserContext()
            Parser.gather_context(src, ctx, opts)

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

        parser = Parser(opts, translator)
        parser.parse()
        parser.close()
        if parser.errors:
            retVal = 1

    return retVal

# ==============================================================================
# API
# ==============================================================================

# ------------------------------------------------------------------------------
class TranslatorAPI(object):
# ------------------------------------------------------------------------------
    u"""
    Abstract kernel-doc translator.

    :cvar list cls.HIGHLIGHT_MAP:  highlight mapping
    :cvar tuple cls.LINE_COMMENT:  tuple with start-/end- comment tags
    """

    HIGHLIGHT_MAP = [
        ( type_constant      , None )
        , ( type_func        , None )
        , ( type_param       , None )
        , ( type_struct_full , None )
        , ( type_struct      , None )
        , ( type_enum_full   , None )
        , ( type_env         , None )
        , ( type_member_func , None )
        , ( type_member      , None )
        , ]

    LINE_COMMENT = ("# ", "")

    def __init__(self):
        self.options = None
        self.parser  = None
        self.dumped_names = []
        self.translated_names = set()

    def setParser(self, parser):
        self.parser = parser
        self.dumped_names = []

    def setOptions(self, options):
        self.options = options

    def highlight(self, cont):
        u"""returns *highlighted* text"""
        if self.options.highlight:
            return highlight_parser(cont, self.HIGHLIGHT_MAP)
        return cont

    def get_preamble(self):
        retVal = ""
        if self.options.preamble == "":
            retVal = self.comment("src-file: %s" % (self.options.rel_fname or self.options.fname))
        elif self.options.preamble:
            retVal = self.options.preamble % self
        return retVal

    def get_epilog(self):
        retVal = ""
        if self.options.epilog == "":
            retVal = self.comment(
                "\nThis file was automatic generated / don't edit.")
        elif self.options.epilog:
            retVal = self.options.epilog % self
        return retVal

    @classmethod
    def comment(cls, cont):
        u"""returns *commented* text"""

        start, end = cls.LINE_COMMENT
        if not start and not end:
            return cont

        retVal = []
        for line in cont.split("\n"):
            if line.strip():
                retVal.append(start + line + end)
            else:
                retVal.append("")
        return "\n".join(retVal)

    def write(self, *objects):
        u"""Write *objects* to stream.

        Write Unicode-values of the *objects* to :py:attr:``self.options.out``.

        :param objects: The positional arguments are the objects with the
            content to write.
        """
        for obj in objects:
            cont = six.text_type(obj)
            self.options.out.write(cont)

    def write_comment(self, *objects):
        u"""Write *objects* as comments to stream."""
        for obj in objects:
            cont = six.text_type(obj)
            self.write(self.comment(cont))

    def eof(self):
        if self.options.eof_newline:
            self.write("\n")

    # API
    # ---

    def output_preamble(self):
        raise NotImplementedError

    def output_epilog(self):
        raise NotImplementedError

    def output_prefix(self):
        raise NotImplementedError

    def output_suffix(self):
        raise NotImplementedError

    def output_DOC(
            self
            , sections         = None # ctx.sections
            , ):
        raise NotImplementedError

    def output_function_decl(
            self
            , function         = None # ctx.decl_name
            , return_type      = None # ctx.return_type
            , parameterlist    = None # ctx.parameterlist
            , parameterdescs   = None # ctx.parameterdescs
            , parametertypes   = None # ctx.parametertypes
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , ):
        raise NotImplementedError

    def output_struct_decl(
            self
            , decl_name        = None # ctx.decl_name
            , decl_type        = None # ctx.decl_type
            , parameterlist    = None # ctx.parameterlist
            , parameterdescs   = None # ctx.parameterdescs
            , parametertypes   = None # ctx.parametertypes
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , definition       = None # ctx.definition
            , ):
        raise NotImplementedError

    def output_union_decl(self, *args, **kwargs):
        self.output_struct_decl(*args, **kwargs)

    def output_enum_decl(
            self
            , enum             = None # ctx.decl_name
            , parameterlist    = None # ctx.parameterlist
            , parameterdescs   = None # ctx.parameterdescs
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , ):
        raise NotImplementedError

    def output_typedef_decl(
            self
            , typedef          = None # ctx.decl_name
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , ):
        raise NotImplementedError

# ------------------------------------------------------------------------------
class NullTranslator(TranslatorAPI):
# ------------------------------------------------------------------------------
    u"""
    Null translator, translates nothing, just parse.
    """
    HIGHLIGHT_MAP = []
    LINE_COMMENT = ("", "")

    # pylint: disable=signature-differs
    def output_preamble(self, *args, **kwargs):
        pass
    def output_epilog(self, *args, **kwargs):
        pass
    def output_prefix(self):
        pass
    def output_suffix(self):
        pass
    def output_DOC(self, *args, **kwargs):
        pass
    def output_function_decl(self, *args, **kwargs):
        pass
    def output_struct_decl(self, *args, **kwargs):
        pass
    def output_union_decl(self, *args, **kwargs):
        pass
    def output_enum_decl(self, *args, **kwargs):
        pass
    def output_typedef_decl(self, *args, **kwargs):
        pass
    def eof(self):
        pass

# ------------------------------------------------------------------------------
class ListTranslator(TranslatorAPI):
# ------------------------------------------------------------------------------

    u"""
    Generates a list of kernel-doc symbols.
    """

    def __init__(self, list_exported, list_internal_types
                 , *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.list_exported       = list_exported
        self.list_internal_types = list_internal_types

        self.names = dict()
        for t in Parser.DOC_TYPES:
            self.names[t] = []

    def get_type(self, name):
        for t, l in self.names.items():
            if name in l:
                return t
        return None

    def output_preamble(self):
        pass

    def output_epilog(self):
        pass

    def output_prefix(self):
        pass

    def output_suffix(self):
        pass

    def output_DOC(self, sections = None):
        for header in sections.keys():
            self.names["DOC"].append(header)

    def output_function_decl(self, **kwargs):
        self.names["function"].append(kwargs["function"])

    def output_struct_decl(self, **kwargs):
        self.names["struct"].append(kwargs["decl_name"])

    def output_union_decl(self, **kwargs):
        self.names["union"].append(kwargs["decl_name"])

    def output_enum_decl(self, **kwargs):
        self.names["enum"].append(kwargs["enum"])

    def output_typedef_decl(self, **kwargs):
        self.names["typedef"].append(kwargs["typedef"])

    def eof(self):

        if self.list_exported:
            self.parser.info("list exported symbols")
            for name in self.parser.ctx.exported_symbols:
                t = self.get_type(name)
                if t is None:
                    self.parser.warn("exported symbol '%(name)s' is undocumented"
                                     , name = name)
                    t = "undocumented"
                self.write("[exported %-14s] %s \n" % (t, name))

        if self.list_internal_types:
            self.parser.info("list internal names")
            for t, l in self.names.items():
                if not ("all" in self.list_internal_types
                        or t in self.list_internal_types):
                    continue
                for name in l:
                    if name not in self.parser.ctx.exported_symbols:
                        self.write("[internal %-10s] %s \n" % (t, name))

# ------------------------------------------------------------------------------
class ReSTTranslator(TranslatorAPI):
# ------------------------------------------------------------------------------

    u"""
    Translate kernel-doc to reST markup.

    :cvar list HIGHLIGHT_map: Escape common reST (in-line) markups.  Classic
        kernel-doc comments contain characters and strings like ``*`` or
        trailing ``_``, which are in-line markups in reST. These special strings
        has to be masked in reST.

    """
    INDENT       = "    "
    LINE_COMMENT = (".. ", "")

    HIGHLIGHT_MAP = [
        # the regexpr are partial *overlapping*, mind the order!
        (   type_enum_full   , r"\ :c:type:`\1 \2 <\2>`\ " )
        , ( type_struct_full , r"\ :c:type:`\1 \2 <\2>`\ " )
        , ( type_typedef_full, r"\ :c:type:`\1 \2 <\2>`\ " )
        , ( type_union_full  , r"\ :c:type:`\1 \2 <\2>`\ " )
        , ( type_member_func , r"\ :c:type:`\1\2() <\1>`\ " )
        , ( type_member      , r"\ :c:type:`\1\2 <\1>`\ " )
        , ( type_func        , r"\ :c:func:`\1`\ ")
        , ( type_constant    , r"\ ``\1``\ " )
        , ( type_param       , r"\ ``\1``\ " )
        , ( type_env         , r"\ ``\1``\ " )
        , ( type_struct      , r"\ :c:type:`struct \1 <\1>`\ ")
        # at least replace escaped %, & and $
        , ( esc_type_prefix  , r"\1")
        , ]

    MASK_REST_INLINES = [
        (RE(r"(\w)_([\s\*])")  , r"\1\\_\2")  # trailing underline
        , (RE(r"([\s\*])_(\w)"), r"\1\\_\2")  # leading underline
        , (RE(r"(\*)")   , r"\\\1")  # emphasis
        , (RE(r"(`)")    , r"\\\1")  # interpreted text & inline literals
        , (RE(r"(\|)")   , r"\\\1")  # substitution references
        , ]

    FUNC_PTR = RE(r"([^\(]*\(\*)\s*\)\s*\(([^\)]*)\)")
    BITFIELD = RE(r"^(.*?)\s*(:.*)")

    def highlight(self, text):
        if self.options.markup == "kernel-doc":
            text = highlight_parser(text, self.MASK_REST_INLINES + self.HIGHLIGHT_MAP )
        elif self.options.markup == "reST":
            text = highlight_parser(text, self.HIGHLIGHT_MAP )
        return text

    def format_block(self, content):
        u"""format the content (string)"""
        lines = []
        if self.options.markup == "kernel-doc":
            lines = [ l.strip() for l in content.split("\n")]
        elif self.options.markup == "reST":
            lines = [ l.rstrip() for l in content.split("\n")]
        return "\n".join(lines)

    def write_anchor(self, refname):
        ID = refname
        if self.options.id_prefix:
            ID = self.options.id_prefix + "." + ID
        ID = normalize_id(ID)
        self.write("\n.. _`%s`:\n" % ID)

    HEADER_TAGS = (
        "#"   # level 0 / part with overline
        "="   # level 1 / chapter with overline
        "="   # level 2 / sec
        "-"   # level 3 / subsec
        "-"   # level 4 / subsubsec
        '"' ) # level 5 / para

    def write_header(self, header, sec_level=2):
        header = self.highlight(header)
        sectag = self.HEADER_TAGS[sec_level]
        if sec_level < 2:
            self.write("\n", (sectag * len(header)))
        self.write("\n%s" % header)
        self.write("\n", (sectag * len(header)), "\n")

    def write_section(self, header, content, sec_level=2, ID=None):
        if not self.options.no_header:
            if ID:
                self.write_anchor(ID)
            self.write_header(header, sec_level=sec_level)
        if header.lower() == "example":
            self.write("\n.. code-block:: c\n\n")
            for l in textwrap.dedent(content).split("\n"):
                if not l.strip():
                    self.write("\n")
                else:
                    self.write(self.INDENT, l, "\n")
        else:
            content = self.format_block(content)
            content = self.highlight(content)
            self.write("\n" + content)

        self.write("\n")

    def write_definition(self, term, definition, prefix=""):
        term  = normalize_ws(term) # term has to be a "one-liner"
        term  = self.highlight(term)
        if definition != Parser.undescribed:
            definition = self.format_block(definition)
            definition = self.highlight(definition)
        self.write("\n", prefix, term)
        for l in textwrap.dedent(definition).split("\n"):
            self.write("\n", prefix)
            if l.strip():
                self.write(self.INDENT, l)
        self.write("\n")

    def write_func_param(self, param, param_type, descr):
        param = param.replace("*", r"\*")
        self.write("\n", self.INDENT, param)

        if descr != Parser.undescribed:
            descr = self.format_block(descr)
            descr = self.highlight(descr)
        for l in textwrap.dedent(descr).split("\n"):
            self.write("\n")
            if l.strip():
                self.write(self.INDENT * 2, l)

        if param_type:
            param_type = param_type.replace("*", r"\*")
            self.write("\n", self.INDENT, param_type)

        self.write("\n")

    def output_preamble(self):
        self.parser.ctx.offset = 0
        if self.options.mode_line:
            self.write_comment(
                "-*- coding: %s; mode: rst -*-\n"
                % (getattr(self.options.out, "encoding", "utf-8") or "utf-8").lower())

        preamble = self.get_preamble()
        if preamble:
            self.write(preamble, "\n")

        if self.options.top_title:
            self.write_anchor(self.options.top_title)
            self.write_header(self.options.top_title, 0)
            if self.options.top_link:
                self.write("\n", self.options.top_link % self.options, "\n")

    def output_epilog(self):
        self.parser.ctx.offset = 0
        epilog = self.get_epilog()
        if epilog:
            self.write(epilog, "\n")

    def output_prefix(self):
        if compat.sphinx_has_c_namespace() and self.options.id_prefix:
            self.write(".. c:namespace-push:: %s" % self.options.id_prefix, "\n")

    def output_suffix(self):
        if compat.sphinx_has_c_namespace() and self.options.id_prefix:
            self.write("\n", ".. c:namespace-pop::", "\n")

    def output_DOC(self, sections = None):
        self.parser.ctx.offset = self.parser.ctx.decl_offset
        for header, content in sections.items():
            self.write_section(header, content, sec_level=2, ID=header)

    def output_function_decl(
            self
            , function         = None # ctx.decl_name
            , return_type      = None # ctx.return_type
            , parameterlist    = None # ctx.parameterlist
            , parameterdescs   = None # ctx.parameterdescs
            , parametertypes   = None # ctx.parametertypes
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , ):
        self.parser.ctx.offset = self.parser.ctx.decl_offset
        self.write_anchor(function)
        self.write_header(function, sec_level=2)

        if self.options.man_sect:
            self.write("\n.. kernel-doc-man:: %s.%s\n" % (function, self.options.man_sect) )

        # write function definition

        self.write("\n.. c:function:: ")
        if return_type and re.search(r"\s\*+$", return_type):
            self.write(return_type, function, "(")
        else:
            self.write(return_type, " ", function, "(")

        p_list = []

        for p_name in parameterlist:
            p_type = parametertypes[p_name]

            if self.FUNC_PTR.search(p_type):
                # pointer to function
                p_list.append("%s%s)(%s)"
                              % (self.FUNC_PTR[0], p_name, self.FUNC_PTR[1]))
            elif re.search(r"\s\*+$", p_type):
                # pointer
                p_list.append("%s%s" % (p_type, p_name))
            else:
                p_list.append("%s %s" % (p_type, p_name))

        p_line = ", ".join(p_list)
        self.write(p_line, ")\n")

        # purpose

        if purpose:
            self.write("\n", self.INDENT, self.highlight(purpose), "\n")

        # parameter descriptions

        for p_name in parameterlist:

            p_type = parametertypes[p_name]
            p_name = re.sub(r"\[.*", "", p_name)

            if p_name != "..." and "." in p_name:
                # @foo.bar sub-descriptions are printed below, ignore them here
                continue

            p_desc = parameterdescs[p_name]

            param = ""
            param_type = None
            if self.FUNC_PTR.search(p_type):
                # pointer to function
                param = ":param %s%s)(%s):" % (self.FUNC_PTR[0], p_name, self.FUNC_PTR[1])
            elif p_type.endswith("*"):
                # pointer & pointer to pointer
                param = ":param %s:" % (p_name)
                param_type = ":type %s: %s" % (p_name, p_type)
            elif p_name == "...":
                param = ":param ellipsis ellipsis:"
            else:
                param = ":param %s:" % (p_name)
                param_type = ":type %s: %s" % (p_name, p_type)

            self.parser.ctx.offset = parameterdescs.offsets.get(
                p_name, self.parser.ctx.offset)

            self.write_func_param(param, param_type, p_desc)

            # print all the @foo.bar sub-descriptions
            sub_descr = [x for x in parameterdescs.keys() if x.startswith(p_name + ".")]
            for _p_name in sub_descr:
                p_desc = parameterdescs.get(_p_name, None)
                # do not print undescribed sub-descriptions
                if p_desc == self.parser.undescribed:
                    continue
                self.parser.ctx.offset = parameterdescs.offsets.get(
                    _p_name, self.parser.ctx.offset)
                self.write_definition(_p_name, p_desc)

        # sections

        for header, content in sections.items():
            self.parser.ctx.offset = sections.offsets[header]
            self.write_section(
                header
                , content
                , sec_level = 3
                , ID = function + "." + header)

    def output_struct_decl(
            self
            , decl_name        = None # ctx.decl_name
            , decl_type        = None # ctx.decl_type
            , parameterlist    = None # ctx.parameterlist
            , parameterdescs   = None # ctx.parameterdescs
            , parametertypes   = None # ctx.parametertypes
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , definition       = None # ctx.definition
            , ):
        self.parser.ctx.offset = self.parser.ctx.decl_offset
        self.write_anchor(decl_name)
        self.write_header("%s %s" % (decl_type, decl_name), sec_level=2)

        if self.options.man_sect:
            self.write("\n.. kernel-doc-man:: %s.%s\n" % (decl_name, self.options.man_sect) )

        # write struct definition
        # see https://github.com/sphinx-doc/sphinx/issues/2713
        if compat.sphinx_has_c_types():
            self.write("\n.. c:%s:: %s\n\n" % (decl_type, decl_name))
        else:
            self.write("\n.. c:type:: %s %s\n\n" % (decl_type, decl_name))
        # purpose

        if purpose:
            self.write(self.INDENT, self.highlight(purpose), "\n")

        # definition

        self.write_anchor(decl_name + "." + Parser.section_def)
        self.write_header(Parser.section_def, sec_level=3)
        self.write("\n.. code-block:: c\n\n")
        self.write(self.INDENT, decl_type, " ", decl_name, " {\n")

        definition = re.sub(r"(([{;]))", r"\1\n", definition)
        level = 2
        enum = False
        for clause in definition.split('\n'):
            clause = normalize_ws(clause)
            if not clause:
                continue
            if clause[0] == "}" and level > 2:
                level -= 1
            if MACRO.match(clause):
                self.write(self.INDENT, clause[:-1].strip(), '\n')
            elif enum:
                for l in clause.split(','):
                    l = normalize_ws(l)
                    if l[0] == "}" and level > 2:
                        level -= 1
                        self.write(self.INDENT * level, l, '\n')
                    else:
                        self.write(self.INDENT * level, l, ',\n')
            else:
                self.write(self.INDENT * level, clause, '\n')
            if clause[-1] == "{":
                level += 1
                enum = clause.startswith('enum')

        self.write(self.INDENT, "}\n")

        # member description

        self.write_anchor(decl_name + "." + Parser.section_members)
        self.write_header(Parser.section_members, sec_level=3)

        for p_name in parameterlist:
            if MACRO.match(p_name):
                continue
            p_name = re.sub(r"\[.*", "", p_name)
            if "." in p_name:
                # @foo.bar sub-descriptions are printed below, ignore them here
                continue

            p_desc = parameterdescs.get(p_name, None)

            if p_desc is not None:
                self.parser.ctx.offset = parameterdescs.offsets.get(
                    p_name, self.parser.ctx.offset)
                self.write_definition(p_name, p_desc)

            # print all the @foo.bar sub-descriptions
            sub_descr = [x for x in parameterdescs.keys() if x.startswith(p_name + ".")]
            for _p_name in sub_descr:
                p_desc = parameterdescs.get(_p_name, None)
                # do not print undescribed sub-descriptions
                if p_desc == self.parser.undescribed:
                    continue
                self.parser.ctx.offset = parameterdescs.offsets.get(
                    _p_name, self.parser.ctx.offset)
                self.write_definition(_p_name, p_desc)

        # sections

        for header, content in sections.items():
            self.parser.ctx.offset = sections.offsets[header]
            self.write_section(
                header
                , content
                , sec_level = 3
                , ID = decl_name + "." + header)

    def output_enum_decl(
            self
            , enum             = None # ctx.decl_name
            , parameterlist    = None # ctx.parameterlist
            , parameterdescs   = None # ctx.parameterdescs
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , ):
        self.parser.ctx.offset = self.parser.ctx.decl_offset
        self.write_anchor(enum)
        self.write_header("enum %s" % enum, sec_level=2)

        if self.options.man_sect:
            self.write("\n.. kernel-doc-man:: %s.%s\n" % (enum, self.options.man_sect) )

        # write union definition
        # see https://github.com/sphinx-doc/sphinx/issues/2713
        if compat.sphinx_has_c_types():
            self.write("\n.. c:enum:: %s\n\n" % enum)
        else:
            self.write("\n.. c:type:: enum %s\n\n" % enum)

        # purpose

        if purpose:
            self.write(self.INDENT, self.highlight(purpose), "\n")

        # definition

        self.write_anchor(enum + "." + Parser.section_def)
        self.write_header(Parser.section_def, sec_level=3)
        self.write("\n.. code-block:: c\n\n")
        self.write(self.INDENT, "enum ", enum, " {")

        e_list = parameterlist[:]
        while e_list:
            e = e_list.pop(0)
            if MACRO.match(e):
                self.write("\n", self.INDENT, e)
            else:
                self.write("\n", self.INDENT * 2, e)
            if e_list:
                self.write(",")
        self.write("\n", self.INDENT, "};\n")

        # constants description

        self.write_anchor(enum + "." + Parser.section_constants)
        self.write_header(Parser.section_constants, sec_level=3)

        for p_name in parameterlist:
            p_desc = parameterdescs.get(p_name, None)
            self.parser.ctx.offset = parameterdescs.offsets.get(
                p_name, self.parser.ctx.offset)
            if p_desc is None:
                continue
            self.write_definition(p_name, p_desc)

        # sections

        for header, content in sections.items():
            self.parser.ctx.offset = sections.offsets[header]
            self.write_section(
                header
                , content or "???"
                , sec_level = 3
                , ID = enum + "." + header)

    def output_typedef_decl(
            self
            , typedef          = None # ctx.decl_name
            , sections         = None # ctx.sections
            , purpose          = None # ctx.decl_purpose
            , ):
        self.parser.ctx.offset = self.parser.ctx.decl_offset
        self.write_anchor(typedef)
        self.write_header("typedef %s" % typedef, sec_level=2)

        if self.options.man_sect:
            self.write("\n.. kernel-doc-man:: %s.%s\n" % (typedef, self.options.man_sect) )

        # write typdef definition
        # see https://github.com/sphinx-doc/sphinx/issues/2713
        if compat.sphinx_has_c_types():
            self.write("\n.. c:type:: %s\n\n" % typedef)
        else:
            self.write("\n.. c:type:: typedef %s\n\n" % typedef)
        if purpose:
            self.write(self.INDENT, self.highlight(purpose), "\n")

        for header, content in sections.items():
            self.parser.ctx.offset = sections.offsets[header]
            self.write_section(
                header
                , content or "???"
                , sec_level = 3
                , ID = typedef + "." + header)

# ------------------------------------------------------------------------------
class ParseOptions(Container):
# ------------------------------------------------------------------------------

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=global-statement

    PARSE_OPTION_RE = r"^/\*+\s*parse-%s:\s*([a-zA-Z0-9_-]*?)\s*\*/+\s*$"
    PARSE_OPTIONS   = [
        ("highlight", ["on","off"], "setOnOff")
        , ("INSPECT", ["on","off"], "setINSPECT")
        , ("markup",  ["reST", "kernel-doc"], "setVal")
        , ("SNIP",    [], "setVal")
        , ("SNAP",    [], "snap")
        , ]

    def dumpOptions(self):
        # dumps options which are variable from parsing source-code
        return dict(
            highlight = self.highlight
            , markup  = self.markup )

    def __init__(self, *args, **kwargs):

        self.id_prefix      = None  # A prefix for generated IDs.
        self.out            = None  # File descriptor for output.
        self.eof_newline    = True  # write newline on end of file

        self.src_tree       = SRCTREE # root folder of sources (defaults to CWD)
        self.rel_fname      = ""      # pathname relative to src_tree
        self.fname          = ""      # absolute pathname

        # self.encoding: the input encoding (encoding of the parsed source
        # file), the output encoding could be seek from the file-descriptor at
        # self.out.

        self.encoding       = "utf-8"
        self.tab_width      = 8  # tab-stops every n chars

        # control which content to print

        self.use_names     = []    # positive list of names to print / empty list means "print all"
        self.skip_names    = []    # negative list of names (not to print)
        self.use_all_docs  = False # True/False print all "DOC:" sections
        self.no_header     = False # skip section header
        self.error_missing = True  # report missing names as errors / else warning
        self.verbose_warn  = True  # more warn messages

        # self.gather_context: [True/False] Scan additional context from the
        # parsed source. E.g.: The list of exported symbols is a part of the
        # parser's context. If the context of exported symbols is needed, we
        # have to parse twice. First to find exported symbols, store them in the
        # context and a second once for *normal* parsing within this modified
        # *context*.

        self.gather_context    = False
        self.exp_method        = None
        self.exp_ids           = []
        self.known_attrs       = []

        # epilog / preamble

        self.skip_preamble  = False
        self.skip_epilog    = False
        self.mode_line      = True  # write mode-line in the very first line
        self.top_title      = ""    # write a title on top of the preamble
        self.top_link       = ""    # if top_title, add link to the *top* of the preamble
        self.preamble       = ""    # additional text placed into the preamble
        self.epilog         = ""    # text placed into the epilog

        # default's of filtered PARSE_OPTIONS

        self.opt_filters    = dict()
        self.markup         = "reST"
        self.highlight      = True  # switch highlighting on/off
        self.man_sect       = None  # insert ".. kernel-doc-man:" directive, section no self.man_sect
        self.add_filters(self.PARSE_OPTIONS)

        # SNIP / SNAP
        self.SNIP = None

        # init options with arguments from caller
        super().__init__(self, *args, **kwargs)

        # absolute and relativ filename

        if not self.fname:
            LOG.error("no source file given!")

        self.rel_fname = self.fname
        if self.fname[0] == '/':
            if not self.src_tree:
                LOG.error("missing SRCTREE")
            self.rel_fname = self.fname[1:]

        self.fname = os.path.abspath(self.src_tree + "/" + self.rel_fname)

    def set_defaults(self):

        # default way to identify exported symbol

        if not self.exp_method:
            self.exp_method = DEFAULT_EXP_METHOD

        if not self.exp_ids:
            self.exp_ids = DEFAULT_EXP_IDS

        # default top title and top link

        if self.fname and self.top_title == "":
            self.top_title = os.path.basename(self.fname)
        if self.top_title:
            self.top_title = self.top_title % self

        if self.top_link == "":
            if self.rel_fname:
                self.top_link  = GIT_REF % self
            else:
                LOG.warn("missing SRCTREE, can't set *top_link* option")
        if self.top_link:
            self.top_link = self.top_link % self

    def add_filters(self, parse_options):

        def setINSPECT(name, val): # pylint: disable=unused-argument
            global INSPECT
            INSPECT = bool(val == "on")

        _actions = dict(
            setOnOff     = lambda name, val: ( name, bool(val == "on") )
            , setVal     = lambda name, val: ( name, val )
            , snap       = lambda name, val: ( "SNIP", "" )
            , setINSPECT = setINSPECT
            , )

        for option, val_list, action in parse_options:
            self.opt_filters[option] = (
                RE(self.PARSE_OPTION_RE % option), val_list, _actions[action])

    def filter_opt(self, line, parser):

        for name, (regexpr, val_list, action) in self.opt_filters.items():
            if regexpr.match(line):
                line  = None
                value = regexpr[0]
                if val_list and value not in val_list:
                    parser.error("unknown parse-%(name)s value: '%(value)s'"
                                 , name=name, value=value)
                else:
                    opt_val = action(name, value)
                    if opt_val  is not None:
                        name, value = opt_val
                        self[name]  = value
                    parser.info(
                        "set parse-option: %(name)s = '%(value)s'"
                        , name=name, value=value)
                break
        return line

    def get_exported_symbols_re(self):
        if self.exp_method == 'macro':
            proto_pattern = r"^\s*(?:%s)\s*\(\s*(\w*)\s*\)\s*"
        elif self.exp_method == 'attribute':
            proto_pattern = r"(?:%s)(?:\s+\**\w+\**)*?\s+\**(\w+)\s*[(;]+"
        else:
            LOG.error("Unknown exported symbol method: %s" % self.exp_method)

        id_pattern = "|".join(["(?:" + name + ")" for name in self.exp_ids])
        return RE(proto_pattern % id_pattern, flags=re.M)

# ------------------------------------------------------------------------------
class ParserContext(Container):
# ------------------------------------------------------------------------------

    # pylint: disable=too-many-instance-attributes

    def dumpCtx(self):
        # dumps options which are variable from parsing source-code
        return dict(
            decl_offset = self.decl_offset )

    def __init__(self, *args, **kwargs):
        self.line_no           = 0
        self.contents          = ""
        self.section           = Parser.section_default

        # self.sections: ordered dictionary (list) of sections as they appear in
        # the source. The sections are set by Parser.dump_section
        self.sections          = collections.OrderedDict()
        self.sectcheck         = []

        self.prototype         = ""
        self.last_identifier   = ""

        # self.parameterlist: ordered list of the parameters as they appear in
        # the source. The parameter-list is set by Parser.push_parameter and
        # Parser.dump_enum
        self.parameterlist     = []

        # self.parametertypes: dictionary of <parameter-name>:<type>
        # key/values of the parameters. Set by Parser.push_parameter
        self.parametertypes    = dict()

        # self.parameterdescs: dictionary of <'@parameter'>:<description>
        # key/values of the parameters. Set by Parser.dump_section
        self.parameterdescs    = collections.OrderedDict()

        # self.constants: dictionary of <'%CONST'>:<description>
        # key/values. Set by Parser.dump_section
        self.constants         = dict()

        self.decl_name         = ""
        self.decl_type         = ""  # [struct|union|enum|typedef|function]
        self.decl_purpose      = ""
        self.definition        = ""  # defintion of the struct|union|enum
        self.return_type       = ""  # function's return type definition)

        #self.struct_actual     = ""

        # Additional context from the parsed source

        # self.exported: list of exported symbols
        self.exported_symbols  = []

        # self.mod_xxx: Module informations
        self.mod_authors       = []
        self.mod_descr         = ""
        self.mod_license       = ""

        # SNIP / SNAP
        self.snippets  = collections.OrderedDict()

        # the place, where type dumps are stored
        self.dump_storage = []

        # memo line numbers
        self.offset = 0
        self.last_offset = 0
        self.decl_offset = 0
        self.sections.offsets = dict()
        self.parameterdescs.offsets = dict()

        super().__init__(self, *args, **kwargs)

    def new(self):
        return self.__class__(
            line_no            = self.line_no
            , exported_symbols = self.exported_symbols
            , snippets         = self.snippets
            , dump_storage     = self.dump_storage )


class ParserBuggy(RuntimeError):
    u"""Exception raised when the parser implementation seems buggy.

    The parser implementation perform some integrity tests at runtime.  This
    exception type mainly exists to improve the regular expressions which are
    used to parse and analyze the kernels source code.

    In the exception message the last position the parser parsed is stored, this
    position may, but does not need to be related with the exception (it is only
    an additional information which might help).

    Under normal circumstances, exceptions of this type should never arise,
    unless the implementation of the parser is buggy."""

    def __init__(self, parserObj, message):

        message = ("last parse position %s:%s\n"
                   % (parserObj.ctx.line_no, parserObj.options.fname)
                   + message)
        super().__init__(message)
        self.parserObj = parserObj

# ------------------------------------------------------------------------------
class Parser(SimpleLog):
# ------------------------------------------------------------------------------

    # pylint: disable=too-many-public-methods

    u"""
    kernel-doc comments parser

    States:

    * 0 - normal code
    * 1 - looking for function name
    * 2 - scanning field start.
    * 3 - scanning prototype.
    * 4 - documentation block
    * 5 - gathering documentation outside main block (see Split Doc State)

    Split Doc States:

    * 0 - Invalid (Before start or after finish)
    * 1 - Is started (the /\\*\\* was found inside a struct)
    * 2 - The @parameter header was found, start accepting multi paragraph text.
    * 3 - Finished (the \\*/ was found)
    * 4 - Error: Comment without header was found. Spit a error as it's not
          proper kernel-doc and ignore the rest.
    """

    LOG_FORMAT = "%(fname)s:%(line_no)s: :%(logclass)s: %(message)s\n"

    # DOC_TYPES: types of documentation gathered by the parser
    DOC_TYPES      = ["DOC", "function", "struct", "union", "enum", "typedef"]

    undescribed      = "*undescribed*"

    section_descr     = "Description"
    section_def       = "Definition"
    section_members   = "Members"
    section_constants = "Constants"
    section_intro     = "Introduction"
    section_context   = "Context"
    section_return    = "Return"
    section_default   = section_descr

    special_sections  = [ section_descr
                          , section_def
                          , section_members
                          , section_constants
                          , section_context
                          , section_return ]

    def __init__(self, options, translator):
        super().__init__()

        # raw data akku
        self.rawdata    = ""

        # flags:
        self.state = 0
        self.split_doc_state   = 0
        self.in_doc_sect       = False
        self.in_purpose        = False
        self.brcount           = 0
        self.warnings          = 0
        self.errors            = 0
        self.anon_struct_union = False

        self.options    = None
        self.translator = None
        self.ctx        = ParserContext()

        self.setTranslator(translator)
        self.setOptions(options)

    def setTranslator(self, translator):
        self.translator = translator
        self.translator.setParser(self)
        self.translator.setOptions(self.options)

    def setOptions(self, options):
        self.options = options
        self.translator.setOptions(options)

    def reset_state(self):
        self.ctx = self.ctx.new()
        self.state             = 0
        self.split_doc_state   = 0
        self.in_doc_sect       = False
        self.in_purpose        = False
        self.brcount           = 0
        self.anon_struct_union = False

    # ------------------------------------------------------------
    # Log
    # ------------------------------------------------------------

    def error(self, message, _line_no=None, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        self.errors += 1
        super().error(message, **replace)

    def warn(self, message, _line_no=None, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        self.warnings += 1
        super().warn(message, **replace)

    def info(self, message, _line_no=None, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        super().info(message, **replace)

    def debug(self, message, _line_no=None, **replace):
        replace["fname"]   = self.options.fname
        replace["line_no"] = replace.get("line_no", self.ctx.line_no)
        super().debug(message, **replace)

    # ------------------------------------------------------------
    # state parser
    # ------------------------------------------------------------

    @classmethod
    def gather_context(cls, src, ctx, opts):
        u"""Scan source about context informations.

        Scans *whole* source (e.g. :py:attr:`Parser.rawdata`) about data relevant
        for the context (e.g. exported symbols).

        Names of exported symbols gathered in :py:attr:`ParserContext.exported`.
        The list contains names (symbols) which are exported using the
        pattern specified in opts.

        .. hint::

          A exported symbol does not necessarily have a corresponding source code
          comment with a documentation.

        Module information comes from the ``MODULE_xxx`` macros.  Module
        informations are gathered in ``ParserContext.module_xxx``:

        * ``MODULE_AUTHOR("...")``: Author entries are collected in a list in
          :py:attr:`ParserContext.mod_authors`

        * ``MODULE_DESCRIPTION("...")``: A concatenated string in
          :py:attr:`ParserContext.mod_descr`

        * ``MODULE_LICENSE("...")``: String with comma separated licenses in
          :py:attr:`ParserContext.mod_license`.

        .. hint::

           While parsing header files, about kernel-doc, you will not find the
           ``MODULE_xxx`` macros, because they are commonly used in the ".c"
           files.
        """

        expsym_re = opts.get_exported_symbols_re()
        LOG.debug("gather_context() regExp: %(pattern)s", pattern=expsym_re.pattern)
        for name in expsym_re.findall(src):
            LOG.info("exported symbol: %(name)s", name = name)
            ctx.exported_symbols.append(name)

        LOG.debug("gather_context() regExp: %(pattern)s", pattern=MODULE_INFO.pattern)

        for match in MODULE_INFO.findall(src):
            info_type = match[1]
            content   = match[2]
            if info_type == "AUTHOR":
                ctx.mod_authors.append(content)
            elif info_type == "DESCRIPTION":
                ctx.mod_descr   += content + " "
            elif info_type == "LICENSE":
                ctx.mod_license += content + ", "

        LOG.info("mod_authors: %(x)s",  x = ctx.mod_authors)
        LOG.info("mod_descr: %(x)s",    x = ctx.mod_descr)
        LOG.info("mod_license : %(x)s", x = ctx.mod_license)

    def parse(self, src=None): # start parsing
        self.dump_preamble()
        self.dump_prefix()
        if src is not None:
            for line in src:
                self.feed(line)
        else:
            with openTextFile(self.options.fname, encoding=self.options.encoding) as srcFile:
                for line in srcFile:
                    self.feed(line)
        self.dump_suffix()
        self.dump_epilog()
        self.translator.eof()

    def parse_dump_storage(self, translator=None, options=None):
        if options is not None:
            self.setOptions(options)
        if translator is not None:
            self.setTranslator(translator)
        self.dump_preamble()
        self.dump_prefix()
        for name, out_type, opts, ctx, kwargs in self.ctx.dump_storage:
            self.options.update(opts)
            self.ctx.update(ctx)
            self.output_decl(name, out_type, **kwargs)
        self.dump_suffix()
        self.dump_epilog()
        self.translator.eof()

    def close(self):           # end parsing
        self.feed("", eof=True)
        # log requested but missed documentation
        log_missed = self.error
        if not self.options.error_missing:
            log_missed = self.warn

        if isinstance(self.translator, NullTranslator):
            # the NullTranslator does not translate / translated_names is
            # empty
            pass
        elif isinstance(self.translator, ListTranslator):
            self.parse_dump_storage()
        else:
            for name in self.options.use_names:
                if name not in self.translator.translated_names:
                    log_missed("no documentation for '%(name)s' found", name=name)

        if self.errors or self.warnings:
            self.warn("total errors: %(errors)s / total warnings: %(warnings)s"
                      , errors=self.errors, warnings=self.warnings)
            self.warnings -= 1
        global INSPECT  # pylint: disable=global-statement
        INSPECT = False

    def feed(self, data, eof=False):
        self.rawdata = self.rawdata + data

        if self.options.gather_context:
            # Scan additional context from the parsed source. For this, collect
            # all lines in self.rawdata until EOF. On EOF, scan rawdata about
            # (e.g.) exported symbols and after this, continue with the *normal*
            # parsing.
            if not eof:  # pylint: disable=no-else-return
                return
            else:
                self.gather_context(self.rawdata, self.ctx, self.options)

        lines = self.rawdata.split("\n")

        if not eof:
            # keep last line, until EOF
            self.rawdata = lines[-1]
            lines = lines[:-1]

        for l in lines:
            l = l.expandtabs(self.options.tab_width)
            self.ctx.line_no += 1
            l = self.options.filter_opt(l, self)
            if l is None:
                continue

            if self.options.SNIP:
                # record snippet
                val = self.ctx.snippets.get(self.options.SNIP, "")
                if val or l:
                    self.ctx.snippets[self.options.SNIP] = val + l + "\n"

            state = getattr(self, "state_%s" % self.state)
            try:
                state(l)
            except Exception as _exc:
                self.warn("total errors: %(errors)s / warnings: %(warnings)s"
                          , errors=self.errors, warnings=self.warnings)
                self.warnings -= 1
                self.error("unhandled exception in line: %(l)s", l=l)
                raise

    def output_decl(self, name, out_type, **kwargs):
        self.ctx.offset = self.ctx.decl_offset

        if name in self.translator.dumped_names:
            self.error("name '%s' used several times" % name)
        self.translator.dumped_names.append(name)

        if isinstance(self.translator, NullTranslator):
            self.ctx.dump_storage.append(
                ( name
                  , out_type
                  , self.options.dumpOptions()
                  , self.ctx.dumpCtx()
                  , copy.deepcopy(kwargs) ) )
            return

        do_translate = False
        if name in self.options.skip_names:
            do_translate = False
        elif name in self.options.use_names:
            do_translate = True
        elif out_type != "DOC"  and not self.options.use_names:
            do_translate = True
        elif out_type == "DOC" and self.options.use_all_docs:
            do_translate = True
        if do_translate:
            self.translator.translated_names.add(name)
            out_func = getattr(self.translator, "output_%s" % out_type)
            out_func(**kwargs)
        else:
            self.debug("skip translation of %(t)s: '%(n)s'", t=out_type, n=name)

    def state_0(self, line):
        u"""state: 0 - normal code"""

        if doc_start.match(line):
            self.debug("START: kernel-doc comment / switch state 0 --> 1")
            self.ctx.decl_offset = self.ctx.line_no + 1
            self.state = 1
            self.in_doc_sect = False

    def state_1(self, line):
        u"""state: 1 - looking for function name"""

        if doc_block.match(line):
            self.debug("START: DOC block / switch state 1 --> 4")
            self.ctx.last_offset = self.ctx.line_no + 1
            self.state = 4
            self.ctx.contents = ""
            self.ctx.section =  self.section_intro
            if doc_block[0].strip():
                self.ctx.section = self.sect_title(doc_block[0])
            self.info("DOC: %(sect)s", sect=self.ctx.section)

        elif doc_decl.match(line):
            self.debug("START: declaration / switch state 1 --> 2")
            self.ctx.last_offset = self.ctx.line_no + 1
            self.state = 2

            identifier = doc_decl[0].strip()
            self.ctx.decl_type = "function"
            if doc_decl_ident.match(line):
                identifier = doc_decl_ident[1]
                self.ctx.decl_type = doc_decl_ident[0]
            self.ctx.last_identifier = identifier.strip()

            self.debug("FLAG: in_purpose=True")
            self.in_purpose = True
            self.info("scanning doc for: %(t)s '%(i)s'", t=self.ctx.decl_type, i = identifier)

            self.ctx.decl_purpose = ""
            if doc_decl_purpose.search(line):
                self.ctx.decl_purpose = doc_decl_purpose[0].strip()

            if not self.ctx.decl_purpose:
                self.warn("missing initial short description of '%(i)s'"
                          , i=self.ctx.last_identifier)

        else:
            self.warn("can't understand: -->|%(line)s|<--"
                      " - I thought it was a doc line" , line=line)
            self.state = 0

    def sect_title(self, title):
        u"""Normalize common section titles"""
        # fix varius notations for the "Return:" section

        retVal = title

        if title.lower() in ["description", ]:
            retVal = self.section_descr

        elif title.lower() in ["introduction", "intro"]:
            retVal = self.section_intro

        elif title.lower() in ["context", ]:
            retVal = self.section_context

        elif title.lower() in ["return", "returns"]:
            retVal = self.section_return

        return retVal

    def state_2(self, line):
        u"""state: 2 - scanning field start. """

        new_sect = ""
        new_cont = ""

        if not doc_sect_except.match(line):

            # probe different sect start pattern ...

            if self.options.markup == "reST":
                if doc_sect_reST.match(line):
                    # this is a line with a parameter definition or vintage
                    # section "Context: lorem", "Return: lorem" etc.
                    new_sect = self.sect_title(doc_sect_reST[0].strip())
                    new_cont = doc_sect_reST[1].strip()
                elif reST_sect.match(line):
                    # this is a line with a section definition "Section name:\n"
                    new_sect = self.sect_title(reST_sect[0].strip())
                    new_cont = ""

                # Sub-sections in parameter descriptions are not provided,
                # with the exception of special_sections names. To allow
                # comments like:
                #   * @arg: lorem
                #   * Return: foo
                if ( new_sect
                     and self.ctx.section.startswith("@")
                     and not new_sect.startswith("@")
                     and not new_sect in self.special_sections ):
                    new_sect = ""
                    new_cont = ""

            else:  # kernel-doc vintage mode
                if doc_sect.match(line):
                    # this is a line with a parameter or section definition
                    new_sect = self.sect_title(doc_sect[0].strip())
                    new_cont = doc_sect[1].strip()

        if new_sect:

            # a new section starts *here*

            self.debug("found new section --> %(sect)s", sect=new_sect)

            if self.ctx.contents.strip():
                if not self.in_doc_sect:
                    self.warn("contents before sections '%(c)s'" , c=self.ctx.contents.strip())
                self.dump_section(self.ctx.section, self.ctx.contents)
                self.ctx.section  = self.section_default
                self.ctx.contents = ""

            self.debug("new_sect: '%(sec)s' / desc: '%(desc)s'", sec = new_sect, desc = new_cont)
            self.ctx.last_offset = self.ctx.line_no

            self.in_doc_sect = True
            self.in_purpose  = False
            self.debug("FLAGs: in_doc_sect=%(s)s / in_purpose=%(p)s", s=self.in_doc_sect, p=self.in_purpose)

            self.ctx.section  = new_sect
            if new_cont:
                self.ctx.contents = new_cont + "\n"
            self.info("section: %(sec)s" , sec=self.ctx.section)

        elif doc_end.search(line):

            # end of the comment-block

            if self.ctx.contents:
                self.dump_section(self.ctx.section, self.ctx.contents)
                self.ctx.section  = self.section_default
                self.ctx.contents = ""

            # look for doc_com + <text> + doc_end:
            if RE(doc_com.pattern + r"[a-zA-Z_0-9:\.]+" + doc_end.pattern).match(line):
                self.warn("suspicious ending line")

            self.ctx.prototype = ""
            self.debug("END doc block / switch state 2 --> 3")
            self.debug("end of doc comment, looking for prototype")
            self.state   = 3
            self.brcount = 0

        elif doc_content.match(line):

            # a comment line with *content* of a section or a *purpose*

            cont_line = doc_content[0]

            if not cont_line.strip():
                # it's a empty line

                if self.in_purpose:

                    # empty line after short description (*purpose*) introduce the
                    # "Description" section

                    self.debug("found empty line in *purpose* --> start 'Description' section")
                    if self.ctx.contents.strip():
                        if not self.in_doc_sect:
                            self.warn("contents before sections '%(c)s'" , c=self.ctx.contents.strip())
                        self.dump_section(self.ctx.section, self.ctx.contents)

                    self.ctx.section  = self.section_descr
                    self.ctx.contents = ""
                    self.in_doc_sect  = True
                    self.in_purpose   = False
                    self.debug("FLAGs: in_doc_sect=%(s)s / in_purpose=%(p)s", s=self.in_doc_sect, p=self.in_purpose)

                elif (self.ctx.section.startswith("@")
                      or self.ctx.section == self.section_context):

                    # miguel-style comment kludge, look for blank lines after @parameter
                    # line to signify start of description

                    self.debug("blank lines after @parameter --> start 'Description' section")
                    self.dump_section(self.ctx.section, self.ctx.contents)
                    self.ctx.last_offset = self.ctx.line_no
                    self.ctx.section  = self.section_descr
                    self.ctx.contents = ""
                    self.in_doc_sect  = True
                    self.debug("FLAGs: in_doc_sect=%(s)s / in_purpose=%(p)s", s=self.in_doc_sect, p=self.in_purpose)

                else:
                    self.ctx.contents += "\n"

            elif self.in_purpose:
                # Continued declaration purpose, dismiss leading whitespace
                if self.ctx.decl_purpose:
                    self.ctx.decl_purpose += " " + cont_line.strip()
                else:
                    self.ctx.decl_purpose = cont_line.strip()
            else:
                if ( self.options.markup == "reST"
                     and self.ctx.section.startswith("@")):
                    # FIXME: I doubt if it is a good idea to strip leading
                    # whitespaces in parameter description, but *over all* we
                    # get better reST output.
                    cont_line = cont_line.strip()
                    # Sub-sections in parameter descriptions are not provided,
                    # but if this is a "lorem:\n" line create a new paragraph.
                    if reST_sect.match(line) and not doc_sect_except.match(line):
                        cont_line = "\n" + cont_line + "\n"

                self.ctx.contents += cont_line + "\n"

        else:
            # i dont know - bad line?  ignore.
            self.warn("bad line: '%(line)s'", line = line.strip())

    def state_3(self, line):
        u"""state: 3 - scanning prototype."""

        if line.startswith('typedef'):
            if not self.ctx.decl_type == 'typedef':
                self.warn(
                    "typedef of function pointer not marked"
                    " as typdef, use: 'typedef %s' in the comment."
                    % (self.ctx.last_identifier)
                    , line_no = self.ctx.decl_offset)
            self.ctx.decl_type = 'typedef'

        if doc_state5_oneline.match(line):
            sect = doc_state5_oneline[0].strip()
            cont = doc_state5_oneline[1].strip()
            if cont and sect:
                self.ctx.section  = self.sect_title(sect)
                self.ctx.contents = cont
                self.dump_section(self.ctx.section, self.ctx.contents)
                self.ctx.section  = self.section_default
                self.ctx.contents = ""

        elif doc_state5_start.match(line):
            self.debug("FLAG: split_doc_state=1 / switch state 3 --> 5")
            self.state = 5
            self.split_doc_state = 1
            if self.ctx.decl_type == 'function':
                self.error("odd construct, gathering documentation of a function"
                           " outside of the main block?!?")

        elif self.ctx.decl_type == 'function':
            self.process_state3_function(line)
        else:
            self.process_state3_type(line)

    def state_4(self, line):
        u"""state: 4 - documentation block"""

        if doc_block.match(line):
            # a new DOC block arrived, dump the last section and pass the new
            # DOC block to state 1.
            self.dump_DOC(self.ctx.section, self.ctx.contents)
            self.ctx = self.ctx.new()
            self.debug("END & START: DOC block / switch state 4 --> 1")
            self.state = 1
            self.state_1(line)

        elif doc_end.match(line):
            # the DOC block ends here, dump it and reset to state 0
            self.debug("END: DOC block / dump doc section / switch state 4 --> 0")
            self.dump_DOC(self.ctx.section, self.ctx.contents)
            self.ctx = self.ctx.new()
            self.state = 0

        elif doc_content.match(line):
            cont = doc_content[0]
            if ( not cont.strip() # dismiss leading newlines
                 and not self.ctx.contents):
                pass
            else:
                self.ctx.contents += doc_content[0] + "\n"

    def state_5(self, line):
        u"""state: 5 - gathering documentation outside main block"""

        if ( self.split_doc_state == 1
             and doc_state5_sect.match(line)):

            # First line (split_doc_state 1) needs to be a @parameter
            self.ctx.section  = self.sect_title(doc_state5_sect[0].strip())
            self.ctx.contents = doc_state5_sect[1].strip()
            self.split_doc_state = 2
            self.debug("SPLIT-DOC-START: '%(param)s' / split-state 1 --> 2"
                       , param = self.ctx.section)
            self.ctx.last_offset = self.ctx.line_no
            self.info("section: %(sec)s" , sec=self.ctx.section)

        elif doc_state5_end.match(line):
            # Documentation block end
            self.debug("SPLIT-DOC-END: ...")

            if not self.ctx.contents.strip():
                self.debug("SPLIT-DOC-END: ... no description to dump")

            else:
                self.dump_section(self.ctx.section, self.ctx.contents)
                self.ctx.section  = self.section_default
                self.ctx.contents = ""

            self.debug("SPLIT-DOC-END: ... split-state --> 0  / state = 3")
            self.state = 3
            self.split_doc_state = 0

        elif doc_content.match(line):
            # Regular text
            if self.split_doc_state == 2:
                self.ctx.contents += doc_content[0] + "\n"

            elif self.split_doc_state == 1:
                self.split_doc_state = 4
                self.error("Comment without header was found split-state --> 4")
                self.warn("Incorrect use of kernel-doc format: %(line)s"
                          , line = line)

    # ------------------------------------------------------------
    # helper to parse special objects
    # ------------------------------------------------------------

    def process_state3_function(self, line):

        self.debug("PROCESS-FUNCTION: %(line)s", line=line)
        line = C99_comments.sub("", line) # strip C99-style comments to end of line
        line = line.strip()

        stripProto = RE(r"([^\{]*)")

        # ?!?!? MACDOC does not exists (any more)?
        # if ($x =~ m#\s*/\*\s+MACDOC\s*#io || ($x =~ /^#/ && $x !~ /^#\s*define/)) {
        #   do nothing
        # }

        if line.startswith("#") and not MACRO_define.search(line):
            # do nothing
            pass
        elif stripProto.match(line):
            self.ctx.prototype += " " + stripProto[0]

        if ( MACRO_define.search(line)
             or "{" in line
             or ";" in line ):

            # strip cr&nl, strip C89 comments, strip leading whitespaces
            self.ctx.prototype = C89_comments.sub(
                "", CR_NL.sub(" ", self.ctx.prototype)).lstrip()

            if SYSCALL_DEFINE.search(self.ctx.prototype):
                self.ctx.prototype = self.syscall_munge(self.ctx.prototype)

            if ( TRACE_EVENT.search(self.ctx.prototype)
                 or DEFINE_EVENT.search(self.ctx.prototype)
                 or DEFINE_SINGLE_EVENT.search(self.ctx.prototype) ):
                self.ctx.prototype = self.tracepoint_munge(self.ctx.prototype)

            self.ctx.prototype = self.ctx.prototype.strip()
            self.info("prototype --> '%(proto)s'", proto=self.ctx.prototype)
            self.dump_function(self.ctx.prototype)
            self.reset_state()

    def syscall_munge(self, prototype):
        self.debug("syscall munge: '%(prototype)s'" , prototype=prototype)
        void = False

        # strip needles whitespaces
        prototype = normalize_ws(prototype)

        if SYSCALL_DEFINE0.search(prototype):
            void = True
        prototype = SYSCALL_DEFINE.sub("long sys_", prototype)
        if not self.ctx.last_identifier.startswith("sys_"):
            self.ctx.last_identifier = "sys_%s" % self.ctx.last_identifier

        if re.search(r"long (sys_.*?),", prototype):
            prototype = prototype.replace(",", "(", 1)
        elif void:
            prototype = prototype.replace(")","(void)",1)

        # now delete all of the odd-number commas in $prototype
        # so that arg types & arg names don't have a comma between them

        retVal = prototype
        if not void:
            x = prototype.split(",")
            y = []
            while x:
                y.append(x.pop(0) + x.pop(0))
            retVal = ",".join(y)
        self.debug("syscall munge: retVal '%(retVal)s'" , retVal=retVal)
        return retVal

    def tracepoint_munge(self, prototype):
        self.debug("tracepoint munge: %(prototype)s" , prototype=prototype)

        retVal  = prototype
        tp_name = ""
        tp_args = ""

        if TRACE_EVENT_name.match(prototype):
            tp_name = TRACE_EVENT_name[0]

        elif DEFINE_SINGLE_EVENT_name.match(prototype):
            tp_name = DEFINE_SINGLE_EVENT_name[0]

        elif DEFINE_EVENT_name.match(prototype):
            tp_name = DEFINE_EVENT_name[1]

        tp_name = tp_name.lstrip()

        if TP_PROTO.search(prototype):
            tp_args = TP_PROTO[0]

        if not tp_name.strip() or not tp_args.strip():
            self.warn("Unrecognized tracepoint format: %(prototype)s"
                      , prototype=prototype)
        else:
            if not self.ctx.last_identifier.startswith("trace_"):
                self.ctx.last_identifier = "trace_%s" % self.ctx.last_identifier
            retVal = ("static inline void trace_%s(%s)"
                      % (tp_name, tp_args))
        return retVal

    def process_state3_type(self, line):
        self.debug("PROCESS-TYPE: %(line)s", line=line)

        # strip cr&nl, strip C99 comments, strip leading&trailing whitespaces
        line = C99_comments.sub("", CR_NL.sub(" ", line)).strip()

        if MACRO.match(line):
            # To distinguish preprocessor directive from regular declaration
            # later (drop-semicolon).
            line += ";"

        m = RE(r"([^{};]*)([{};])(.*)")

        while True:
            if m.search(line):
                if self.ctx.prototype:
                    self.ctx.prototype += " "
                self.ctx.prototype += m[0] + m[1]
                if m[1] == "{":
                    self.brcount += 1
                if m[1] == "}":
                    self.brcount -= 1
                if m[1] == ";" and self.brcount == 0:
                    self.info("prototype --> '%(proto)s'", proto=self.ctx.prototype)
                    self.debug("decl_type: %(decl_type)s", decl_type=self.ctx.decl_type)
                    if self.ctx.decl_type == "union":
                        self.dump_union(self.ctx.prototype)
                    elif self.ctx.decl_type == "struct":
                        self.dump_struct(self.ctx.prototype)
                    elif self.ctx.decl_type == "enum":
                        self.dump_enum(self.ctx.prototype)
                    elif self.ctx.decl_type == "typedef":
                        self.dump_typedef(self.ctx.prototype)
                    else:
                        raise ParserBuggy(
                            self, "unknown decl_type: %s" % self.ctx.decl_type)

                    self.reset_state()
                    break
                line = m[2]
            else:
                self.ctx.prototype += line
                break

    # ------------------------------------------------------------
    # dump objects
    # ------------------------------------------------------------

    def dump_preamble(self):
        if not self.options.skip_preamble:
            self.translator.output_preamble()

    def dump_epilog(self):
        if not self.options.skip_epilog:
            self.translator.output_epilog()

    def dump_prefix(self):
        self.translator.output_prefix()

    def dump_suffix(self):
        self.translator.output_suffix()

    def dump_section(self, name, cont):
        u"""Store section's *content* under it's name.

        :param str name: name of the section
        :param str cont: content of the section

        Stores the *content* under section's *name* in one of the *container*. A
        container is a hash object, the section name is the *key* and the
        content is the *value*.

        Container:

        * self.ctx.constants:       holds constant's descriptions
        * self.ctx.parameterdescs:  holds parameter's descriptions
        * self.ctx.sections:        holds common sections like "Return:"

        There are the following contai
        """
        self.debug("dump_section(): %(name)s", name = name)
        name = name.strip()
        cont = cont.rstrip() # dismiss trailing whitespace
        # FIXME: sections with '%CONST' prefix no longer exists
        # _type_constant     = RE(r"\%([-_\w]+)")
        #if _type_constant.match(name):  # '%CONST' - name of a constant.
        #    name = _type_constant[0]
        #    self.debug("constant section '%(name)s'",  name = name)
        #    if self.ctx.constants.get(name, None):
        #        self.error("duplicate constant definition '%(name)s'"
        #                   , name = name)
        #    self.ctx.constants[name] = cont

        _type_param  = RE(r"\@(\w[.\w]*)")  # match @foo and @foo.bar
        if _type_param.match(name):   # '@parameter' - name of a parameter
            name = _type_param[0]
            self.debug("parameter definition '%(name)s'", name = name)
            if self.ctx.parameterdescs.get(name, None):
                self.error("duplicate parameter definition '%(name)s'"
                           , name = name, line_no = self.ctx.last_offset )
            self.ctx.parameterdescs[name] = cont
            self.ctx.parameterdescs.offsets[name] = self.ctx.last_offset
            self.ctx.sectcheck.append(name)

        elif name == "@...":
            self.debug("parameter definiton '...'")
            name = "..."
            if self.ctx.parameterdescs.get(name, None):
                self.error("parameter definiton '...'"
                           , line_no = self.ctx.last_offset )
            self.ctx.parameterdescs[name] = cont
            self.ctx.parameterdescs.offsets[name] = self.ctx.last_offset
            self.ctx.sectcheck.append(name)
        else:
            self.debug("other section '%(name)s'", name = name)
            if self.ctx.sections.get(name, None):
                self.warn("duplicate section name '%(name)s'"
                          , name = name, line_no = self.ctx.last_offset )
                self.ctx.sections[name] += "\n\n" + cont
            else:
                self.ctx.sections[name] = cont
            self.ctx.sections.offsets[name] = self.ctx.last_offset

    def dump_function(self, proto):
        self.debug("dump_function(): (1) '%(proto)s'", proto=proto)
        hasRetVal = True
        proto = re.sub( r"^static +"         , "", proto )
        proto = re.sub( r"^extern +"         , "", proto )
        proto = re.sub( r"^asmlinkage +"     , "", proto )
        proto = re.sub( r"^inline +"         , "", proto )
        proto = re.sub( r"^__inline__ +"     , "", proto )
        proto = re.sub( r"^__inline +"       , "", proto )
        proto = re.sub( r"^__always_inline +", "", proto )
        proto = re.sub( r"^noinline +"       , "", proto )
        proto = re.sub( r"__init +"          , "", proto )
        proto = re.sub( r"__init_or_module +", "", proto )
        proto = re.sub( r"__meminit +"       , "", proto )
        proto = re.sub( r"__must_check +"    , "", proto )
        proto = re.sub( r"__weak +"          , "", proto )

        # Remove known attributes from function prototype
        known_attrs = self.options.known_attrs
        if self.options.exp_method == 'attribute':
            known_attrs.extend(self.options.exp_ids)
        for attr in known_attrs:
            proto = re.sub(r"%s +" % attr, "", proto)

        define = bool(MACRO_define.match(proto))
        proto = MACRO_define.sub("", proto )

        proto = re.sub( r"__attribute__\s*\(\("
                        r"(?:"
                        r"[\w\s]+"          # attribute name
                        r"(?:\([^)]*\))?"   # attribute arguments
                        r"\s*,?"            # optional comma at the end
                        r")+"
                        r"\)\)\s+"
                        , ""
                        , proto)

        # Yes, this truly is vile.  We are looking for:
        # 1. Return type (may be nothing if we're looking at a macro)
        # 2. Function name
        # 3. Function parameters.
        #
        # All the while we have to watch out for function pointer parameters
        # (which IIRC is what the two sections are for), C types (these
        # regexps don't even start to express all the possibilities), and
        # so on.
        #
        # If you mess with these regexps, it's a good idea to check that
        # the following functions' documentation still comes out right:
        # - parport_register_device (function pointer parameters)
        # - atomic_set (macro)
        # - pci_match_device, __copy_to_user (long return type)

        self.debug("dump_function(): (2) '%(proto)s'", proto=proto)

        x = RE(r"^()([a-zA-Z0-9_~:]+)\s+")

        if define and x.match(proto):
            # This is an object-like macro, it has no return type and no
            # parameter list.  Function-like macros are not allowed to have
            # spaces between decl_name and opening parenthesis (notice
            # the \s+).
            self.ctx.return_type = x[0]
            self.ctx.decl_name   = x[1]
            hasRetVal = False
            self.debug("dump_function(): (hasRetVal = False) '%(proto)s'"
                       , proto=proto)
        else:
            matchExpr = None
            for regexp in FUNC_PROTOTYPES:
                if regexp.match(proto):
                    matchExpr = regexp
                    self.debug("dump_function(): matchExpr = '%(pattern)s' // '%(proto)s'"
                               , pattern = matchExpr.pattern, proto=proto)
                    break

            if matchExpr is not None:
                self.debug("dump_function(): return_type='%(x)s'", x=matchExpr[0])
                self.ctx.return_type = matchExpr[0]
                self.debug("dump_function(): decl_name='%(x)s'", x=matchExpr[1])
                self.ctx.decl_name   = matchExpr[1]
                self.create_parameterlist(matchExpr[2], ",")
            else:
                self.warn("can't understand function proto: '%(prototype)s'"
                          , prototype = self.ctx.prototype
                          , line_no = self.ctx.decl_offset)
                return

            if self.ctx.last_identifier != self.ctx.decl_name:
                self.warn("function name from comment differs:  %s <--> %s"
                          % (self.ctx.last_identifier, self.ctx.decl_name)
                          , line_no = self.ctx.decl_offset)

        self.check_sections(self.ctx.decl_name
                            , self.ctx.decl_type
                            , self.ctx.sectcheck
                            , self.ctx.parameterlist
                            )
        if hasRetVal:
            self.check_return_section(self.ctx.decl_name, self.ctx.return_type)

        self.output_decl(
            self.ctx.decl_name, "function_decl"
            , function         = self.ctx.decl_name
            , return_type      = self.ctx.return_type
            , parameterlist    = self.ctx.parameterlist
            , parameterdescs   = self.ctx.parameterdescs
            , parametertypes   = self.ctx.parametertypes
            , sections         = self.ctx.sections
            , purpose          = self.ctx.decl_purpose )

    def dump_DOC(self, name, cont):
        self.dump_section(name, cont)
        self.output_decl(name, "DOC"
                         , sections = self.ctx.sections )

    def dump_union(self, proto):

        if not self.prepare_struct_union(proto):
            self.error("can't parse union!")
            return

        if self.ctx.last_identifier != self.ctx.decl_name:
            self.warn("struct name from comment differs:  %s <--> %s"
                      % (self.ctx.last_identifier, self.ctx.decl_name)
                      , line_no = self.ctx.decl_offset)

        self.output_decl(
            self.ctx.decl_name, "union_decl"
            , decl_name        = self.ctx.decl_name
            , decl_type        = self.ctx.decl_type
            , parameterlist    = self.ctx.parameterlist
            , parameterdescs   = self.ctx.parameterdescs
            , parametertypes   = self.ctx.parametertypes
            , sections         = self.ctx.sections
            , purpose          = self.ctx.decl_purpose
            , definition       = self.ctx.definition )

    def dump_struct(self, proto):

        if not self.prepare_struct_union(proto):
            self.error("can't parse struct!")
            return

        if self.ctx.last_identifier != self.ctx.decl_name:
            self.warn("struct name from comment differs:  %s <--> %s"
                      % (self.ctx.last_identifier, self.ctx.decl_name)
                      , line_no = self.ctx.decl_offset)

        self.output_decl(
            self.ctx.decl_name, "struct_decl"
            , decl_name        = self.ctx.decl_name
            , decl_type        = self.ctx.decl_type
            , parameterlist    = self.ctx.parameterlist
            , parameterdescs   = self.ctx.parameterdescs
            , parametertypes   = self.ctx.parametertypes
            , sections         = self.ctx.sections
            , purpose          = self.ctx.decl_purpose
            , definition       = self.ctx.definition)

    def prepare_struct_union(self, proto):
        self.debug("prepare_struct_union(): '%(proto)s'", proto=proto)

        retVal  = False
        members = ""

        # ignore members marked private:
        proto = re.sub(r"/\*\s*private:.*?\/\*\s*public:.*?\*\/", "", proto, flags=re.I)
        proto = re.sub(r"/\*\s*private:.*$", "};", proto, flags=re.I)

        if C_STRUCT_UNION.match(proto):

            if C_STRUCT_UNION[0] != self.ctx.decl_type:
                self.error("determine of decl_type is inconsistent: '%s' <--> '%s'"
                           "\nprototype: %s"
                           % (C_STRUCT_UNION[0], self.ctx.decl_type, proto))
                return False

            self.ctx.decl_name = C_STRUCT_UNION[1]
            self.ctx.definition = members = C89_comments.sub("", C_STRUCT_UNION[2])

            # strip kmemcheck_bitfield_{begin,end}.*;
            members =  re.sub(r"kmemcheck_bitfield_.*?;", "", members)

            # strip attributes
            members = re.sub(r"__attribute__\s*\(\([a-z,_\*\s\(\)]*\)\)", "", members, flags=re.I)
            members = re.sub(r"__aligned\s*\([^;]*\)", "", members)
            members = re.sub(r"\s*CRYPTO_MINALIGN_ATTR", "", members)

            # replace DECLARE_BITMAP
            members = re.sub(r"DECLARE_BITMAP\s*\(([^,)]+),\s*([^,)]+)\)"
                             , r"unsigned long \1[BITS_TO_LONGS(\2)]"
                             , members )

            # replace DECLARE_HASHTABLE
            members = re.sub(r"DECLARE_HASHTABLE\s*\(([^,)]+),\s*([^,)]+)\)"
                             , r"unsigned long \1[1 << ((\2) - 1)]"
                             , members )

            # replace DECLARE_KFIFO
            members = re.sub(r"DECLARE_KFIFO\s*\(([^,)]+),\s*([^,)]+),\s*([^,)]+)\)"
                             , r"\2 \1"
                             , members )

            # replace DECLARE_KFIFO_PTR
            members = re.sub(r"DECLARE_KFIFO_PTR\s*\(([^,)]+),\s*([^,)]+)\)"
                             , r"\2 \1"
                             , members )

            # Split nested struct/union elements as newer ones
            NESTED = RE(r"(struct|union)([^{};]+){([^{}]*)}([^{}\;]*)\;")
            while NESTED.search(members):
                n_content = NESTED[2].strip()
                n_type = NESTED[0].strip()
                n_ids = NESTED[3].strip()
                n_new = ''
                # union car {int foo;} bar1, bar2, *bbar3;
                for n_id in n_ids.split(','):
                    n_id = re.sub(r"[:\[].*", "", n_id).strip()
                    n_id = n_id.strip().replace('*','')
                    n_new += "%s %s;" % (NESTED[0].strip(), n_id)
                    for arg in n_content.split(';'):
                        arg = normalize_ws(arg)
                        if not arg:
                            continue
                        # Handle arrays
                        arg = re.sub(r"\[\s*\S.*\]", "", arg)

                        PTR_TO_FUNC = RE(r"^([^\(]+\(\*?\s*)([\w\.]*)(\s*\).*)")
                        if PTR_TO_FUNC.search(arg):
                            n_type = PTR_TO_FUNC[0].strip()
                            n_name = PTR_TO_FUNC[1].strip()
                            n_extra = PTR_TO_FUNC[2].strip()
                            if not n_name:
                                continue
                            if not n_id:
                                n_new += "%s%s%s; " % (n_type, n_name, n_extra)
                            else:
                                n_new += "%s%s.%s%s; " % (n_type, n_id, n_name, n_extra)

                        else:
                            # suppport bit types e.g. '__u8 arg1 : 1' --> '__u8 arg1'
                            arg = re.sub(r"\s*:\s*[0-9]+", "", arg)
                            n_type = arg.split(" ")[0]
                            n_name = arg.split(" ")[-1].replace('*','')
                            if n_name == n_type:
                                # anonymous struct/union
                                n_new += "%s;" % (n_type)
                            elif not n_id:
                                n_new += "%s %s;" % (n_type, n_name)
                            else:
                                n_new += "%s %s.%s;" % (n_type, n_id, n_name)
                members = NESTED.sub(n_new, members, count=1)

            # ignore other nested elements, like enums
            members = re.sub(r"({[^\{\}]*})", '', members)
            self.create_parameterlist(members, ';')
            self.check_sections(self.ctx.decl_name
                                , self.ctx.decl_type
                                , self.ctx.sectcheck
                                , self.ctx.parameterlist # self.ctx.struct_actual.split(" ")
                                )
            retVal = True

        else:
            retVal = False

        return retVal

    def dump_enum(self, proto):
        self.debug("dump_enum(): '%(proto)s'", proto=proto)

        proto = C89_comments.sub("", proto)
        # strip #define macros inside enums
        proto = re.sub(r"#\s*((define|ifdef)\s+|endif)[^;]*;", "", proto)

        splitchar = ","
        RE_NAME = RE(r"^\s*(\w+).*")

        if C_ENUM.search(proto):
            self.ctx.decl_name = C_ENUM[0]
            members = normalize_ws(C_ENUM[1])

            # drop trailing splitchar, if extists
            if members.endswith(splitchar):
                members = members[:-1]

            for member in members.split(splitchar):
                name = RE_NAME.sub(r"\1", member)
                self.ctx.parameterlist.append(name)
                if not self.ctx.parameterdescs.get(name, None):
                    self.warn(
                        "Enum value '%(name)s' not described"
                        " in enum '%(decl_name)s'"
                        , name = name,  decl_name=self.ctx.decl_name )
                    self.ctx.parameterdescs[name] = Parser.undescribed

            if self.ctx.last_identifier != self.ctx.decl_name:
                self.warn("enum name from comment differs:  %s <--> %s"
                          % (self.ctx.last_identifier, self.ctx.decl_name)
                          , line_no = self.ctx.decl_offset)

            self.check_sections(self.ctx.decl_name
                                , self.ctx.decl_type
                                , self.ctx.sectcheck
                                , self.ctx.parameterlist )

            self.output_decl(
                self.ctx.decl_name, "enum_decl"
                , enum             = self.ctx.decl_name
                , parameterlist    = self.ctx.parameterlist
                , parameterdescs   = self.ctx.parameterdescs
                , sections         = self.ctx.sections
                , purpose          = self.ctx.decl_purpose )

        else:
            self.error("can't parse enum!")

    def dump_typedef(self, proto):
        self.debug("dump_typedef(): '%(proto)s'", proto=proto)

        proto = C89_comments.sub("", proto)

        matchExpr = None
        if C_FUNC_TYPEDEF.search(proto):
            matchExpr = C_FUNC_TYPEDEF
        elif C_FUNC_TYPEDEF_2.search(proto):
            self.warn("typedef of function pointer used uncommon code style: '%s'" % proto)
            matchExpr = C_FUNC_TYPEDEF_2

        if matchExpr:
            # Parse function prototypes

            self.ctx.return_type = matchExpr[0].lstrip()
            self.ctx.decl_name   = matchExpr[1]
            self.check_return_section(self.ctx.decl_name, self.ctx.return_type)

            f_args = matchExpr[2]
            self.create_parameterlist(f_args, ',')

            if self.ctx.last_identifier != self.ctx.decl_name:
                self.warn("function name from comment differs:  %s <--> %s"
                          % (self.ctx.last_identifier, self.ctx.decl_name)
                          , line_no = self.ctx.decl_offset)

            self.check_sections(self.ctx.decl_name
                                , self.ctx.decl_type
                                , self.ctx.sectcheck
                                , self.ctx.parameterlist )
            self.output_decl(
                self.ctx.decl_name, "function_decl"
                , function         = self.ctx.decl_name
                , return_type      = self.ctx.return_type
                , parameterlist    = self.ctx.parameterlist
                , parameterdescs   = self.ctx.parameterdescs
                , parametertypes   = self.ctx.parametertypes
                , sections         = self.ctx.sections
                , purpose          = self.ctx.decl_purpose )

        else:
            self.debug("dump_typedef(): '%(proto)s'", proto=proto)
            x1 = RE(r"\(*.\)\s*;$")
            x2 = RE(r"\[*.\]\s*;$")

            while x1.search(proto) or x2.search(proto):
                proto = x1.sub(";", proto)
                proto = x2.sub(";", proto)

            self.debug("dump_typedef(): '%(proto)s'", proto=proto)

            if C_TYPEDEF.match(proto):
                self.ctx.decl_name = C_TYPEDEF[0]
                if self.ctx.last_identifier != self.ctx.decl_name:
                    self.warn("typedef name from comment differs:  %s <--> %s"
                              % (self.ctx.last_identifier, self.ctx.decl_name)
                              , line_no = self.ctx.decl_offset)

                self.check_sections(self.ctx.decl_name
                                    , self.ctx.decl_type
                                    , self.ctx.sectcheck
                                    , self.ctx.parameterlist )
                self.output_decl(
                    self.ctx.decl_name, "typedef_decl"
                    , typedef   = self.ctx.decl_name
                    , sections  = self.ctx.sections
                    , purpose   = self.ctx.decl_purpose )
            else:
                self.error("can't parse typedef!")

    def create_parameterlist(self, parameter, splitchar):
        self.debug("create_parameterlist(): splitchar='%(x)s' params='%(y)s'"
                   , x=splitchar, y=parameter)
        parameter = normalize_ws(parameter)
        pointer_to_func = RE(r"\(.+\)\s*\(")

        # temporarily replace commas inside function pointer definition
        m = RE(r"(\([^\),]+),")

        while m.search(parameter):
            parameter = m.sub(r"\1#", parameter)
        # drop trailing splitchar, if extists
        if parameter.endswith(splitchar):
            parameter = parameter[:-1]

        self.debug("create_parameterlist(): params='%(y)s'", y=parameter)
        for c, p in enumerate(parameter.split(splitchar)):
            p = C99_comments.sub("", p)
            p = p.strip()

            self.debug("  parameter#%(c)s: %(p)s", c=c, p=p)
            p_type = None
            p_name = None

            if MACRO.match(p):

                # Treat preprocessor directive as a typeless variable just to
                # fill corresponding data structures "correctly". Catch it later
                # in output_* subs.
                self.debug("  parameter#%(c)s: (MACRO) %(p)s=''" , c=c, p=p)
                self.push_parameter(p, "")

            elif pointer_to_func.search(p):

                # pointer-to-function
                p = p.replace("#", ",") # reinsert temporarily removed commas
                self.debug("  parameter#%(c)s: (pointer to function) %(p)s", c=c, p=p)
                m = RE(r"[^\(]+\(\*?\s*([\w\.]*)\s*\)")
                m.match(p)
                p_name = m[0]
                p_type  = p
                p_type = re.sub(r"([^\(]+\(\*?)\s*"+p_name, r"\1", p_type)
                #self.save_struct_actual(p_name)
                self.push_parameter(p_name, p_type)

            else:
                p = re.sub(r"\s*:\s*", ":", p)
                p = re.sub(r"\s*\["  , "[", p)
                self.debug("  parameter#%(c)s: (common) %(p)s", c=c, p=p)

                p_args = re.split(r"\s*,\s*", p)
                if re.match(r"\s*,\s*", p_args[0]):
                    p_args[0] = re.sub(r"(\*+)\s*", r" \1", p_args[0])

                self.debug("  parameter#%(c)s : (1) p_args = %(p_args)s"
                           , c=c, p_args=repr(p_args))

                first_arg = []
                m = RE(r"^(.*\s+)(.*?\[.*\].*)$")
                if m.match(p_args[0]):
                    p_args.pop(0)
                    first_arg.extend(re.split(r"\s+", m[0]))
                    first_arg.append(m[1])
                else:
                    first_arg.extend(re.split(r"\s+", p_args.pop(0)))

                p_args = [first_arg.pop() ] + p_args
                self.debug("  parameter#%(c)s : (2) p_args=%(p_args)s"
                           , c=c, p_args=repr(p_args))
                p_type = " ".join(first_arg)

                ma = RE(r"^(\*+)\s*(.*)")
                mb = RE(r"(.*?):(\d+)")

                for p_name in p_args:
                    self.debug("  parameter#%(c)s : (3) p_name='%(p_name)s'"
                               , c=c, p_name=p_name)

                    if ma.match(p_name):
                        p_type = "%s %s" % (p_type, ma[0])
                        p_name = ma[1]

                    elif mb.match(p_name):
                        if p_type:
                            p_name = mb[0]
                            p_type = "%s:%s" % (p_type, mb[1])
                        else:
                            # skip unnamed bit-fields
                            continue

                    self.debug("  parameter#%(c)s : (4) p_name='%(p_name)s' / p_type='%(p_type)s'"
                               , c=c, p_name=p_name, p_type=p_type)
                    #self.save_struct_actual(p_name)
                    self.push_parameter(p_name, p_type)

    def push_parameter(self, p_name, p_type):
        self.debug(
            "push_parameter(): p_name='%(p_name)s' / p_type='%(p_type)s'"
            , p_name=p_name, p_type=p_type)
        p_name  = p_name.strip()
        p_type  = p_type.strip()

        if ( self.anon_struct_union
             and not p_type
             and p_name == "}" ):
            # ignore the ending }; from anon. struct/union
            return

        self.anon_struct_union = False

        self.debug(
            "push_parameter(): (1) p_name='%(p_name)s' / p_type='%(p_type)s'"
            , p_name=p_name, p_type=p_type)

        if not p_type and re.search(r"\.\.\.$", p_name):
            if not self.ctx.parameterdescs.get(p_name, None):
                self.ctx.parameterdescs[p_name] = "variable arguments"

        elif not p_type and (not p_name or p_name == "void"):
            p_name = "void"
            self.ctx.parameterdescs[p_name] = "no arguments"

        elif not p_type and (p_name in ("struct", "union")):
            # handle unnamed (anonymous) union or struct:
            p_type  = p_name
            p_name = "{unnamed_" + p_name + "}"
            self.ctx.parameterdescs[p_name] = "anonymous"
            self.anon_struct_union = True

        self.debug(
            "push_parameter(): (2) p_name='%(p_name)s' / p_type='%(p_type)s'"
            , p_name=p_name, p_type=p_type)

        if not p_name.startswith("#"):
            # strip array from paramater name / e.g. p_name is "modes[]" from a
            # parmeter defined by: "const char * const modes[]"

            p_name = re.sub(r"\[.*", "", p_name)

            # strip parentheses and pointers, e.g.: (*foo) --> foo

            p_name = re.sub(r"[\*\(\)]", "", p_name)

        self.debug(
            "push_parameter(): (3) p_name='%(p_name)s' / p_type='%(p_type)s'"
            , p_name=p_name, p_type=p_type)

        # warn if parameter has no description (but ignore ones starting with
        # '#' as these are not parameters but inline preprocessor statements);
        # also ignore unnamed structs/unions;

        if not self.anon_struct_union:
            if ( not self.ctx.parameterdescs.get(p_name, None)
                 and not p_name.startswith("#") ):
                if p_type in ("function", "enum"):
                    self.warn("Function parameter or member '%(p_name)s' not "
                              "described in '%(decl_name)s'."
                              , p_name = p_name
                              , decl_name = self.ctx.decl_name
                              , line_no = self.ctx.last_offset)
                else:
                    self.warn("no description found for parameter '%(p_name)s'"
                              , p_name = p_name, line_no = self.ctx.decl_offset)
                self.ctx.parameterdescs[p_name] = Parser.undescribed

        self.ctx.parameterlist.append(p_name)
        self.ctx.parametertypes[p_name] = p_type.strip()

    # def save_struct_actual(self, actual):
    #     # strip all spaces from the actual param so that it looks like one
    #     # string item
    #     self.debug("save_struct_actual(): actual='%(a)s'", a=actual)
    #     actual = WHITESPACE.sub("", actual)
    #     self.ctx.struct_actual += actual + " "
    #     self.debug("save_struct_actual: '%(a)s'", a=self.ctx.struct_actual)


    def check_sections(self, decl_name, decl_type
                       , sectcheck, parameterlist):
        self.debug("check_sections(): decl_name='%(n)s' / decl_type='%(t)s' /"
                   " sectcheck=%(sc)s / parameterlist=%(pl)s"
                   , n=decl_name, t=decl_type, sc=sectcheck, pl=parameterlist)

        for sect in sectcheck:
            err = True
            for para in parameterlist:
                para = re.sub(r"\[.*\]", "", para)
                #para = re.sub(r"/__attribute__\s*\(\([A-Za-z,_\*\s\(\)]*\)\)/", "", para)
                if para == sect:
                    err = False
                    break
            if err:
                if decl_type == "function":
                    self.warn(
                        "excess function parameter '%(sect)s' description in '%(decl_name)s'"
                        , sect = sect, decl_name = decl_name
                        , line_no = self.ctx.decl_offset )
                else:
                    self.warn(
                        "excess %(decl_type)s member '%(sect)s' description in '%(decl_name)s'"
                        , decl_type = decl_type, decl_name = decl_name, sect = sect
                        , line_no = self.ctx.decl_offset )
            else:
                self.debug("check_sections(): parameter '%(sect)s': description exists / OK"
                           , sect=sect)

    def check_return_section(self, decl_name, return_type):
        self.debug("check_return_section(): decl_name='%(n)s', return_type='%(t)s"
                   , n=decl_name, t=return_type)
        # Ignore an empty return type (It's a macro) and ignore functions with a
        # "void" return type. (But don't ignore "void *")

        if ( not return_type
             or re.match(r"void\s*\w*\s*$", return_type) ):
            self.debug("check_return_section(): ignore void")
            return

        if self.options.verbose_warn and not self.ctx.sections.get(self.section_return, None):
            self.warn("no description found for return-value of function '%(func)s()'"
                      , func = decl_name, line_no = self.ctx.decl_offset)
        else:
            self.debug("check_return_section(): return-value of %(func)s() OK"
                       , func = decl_name)

# ==============================================================================
# run ...
# ==============================================================================

if __name__ == "__main__":
    sys.exit(main())
