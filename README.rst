========
linuxdoc
========

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

Installing
==========

Works as usual, e.g. use::

  pip install --user git+http://github.com/return42/linuxdoc.git

If you like to see how (fast) *linuxdoc* builds your kernel documentation,
follow the more detailed installation instructions in the documentation.

Online at http://return42.github.io/linuxdoc or create by::

   make docs

Development
===========

`github return42/linuxdoc <https://github.com/return42/linuxdoc>`_

The authors
===========

The linuxdoc lib is maintained by **Markus Heiser**, e-mail address
*markus.heiser*\ *@*\ *darmarIT.de*.
