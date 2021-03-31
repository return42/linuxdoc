#!/usr/bin/env python3
# -*- coding: utf-8; mode: python -*-
# SPDX-License-Identifier: GPL-2.0
# pylint: disable=missing-docstring, invalid-name, unnecessary-pass
"""\
kernel-doc-man
~~~~~~~~~~~~~~

Implementation of the ``kernel-doc-man`` builder.

User documentation see :ref:`man-pages`.
"""

# ==============================================================================
# imports
# ==============================================================================

import re
import collections
from os import path

from docutils.io import FileOutput
from docutils.frontend import OptionParser
from docutils import nodes
from docutils.utils import new_document
from docutils.parsers.rst import Directive
from docutils.transforms import Transform

from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.nodes import inline_all_toctrees
from sphinx.util.console import bold, darkgreen  # pylint: disable=no-name-in-module
from sphinx.writers.manpage import ManualPageWriter

from sphinx.builders.manpage import ManualPageBuilder

from .kernel_doc import Container

logger = logging.getLogger(__name__)

# ==============================================================================
# common globals
# ==============================================================================

DEFAULT_MAN_SECT  = 9

# The version numbering follows numbering of the specification
# (Documentation/books/kernel-doc-HOWTO).
__version__  = '1.0'

# ==============================================================================
def setup(app):
# ==============================================================================

    app.add_builder(KernelDocManBuilder)
    app.add_directive("kernel-doc-man", KernelDocMan)
    app.add_node(kernel_doc_man
                 , html    = (skip_kernel_doc_man, None)
                 , latex   = (skip_kernel_doc_man, None)
                 , texinfo = (skip_kernel_doc_man, None)
                 , text    = (skip_kernel_doc_man, None)
                 , man     = (skip_kernel_doc_man, None) )

    return dict(
        version = __version__
        , parallel_read_safe = True
        , parallel_write_safe = True
    )

# ==============================================================================
class kernel_doc_man(  # pylint: disable=invalid-name
        nodes.Invisible, nodes.Element):
# ==============================================================================
    """Node to mark a section as *manpage*"""

def skip_kernel_doc_man(self, node):  # pylint: disable=unused-argument
    raise nodes.SkipNode


# ==============================================================================
class KernelDocMan(Directive):
# ==============================================================================

    required_arguments = 1
    optional_arguments = 0

    def run(self):
        man_node = kernel_doc_man()
        man_node["manpage"] = self.arguments[0]
        return [man_node]

