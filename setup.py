#!/usr/bin/env python
# pylint: disable=invalid-name, missing-docstring

import os
import io
import importlib
from setuptools import setup, find_packages

_dir = os.path.abspath(os.path.dirname(__file__))

SRC    = os.path.join(_dir, 'linuxdoc')
README = os.path.join(_dir, 'README.rst')
DOCS   = os.path.join(_dir, 'docs')
TESTS  = os.path.join(_dir, 'tests')


def load_source(modname, modpath):
    spec = importlib.util.spec_from_file_location(modname, modpath)
    if not spec:
        raise ValueError("Error loading '%s' module" % modpath)
    module = importlib.util.module_from_spec(spec)
    if not spec.loader:
        raise ValueError("Error loading '%s' module" % modpath)
    spec.loader.exec_module(module)
    return module


def readFile(fname, m='rt', enc='utf-8', nl=None):
    with io.open(fname, mode=m, encoding=enc, newline=nl) as f:
        return f.read()

PKG = load_source('__pkginfo__', os.path.join(SRC, '__pkginfo__.py'))

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
    , packages         = ['linuxdoc']
    , install_requires = PKG.install_requires
    , entry_points     = PKG.get_entry_points()
    , classifiers      = PKG.classifiers
    , project_urls     = PKG.project_urls
)
