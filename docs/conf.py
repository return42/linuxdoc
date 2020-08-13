# -*- coding: utf-8 -*-
#
# Sphinx documentation build configuration file

import re
import linuxdoc
import sys, os

from pallets_sphinx_themes import ProjectLink

sys.path.append(os.path.abspath('../utils/site-python'))
from sphinx_build_tools import load_sphinx_config

DOC_URL    = "https://return42.github.io/linuxdoc"
GIT_URL    = "https://github.com/return42/linuxdoc"
GIT_BRANCH = 'master'

project   = 'LinuxDoc'
copyright = linuxdoc.__copyright__
version   = linuxdoc.__version__
release   = linuxdoc.__version__
author    = 'return42'
show_authors = True

source_suffix       = '.rst'
show_authors        = True
master_doc          = 'index'
templates_path      = ['_templates']
exclude_patterns    = ['_build', 'slides']
todo_include_todos  = True
highlight_language = 'none'

# if self-signed, disable tls verify
# tls_verify = False

extensions = [
    'sphinx.ext.imgmath'
    , 'sphinx.ext.autodoc'
    , 'sphinx.ext.extlinks'
    #, 'sphinx.ext.autosummary'
    #, 'sphinx.ext.doctest'
    , 'sphinx.ext.todo'
    , 'sphinx.ext.coverage'
    #, 'sphinx.ext.pngmath'
    #, 'sphinx.ext.mathjax'
    , 'sphinx.ext.viewcode'
    , 'sphinx.ext.intersphinx'
    , 'sphinxcontrib.programoutput'  # https://github.com/NextThought/sphinxcontrib-programoutput
    , 'sphinx_tabs.tabs'             # https://github.com/djungelorm/sphinx-tabs
    , 'pallets_sphinx_themes'

    , 'linuxdoc.rstFlatTable'    # Implementation of the 'flat-table' reST-directive.
    , 'linuxdoc.rstKernelDoc'    # Implementation of the 'kernel-doc' reST-directive.
    , 'linuxdoc.kernel_include'  # Implementation of the 'kernel-include' reST-directive.
    , 'linuxdoc.manKernelDoc'    # Implementation of the 'kernel-doc-man' builder
    , 'linuxdoc.cdomain'         # Replacement for the sphinx c-domain (not in sphinx-doc >= v3.0)
    , 'linuxdoc.kfigure'         # Sphinx extension which implements scalable image handling.
]

intersphinx_mapping = {}
#intersphinx_mapping['template-book'] = (
#    'https://h2626237.stratoserver.net/kernel/books/template-book/', None)
#intersphinx_mapping['process'] = (
#    'https://h2626237.stratoserver.net/kernel/books/process/', None)
#intersphinx_mapping['linux'] = (
#    'https://h2626237.stratoserver.net/kernel/linux_src_doc/', None)

extlinks = {}
extlinks['origin'] = (GIT_URL + '/blob/' + GIT_BRANCH + '/%s', 'git://')
extlinks['commit'] = (GIT_URL + '/commit/%s', '#')

# usage:    :mid:`<mail's Message-ID>`  e.g.
extlinks['mid'] = ('http://mid.mail-archive.com/%s', '')
extlinks['lwn'] = ('https://lwn.net/Articles/%s', 'LWN article #')
extlinks['rst-directive'] = ('http://docutils.sourceforge.net/docs/ref/rst/directives.html#%s', '')

# sphinx.ext.imgmath setup
html_math_renderer = 'imgmath'
imgmath_image_format = 'svg'
imgmath_font_size = 14
# sphinx.ext.imgmath setup END

html_search_language = 'en'

sys.path.append(os.path.abspath('_themes'))
html_theme           = "custom"
html_logo            = 'darmarIT_logo_128.png'
html_theme_path      = ['_themes']
# html_static_path     = ["static"]

html_theme_options = {"index_sidebar_logo": True}
html_context = {
    "project_links": [
        ProjectLink("Home", DOC_URL),
        ProjectLink("Source", GIT_URL),
        ProjectLink("API", DOC_URL + '/linuxdoc-api/linuxdoc.html'),
    ]
}
html_sidebars = {
    "**": ["project.html", "relations.html", "localtoc.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}

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

# ------------------------------------------------------------------------------
# Since loadConfig overwrites settings from the global namespace, it has to be
# the last statement in the conf.py file
# ------------------------------------------------------------------------------
load_sphinx_config(globals())
