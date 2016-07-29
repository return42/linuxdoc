# -*- coding: utf-8 -*-
#
# Sphinx documentation build configuration file

import re
import linuxdoc
import sphinx_rtd_theme

master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = ['_build']

project   = 'LinuxDoc'
copyright = linuxdoc.__copyright__
version   = linuxdoc.__version__
release   = linuxdoc.__version__
show_authors = True

extensions = [
    'sphinx.ext.autodoc'
    , 'sphinx.ext.extlinks'
    #, 'sphinx.ext.autosummary'
    #, 'sphinx.ext.doctest'
    , 'sphinx.ext.todo'
    , 'sphinx.ext.coverage'
    #, 'sphinx.ext.pngmath'
    #, 'sphinx.ext.mathjax'
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


intersphinx_mapping = {}
#intersphinx_mapping['linux'] = ('https://return42.github.io/sphkerneldoc/linux_src_doc/', None)
intersphinx_mapping['kernel-doc'] = ('https://return42.github.io/sphkerneldoc/books/kernel-doc-HOWTO/', None)
#intersphinx_mapping['template-book'] = ('http://return42.github.io/sphkerneldoc/books/template-book/', None)
#intersphinx_mapping['linuxdoc'] =  ('http://return42.github.io/linuxdoc', None)
intersphinx_mapping['dbxml2rst'] =  ('http://return42.github.io/dbxml2rst', None)

