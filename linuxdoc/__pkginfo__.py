# -*- coding: utf-8; mode: python -*-
# pylint: disable=invalid-name,redefined-builtin
"""
python package meta informations
"""

package      = 'linuxdoc'
version      = '20181010'
authors      = ['Markus Heiser', ]
emails       = ['markus.heiser@darmarIT.de', ]
copyright    = '2018 Markus Heiser'
url          = 'https://github.com/return42/linuxdoc'
description  = 'Sphinx-doc extensions & tools to extract documentation from C/C++ source file comments.'
license      = 'GPLv2'
keywords     = 'sphinx extension doc source code comments kernel-doc linux'

install_requires = [
    'fspath' ]

def get_entry_points():
    """get entry points of the python package"""
    return {
        'console_scripts': [
            'kernel-doc = linuxdoc.kernel_doc:main'
            , 'kernel-autodoc = linuxdoc.autodoc:main'
            , 'kernel-lintdoc = linuxdoc.lint:main'
            , 'kernel-grepdoc = linuxdoc.grep_doc:main'
            , ] , }

# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable"
    , "Intended Audience :: Developers"
    , "Intended Audience :: Other Audience"
    , "License :: OSI Approved :: GNU General Public License v2 (GPLv2)"
    , "Operating System :: OS Independent"
    , "Programming Language :: Python"
    , "Programming Language :: Python :: 2"
    , "Programming Language :: Python :: 3"
    , "Topic :: Utilities"
    , "Topic :: Documentation :: linux"
    , "Topic :: Software Development :: Documentation"
    , "Topic :: Software Development :: Libraries"
    , "Topic :: Text Processing" ]
