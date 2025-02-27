.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc:

========
LinuxDoc
========

The LinuxDoc library contains:

:ref:`kernel-doc <kernel-doc-intro>`
  A "C" friendly markup, the parser, the Sphinx-doc extension and some tools.
  The kernel-doc markup embeds documentation within the C source files, using a
  few simple conventions. The parser grabs the documentation from source and
  generates proper reST :ref:`[ref] <kernel-doc-intro>`.

  The parser is written in Python and its API is used by the corresponding
  Sphinx-doc extension.  Command line tools shipped with:

  - :ref:`linuxdoc.autodoc`: Suitable for automatic API documentation

  - :ref:`linuxdoc.lintdoc`: *Lint* kernel-doc comments from source code.

  - :ref:`linuxdoc.rest`: A command line interface for kernel-doc's parser API.

:ref:`kernel-doc-man <man-pages>`
  A man page builder. An extension/replacement of the common Sphinx-doc *man*
  builder also integrated in the kernel-doc Sphinx-doc extension.

:ref:`flat-table <xref_table_concerns>`
  A diff and author friendly list-table replacement with *column-span*,
  *row-span* and *auto-span* :ref:`[ref] <rest-flat-table>`.

:ref:`cdomain <customized-c-domain>`
  A customized `Sphinx's C Domain`_ extension. Suitable for demanding projects.

:ref:`kfigure`
  Sphinx extension which implements scalable image handling. Simplifies image
  handling from the author's POV. Wins where Sphinx-doc image handling
  fails. Whatever graphic tools available on your build host, you always get the
  best output-format. Graphviz's DOT format included.

:ref:`kernel-include <kernel-include-directive>`
  A replacement for the ``include`` reST directive. The directive expand
  environment variables in the path name and allows to include files from
  arbitrary locations.


.. admonition:: About "LinuxDoc"

   Even if this project started in context of the Linux-Kernel documentation
   (where the name comes from), you can use these extensions in common
   sphinx-doc_ projects.  If this is unclear to you, take a look at our
   :ref:`Introduction <kernel-doc-intro>`.

---------

Table of Contents
=================

.. toctree::
   :maxdepth: 3

   Introduction <kernel-doc-intro>
   install
   linuxdoc-howto/index
   cmd-line

LinuxDoc is hosted at github: https://github.com/return42/linuxdoc

---------

Source Code
===========

.. toctree::
   :maxdepth: 2

   linuxdoc-api/linuxdoc

---------

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

---------
