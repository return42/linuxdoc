========
linuxdoc
========

The *linuxdoc* lib contains python extensions related to the build process of
the Linux-Kernel documentation.

:copyright:  Copyright (C) 2016 Markus Heiser
:license:    GPL Version 2, June 1991 see linux/COPYING for details.

It is a straight forward implementation in pure python (no perl scripot or other
executable calls). Some of theses extensions are already a part of the kernel
source others not (yet). E.g. the Sphinx-doc extensions ``flat-table`` and
``kernel-include`` are merged into the kernel source tree. On the other side,
e.g. for parsing kernel-doc comments, the linux kernel build uses a perl scripts
while linuxdoc brings a python module with a kernel-doc parser. With this the
documentation build becomes much more clear and flexible (and faster).

If you like to see how (fast) *linuxdoc* builds your kernel documentation,
follow the more detailed installation instruction in the documentation.

* documentation: http://return42.github.io/linuxdoc
* reposetory:    `github return42/fspath <https://github.com/return42/linuxdoc>`_
* author e-mail: *markus.heiser*\ *@*\ *darmarIT.de*

Installing
==========

Install bleading edge::

  pip install --user git+http://github.com/return42/linuxdoc.git

or clone from github::

  git clone https://github.com/return42/linuxdoc
  cd linuxdoc
  make install
