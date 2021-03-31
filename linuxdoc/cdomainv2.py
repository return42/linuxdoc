# -*- coding: utf-8; mode: python -*-
# SPDX-License-Identifier: GPL-2.0
"""\
cdomainv2 (Sphinx v<3.0)
~~~~~~~~~~~~~~~~~~~~~~~~

Replacement for the sphinx c-domain.  For user documentation see
:ref:`customized-c-domain`.

"""

from docutils import nodes
from docutils.parsers.rst import directives
import sphinx

from sphinx import addnodes
from sphinx.locale import _
# pylint: disable=no-name-in-module
from sphinx.domains.c import c_funcptr_sig_re, c_sig_re
from sphinx.domains.c import CObject as Base_CObject
from sphinx.domains.c import CDomain as Base_CDomain
# pylint: enable=no-name-in-module

# Get Sphinx version
major, minor, patch = sphinx.version_info[:3]  # pylint: disable=invalid-name

class CObject(Base_CObject):  # pylint: disable=abstract-method

    """
    Description of a C language object.
    """
    option_spec = {
        "name" : directives.unchanged
    }

    is_function_like_macro = False

    def handle_func_like_macro(self, sig, signode):
        u"""Handles signatures of function-like macros.

        If the objtype is 'function' and the the signature ``sig`` is a
        function-like macro, the name of the macro is returned. Otherwise
        ``False`` is returned.  """

        if not self.objtype == 'function':
            return False

        m = c_funcptr_sig_re.match(sig)  # pylint: disable=invalid-name
        if m is None:
            m = c_sig_re.match(sig)      # pylint: disable=invalid-name
            if m is None:
                raise ValueError('no match')

        rettype, fullname, arglist, _const = m.groups()
        arglist = arglist.strip()
        if rettype or not arglist:
            return False

        arglist = arglist.replace('`', '').replace('\\ ', '') # remove markup
        arglist = [a.strip() for a in arglist.split(",")]

        # has the first argument a type?
        if len(arglist[0].split(" ")) > 1:
            return False

        # This is a function-like macro, it's arguments are typeless!
        signode  += addnodes.desc_name(fullname, fullname)
        paramlist = addnodes.desc_parameterlist()
        signode  += paramlist

        for argname in arglist:
            param = addnodes.desc_parameter('', '', noemph=True)
            # separate by non-breaking space in the output
            param += nodes.emphasis(argname, argname)
            paramlist += param

        self.is_function_like_macro = True
        return fullname

    def handle_signature(self, sig, signode):
        """Transform a C signature into RST nodes."""

        fullname = self.handle_func_like_macro(sig, signode)
        if not fullname:
            fullname = super().handle_signature(sig, signode)

        if "name" in self.options:
            if self.objtype == 'function':
                fullname = self.options["name"]
            else:
                # FIXME: handle :name: value of other declaration types?
                pass
        return fullname

    def add_target_and_index(self, name, sig, signode):  # pylint: disable=arguments-differ
        # for C API items we add a prefix since names are usually not qualified
        # by a module name and so easily clash with e.g. section titles
        targetname = 'c.' + name
        if targetname not in self.state.document.ids:
            signode['names'].append(targetname)
            signode['ids'].append(targetname)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            inv = self.env.domaindata['c']['objects']
            if (name in inv and self.env.config.nitpicky):
                if self.objtype == 'function':
                    if ('c:func', name) not in self.env.config.nitpick_ignore:
                        self.state_machine.reporter.warning(
                            'duplicate C object description of %s, ' % name +
                            'other instance in ' + self.env.doc2path(inv[name][0]),
                            line=self.lineno)
            inv[name] = (self.env.docname, self.objtype)

        indextext = self.get_index_text(name)
        if indextext:
            if major == 1 and minor < 4:
                # indexnode's tuple changed in 1.4
                # https://github.com/sphinx-doc/sphinx/commit/e6a5a3a92e938fcd75866b4227db9e0524d58f7c
                self.indexnode['entries'].append(
                    ('single', indextext, targetname, ''))
            else:
                self.indexnode['entries'].append(
                    ('single', indextext, targetname, '', None))

    def get_index_text(self, name):
        if self.is_function_like_macro:  # pylint: disable=no-else-return
            return _('%s (C macro)') % name
        else:
            return super().get_index_text(name)

class CDomain(Base_CDomain):

    """C language domain.

    """
    name = 'c'
    label = 'C'
    directives = {
        'function': CObject,
        'member':   CObject,
        'macro':    CObject,
        'type':     CObject,
        'var':      CObject,
    }
    "Use :py:class:`CObject <linuxdoc.cdomain.CObject>` directives."