# ==============================================================================
class Section2Manpage(Transform):
# ==============================================================================
    u"""Transforms a *section* tree into an *manpage* tree.

    The structural layout of a man-page differs from the one produced, by the
    kernel-doc parser.  The kernel-doc parser produce reST which fits to *normal*
    documentation, e.g. the declaration of a function in reST is like.

    .. code-block:: rst

        user_function
        =============

        .. c:function:: int user_function(int a)

           The *purpose* description.

           :param int a:
               Parameter a description

       Description
       ===========

       lorem ipsum ..

       Return
       ======

       Returns first argument

    On the other side, in man-pages it is common (see ``man man-pages``) to
    print the *purpose* line in the "NAME" section, function's prototype in the
    "SYNOPSIS" section and the parameter description in the "OPTIONS" section::

       NAME
              user_function -- The *purpose* description.

       SYNOPSIS
               int user_function(int a)

       OPTIONS
               a

       DESCRIPTION
               lorem ipsum

       RETURN VALUE
               Returns first argument

    """
    # The common section order is:
    manTitles = [
        (re.compile(r"^SYNOPSIS|^DEFINITION"
                    , flags=re.I), "SYNOPSIS")
        , (re.compile(r"^CONFIG",     flags=re.I), "CONFIGURATION")
        , (re.compile(r"^DESCR",      flags=re.I), "DESCRIPTION")
        , (re.compile(r"^OPTION",     flags=re.I), "OPTIONS")
        , (re.compile(r"^EXIT",       flags=re.I), "EXIT STATUS")
        , (re.compile(r"^RETURN",     flags=re.I), "RETURN VALUE")
        , (re.compile(r"^ERROR",      flags=re.I), "ERRORS")
        , (re.compile(r"^ENVIRON",    flags=re.I), "ENVIRONMENT")
        , (re.compile(r"^FILE",       flags=re.I), "FILES")
        , (re.compile(r"^VER",        flags=re.I), "VERSIONS")
        , (re.compile(r"^ATTR",       flags=re.I), "ATTRIBUTES")
        , (re.compile(r"^CONFOR",     flags=re.I), "CONFORMING TO")
        , (re.compile(r"^NOTE",       flags=re.I), "NOTES")
        , (re.compile(r"^BUG",        flags=re.I), "BUGS")
        , (re.compile(r"^EXAMPLE",    flags=re.I), "EXAMPLE")
        , (re.compile(r"^SEE",        flags=re.I), "SEE ALSO")
        , ]

    manTitleOrder = [t for r,t in manTitles]

    @classmethod
    def sec2man_get_first_child(cls, subtree, *classes):
        for _c in classes:
            if subtree is None:
                break
            idx = subtree.first_child_matching_class(_c)
            if idx is None:
                subtree = None
                break
            subtree = subtree[idx]
        return subtree

    def strip_man_info(self):
        section  = self.document[0]
        man_info = Container(authors=[])
        man_node = self.sec2man_get_first_child(section, kernel_doc_man)
        name, sect = (man_node["manpage"].split(".", -1) + [DEFAULT_MAN_SECT])[:2]
        man_info["manpage"] = name
        man_info["mansect"] = sect

        # strip field list
        field_list = self.sec2man_get_first_child(section, nodes.field_list)
        if field_list:
            field_list.parent.remove(field_list)
            for field in field_list:
                name  = field[0].astext().lower()
                value = field[1].astext()
                man_info[name] = man_info.get(name, []) + [value,]

            # normalize authors
            for auth, adr in zip(man_info.get("author", [])
                                 , man_info.get("address", [])):
                man_info["authors"].append("%s <%s>" % (auth, adr))

        # strip *purpose*
        desc_content = self.sec2man_get_first_child(
            section, addnodes.desc, addnodes.desc_content)
        if not desc_content or not len(desc_content): # pylint: disable=len-as-condition
            # missing initial short description in kernel-doc comment
            man_info.subtitle = ""
        else:
            man_info.subtitle = desc_content[0].astext()
            del desc_content[0]

        # remove section title
        old_title = self.sec2man_get_first_child(section, nodes.title)
        old_title.parent.remove(old_title)

        # gather type of the declaration
        decl_type = self.sec2man_get_first_child(
            section, addnodes.desc, addnodes.desc_signature, addnodes.desc_type)
        if decl_type is not None:
            decl_type = decl_type.astext().strip()
        man_info.decl_type = decl_type

        # complete infos
        man_info.title    = man_info["manpage"]
        man_info.section  = man_info["mansect"]

        return man_info

    def isolate_sections(self, sec_by_title):
        section = self.document[0]
        while True:
            sect = self.sec2man_get_first_child(section, nodes.section)
            if not sect:
                break
            sec_parent = sect.parent
            target_idx = sect.parent.index(sect) - 1
            sect.parent.remove(sect)
            if isinstance(sec_parent[target_idx], nodes.target):
                # drop target / is useless in man-pages
                del sec_parent[target_idx]
            title = sect[0].astext().upper()
            for r, man_title in self.manTitles:  # pylint: disable=invalid-name
                if r.search(title):
                    title = man_title
                    sect[0].replace_self(nodes.title(text = title))
                    break
            # we dont know if there are sections with the same title
            sec_by_title[title] = sec_by_title.get(title, []) + [sect]

        return sec_by_title

    def isolate_synopsis(self, sec_by_title):
        synopsis = None
        c_desc = self.sec2man_get_first_child(self.document[0], addnodes.desc)
        if c_desc is not None:
            c_desc.parent.remove(c_desc)
            synopsis = nodes.section()
            synopsis += nodes.title(text = 'synopsis')
            synopsis += c_desc
            sec_by_title["SYNOPSIS"] = sec_by_title.get("SYNOPSIS", []) + [synopsis]
        return sec_by_title

    def apply(self, **kwargs):
        self.document.man_info = self.strip_man_info()
        sec_by_title = collections.OrderedDict()

        self.isolate_sections(sec_by_title)
        # On struct, enum, union, typedef, the SYNOPSIS is taken from the
        # DEFINITION section.
        if self.document.man_info.decl_type not in [
                "struct", "enum", "union", "typedef"]:
            self.isolate_synopsis(sec_by_title)

        for sec_name in self.manTitleOrder:
            sec_list = sec_by_title.pop(sec_name,[])
            self.document[0] += sec_list

        for sec_list in sec_by_title.values():
            self.document[0] += sec_list

