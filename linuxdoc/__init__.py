# -*- coding: utf-8; mode: python -*-
u"""
The linuxdoc lib contains python extensions related to the build process of the
Linux-Kernel documentation.

It is a straight forward implementation in pure python (no perl or shell scripts
call). Some of theses extensions are already a part of the kernel source others
not (yet). E.g. the Sphinx-doc extension flat-table is merged into the
kernel. On the other side, for parsing kernel-doc comments, the linux kernel
build uses a perl scripts while linuxdoc brings a python module with a
kernel-doc parser. With whitch the documentation build becomes much more clear
and flexible.

:copyright:  Copyright (C) 2016 Markus Heiser
:license:    GPL Version 2, June 1991 see linux/COPYING for details.

"""

__version__     = "20160723"
__copyright__   = "2016 Markus Heiser"
__url__         = "https://github.com/return42/linuxdoc"
__description__ = "python extensions related for the Linux-Kernel documentation build"
__license__     = "GPLv2"
