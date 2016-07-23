# -*- coding: utf-8 -*-
#
# Sphinx documentation build configuration file

import re
import linuxdoc

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
