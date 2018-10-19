# -*- coding: utf-8 -*-
#
# Sphinx documentation build configuration file

import linuxdoc
import sphinx_rtd_theme

master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = ['_build']

project   = 'LinuxDoc'
copyright = linuxdoc.__copyright__
version   = linuxdoc.__version__
release   = linuxdoc.__version__
author    = 'return42'
show_authors = True

extensions = [
    'linuxdoc.rstFlatTable'      # Implementation of the 'flat-table' reST-directive.
    , 'linuxdoc.rstKernelDoc'    # Implementation of the 'kernel-doc' reST-directive.
    , 'linuxdoc.kernel_include'  # Implementation of the 'kernel-include' reST-directive.
    , 'linuxdoc.manKernelDoc'    # Implementation of the 'kernel-doc-man' builder
    , 'linuxdoc.cdomain'         # Replacement for the sphinx c-domain.
    , 'linuxdoc.kfigure'         # Sphinx extension which implements scalable image handling.
    , 'sphinx.ext.autodoc'
    , 'sphinx.ext.extlinks'
    , 'sphinx.ext.todo'
    , 'sphinx.ext.coverage'
    , 'sphinx.ext.viewcode'
    , 'sphinx.ext.intersphinx'
]

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ["../utils/sphinx-static"]
html_context = {
    'css_files': [
        '_static/theme_overrides.css',
    ],
}
html_logo = 'darmarIT_logo_128.png'

# since https://h2626237.stratoserver.net/ is self-signed, disable tls verify
tls_verify = False
intersphinx_mapping = {}
intersphinx_mapping['template-book'] = ('https://h2626237.stratoserver.net/kernel/books/template-book/', None)
intersphinx_mapping['process'] = ('https://h2626237.stratoserver.net/kernel/books/process/', None)
#intersphinx_mapping['linux'] = ('https://h2626237.stratoserver.net/kernel/linux_src_doc/', None)

extlinks = {}
# usage:    :mid:`<mail's Message-ID>`  e.g.
extlinks['mid'] = ('http://mid.mail-archive.com/%s', '')
extlinks['lwn'] = ('https://lwn.net/Articles/%s', 'LWN article #')
extlinks['rst-directive'] = ('http://docutils.sourceforge.net/docs/ref/rst/directives.html#%s', '')

# ------------------------------------------------------------------------------
# Options of the kernel-doc parser
# ------------------------------------------------------------------------------

# If true, fatal errors (like missing function descripions) raise an error. If
# false, insert Oops messages for fatal errors.  Default: True
kernel_doc_raise_error = False

# Oops messages are Sphinx ``.. todo::`` directives. To inster the Oops messages
# from the kernel-doc parser we have to active todo_include_todos also.
todo_include_todos = True

# If true, more warnings will be logged. E.g. a missing description of a
# function's return value will be logged.
# Default: True
kernel_doc_verbose_warn = False

# Set parser's default kernel-doc mode ``reST|kernel-doc``.
# Default: "reST"
kernel_doc_mode = "reST"

# Global fallback for man section of kernel-doc directives. Set this value if
# you want to create man pages for those kernel-doc directives, which has not
# been set a ``:man-sect:`` value.
# Default: None
kernel_doc_mansect = None

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [ ]

# In nickpick mode, it will complain about lots of missing references that
#
# 1) are just typedefs like: bool, __u32, etc;
# 2) It will complain for things like: enum, NULL;
# 3) It will complain for symbols that should be on different
#    books (but currently aren't ported to ReST)
#
# The list below has a list of such symbols to be ignored in nitpick mode
#
nitpick_ignore = [
    ("c:type", "bool"),
    ("c:type", "enum"),
    ("c:type", "u16"),
    ("c:type", "u32"),
    ("c:type", "u64"),
    ("c:type", "u8"),
    ]

