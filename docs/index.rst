.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc:

========
LinuxDoc
========

The LinuxDoc library contains sphinx-doc_ extensions and command line tools to
extract documentation from C/C++ source file comments. Even if this project
started in context of the Linux-Kernel documentation, you can use these
extensions in common sphinx-doc_ projects. LinuxDoc is hosted at github:
https://github.com/return42/linuxdoc


.. toctree::
   :maxdepth: 1

   install
   linuxdoc-howto/index
   cmd-line
   linux


LinuxDoc feature overview
=========================

kernel-doc
  A "C" friendly markup, the parser, the Sphinx-doc extension and some tools.
  The kernel-doc markup embeds documentation within the C source files, using a
  few simple conventions. The parser grabs the documentation from source and
  generates proper reST :ref:`[ref] <kernel-doc-intro>`.  The parser is written
  in Python and its API is used by the corresponding Sphinx-doc extension.
  Command line tools shipped with:

  - kernel-autodoc: Suitable for automatic API documentation :ref:`[ref]
    <kernel-autodoc>`.

  - kernel-lintdoc: *Lint* kernel-doc comments from source code :ref:`[ref]
    <kernel-lintdoc>`.

  - kernel-doc: A command line interface for kernel-doc's parser API :ref:`[ref]
    <kernel-doc-cmd>`.

kernel-doc-man
  A man page builder. An extension/replacement of the common Sphinx-doc *man*
  builder also integrated in the kernel-doc Sphinx-doc extension :ref:`[ref]
  <man-pages>`.

flat-table
  A diff and author friendly list-table replacement with *column-span*,
  *row-span* and *auto-span* :ref:`[ref] <rest-flat-table>`.

cdomain
  A customized `Sphinx's C Domain`_ extension. Suitable for demanding projects
  :ref:`[ref] <customized-c-domain>`.

kfigure
  Sphinx extension which implements scalable image handling. Simplifies image
  handling from the author's POV. Wins where Sphinx-doc image handling
  fails. Whatever graphic tools available on your build host, you always get the
  best output-format. Graphviz's DOT format included :ref:`[ref] <kfigure>`.

kernel-include
  A replacement for the ``include`` reST directive. The directive expand
  environment variables in the path name and allows to include files from
  arbitrary locations ref:`[ref] <kernel-include-directive>`.


Remarks for Kernel developer
============================

Some of the LinuxDoc features are already a part of the kernel source others not
(yet). E.g. the Sphinx-doc extensions flat-table, cdomain, kfigure and
kernel-include are merged into Kernel's source tree. On the other side, e.g. for
parsing kernel-doc comments, the Linux Kernel build process uses a Perl scripts
while LinuxDoc brings a python module with a kernel-doc parser. With this, the
documentation build becomes more reliable, flexible and faster.  There is a
patch :ref:`[ref] <patch-linux-kernel>` for Kernel's sources available with you
can use LinuxDoc when building the Kernel (and its documentation).


Known applications
==================

There is a *POC* which made use of LinuxDoc.  The *POC* demonstrates and tests
some alternative concepts for the Linux-Kernel documentation.

* https://github.com/return42/sphkerneldoc for the output see
* https://h2626237.stratoserver.net/kernel



Source Code
===========

.. toctree::
   :maxdepth: 2

   linuxdoc-api/linuxdoc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
