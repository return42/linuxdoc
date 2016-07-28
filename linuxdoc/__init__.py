# -*- coding: utf-8; mode: python -*-
u"""
The *linuxdoc* lib contains python extensions related to the build process of
the Linux-Kernel documentation.

It is a straight forward implementation in pure python (no Perl script or other
executable calls). Some of theses extensions are already a part of the kernel
source others not (yet). E.g. the Sphinx-doc extensions ``flat-table`` and
``kernel-include`` are merged into the kernel source tree. On the other side,
e.g. for parsing kernel-doc comments, the Linux kernel build uses a Perl scripts
while linuxdoc brings a python module with a kernel-doc parser. With this, the
documentation build becomes much more clear and flexible (and faster).

:copyright:  Copyright (C) 2016 Markus Heiser
:e-mail:     *markus.heiser*\ *@*\ *darmarIT.de*
:license:    GPL Version 2, June 1991 see Linux/COPYING for details.
:docs:       http://return42.github.io/linuxdoc
:repository: `github return42/fspath <https://github.com/return42/linuxdoc>`_

"""

__version__     = "20160723"
__copyright__   = "2016 Markus Heiser"
__url__         = "https://github.com/return42/linuxdoc"
__description__ = "python extensions related to the Linux-Kernel documentation build"
__license__     = "GPLv2"
