#!/usr/bin/env python
# -*- coding: utf-8; mode: python -*-

from setuptools import setup, find_packages
import linuxdoc

install_requires = [
    'fspath' ]

dependency_links=[
    'git+http://github.com/return42/fspath.git' ]

setup(
    name               = "linuxdoc"
    , version          = linuxdoc.__version__
    , description      = linuxdoc.__description__
    , long_description = linuxdoc.__doc__
    , url              = linuxdoc.__url__
    , author           = "Markus Heiser"
    , author_email     = "markus.heiser@darmarIT.de"
    , license          = linuxdoc.__license__
    , keywords         = "linux kernel-doc"
    , packages         = find_packages(exclude=['docs', 'tests'])
    , install_requires = install_requires
    , dependency_links = dependency_links

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    , classifiers = [
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
)