# ==============================================================================
class KernelDocManBuilder(ManualPageBuilder):
# ==============================================================================

    """
    Builds groff output in manual page format.
    """
    name = 'kernel-doc-man'
    format = 'man'
    supported_image_types = []

    def init(self):
        pass

    def is_manpage(self, node):  # pylint: disable=no-self-use
        if isinstance(node, nodes.section):
            return bool(
                Section2Manpage.sec2man_get_first_child(
                    node, kernel_doc_man) is not None)
        return False

    def prepare_writing(self, docnames):
        """A place where you can add logic before :meth:`write_doc` is run"""
        pass

    def write_doc(self, docname, doctree):
        """Where you actually write something to the filesystem."""
        pass

    def get_partial_document(self, children):  # pylint: disable=no-self-use
        doc_tree =  new_document('<output>')
        doc_tree += children
        return doc_tree

    def write(self, *ignored):
        if self.config.man_pages:
            # build manpages from config.man_pages as usual
            ManualPageBuilder.write(self, *ignored)

        logger.info(bold("scan master tree for kernel-doc man-pages ... ") + darkgreen("{"), nonl=True)

        master_tree = self.env.get_doctree(self.config.master_doc)
        master_tree = inline_all_toctrees(
            self, set(), self.config.master_doc, master_tree, darkgreen, [self.config.master_doc])
        logger.info(darkgreen("}"))
        man_nodes   = master_tree.traverse(condition=self.is_manpage)
        if not man_nodes and not self.config.man_pages:
            logger.warn('no "man_pages" config value nor manual section found; no manual pages '
                        'will be written')
            return

        logger.info(bold('START writing man pages ... '), nonl=True)

        for man_parent in man_nodes:

            doc_tree = self.get_partial_document(man_parent)
            Section2Manpage(doc_tree).apply()

            if not doc_tree.man_info["authors"] and self.config.author:
                doc_tree.man_info["authors"].append(self.config.author)

            doc_writer   = ManualPageWriter(self)
            doc_settings = OptionParser(
                defaults            = self.env.settings
                , components        = (doc_writer,)
                , read_config_files = True
                , ).get_default_values()

            doc_settings.__dict__.update(doc_tree.man_info)
            doc_tree.settings = doc_settings
            targetname  = '%s.%s' % (doc_tree.man_info.title, doc_tree.man_info.section)
            if doc_tree.man_info.decl_type in [
                    "struct", "enum", "union", "typedef"]:
                targetname = "%s_%s" % (doc_tree.man_info.decl_type, targetname)

            destination = FileOutput(
                destination_path = path.join(self.outdir, targetname)
                , encoding='utf-8')

            logger.info(darkgreen(targetname) + " ", nonl=True)
            self.env.resolve_references(doc_tree, doc_tree.man_info.manpage, self)

            # remove pending_xref nodes
            for pendingnode in doc_tree.traverse(addnodes.pending_xref):
                pendingnode.replace_self(pendingnode.children)
            doc_writer.write(doc_tree, destination)
        logger.info("END writing man pages.")


    def finish(self):
        pass
