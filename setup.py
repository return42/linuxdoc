#!/usr/bin/env python
# -*- coding: utf-8; mode: python -*-
# pylint: disable=invalid-name, missing-docstring

import os
from os.path import join as ospj
import io
import imp
from setuptools import setup, find_packages

_dir = os.path.abspath(os.path.dirname(__file__))

SRC    = ospj(_dir, 'linuxdoc')
README = ospj(_dir, 'README.rst')
DOCS   = ospj(_dir, 'docs')
TESTS  = ospj(_dir, 'tests')

PKG = imp.load_source('__pkginfo__', ospj(SRC, '__pkginfo__.py'))

def readFile(fname, m='rt', enc='utf-8', nl=None):
    with io.open(fname, mode=m, encoding=enc, newline=nl) as f:
        return f.read()

setup(
    name               = PKG.package
    , version          = PKG.version
    , description      = PKG.description
    , long_description = readFile(README)
    , url              = PKG.url
    , author           = PKG.authors[0]
    , author_email     = PKG.emails[0]
    , license          = PKG.license
    , keywords         = PKG.keywords
    , packages         = find_packages(exclude=['docs', ])
    , install_requires = PKG.install_requires
    , entry_points     = PKG.get_entry_points()
    , classifiers      = PKG.classifiers
)
