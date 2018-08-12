# -*- coding: utf-8; mode: python -*-
u"""
The LinuxDoc library contains Sphinx-doc extensions and command line tools
related to the build process of the Linux-Kernel documentation.  Even if this
project started in context of the Linux-Kernel documentation, you can use these
extensions in common Sphinx-doc projects.

:copyright:  Copyright (C) 2018 Markus Heiser
:e-mail:     markus.heiser@darmarIT.de
:license:    GPL Version 2, June 1991 see Linux/COPYING for details.
:docs:       http://return42.github.io/linuxdoc
:repository: `github return42/linuxdoc <https://github.com/return42/linuxdoc>`_
"""

from . import __pkginfo__

__version__   = __pkginfo__.version
__author__    = __pkginfo__.authors[0]
__license__   = __pkginfo__.license
__copyright__ = __pkginfo__.copyright
