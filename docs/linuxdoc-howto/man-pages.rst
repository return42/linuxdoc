.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _man-pages:

==================================
man pages from kernel-doc comments
==================================

.. _ManualPageBuilder: http://www.sphinx-doc.org/en/stable/usage/builders/index.html#sphinx.builders.manpage.ManualPageBuilder

.. _`conf.py man-pages`: http://www.sphinx-doc.org/en/stable/config.html#confval-man_pages

.. _`Manual section number`: https://en.wikipedia.org/wiki/Man_page#Manual_sections

The :py:class:`linuxdoc.manKernelDoc.KernelDocManBuilder` produces manual pages
in the groff format.  It is a *man* page builder for Sphinx-doc, mainly written
to generate manual pages from kernel-doc comments by scanning Sphinx's master
``doc-tree`` for *sections* marked with a

.. code-block:: rst

   .. kernel-doc-man:: <declaration-name>.<man-sect no>

directive and build manual pages from those marked *sections*.  Usage::

  $ sphinx-build -b kernel-doc-man ...

Since the ``kernel-doc-man`` builder is an extension of the common
ManualPageBuilder_ it is also a full replacement, building booth, the common
sphinx man-pages from `conf.py man-pages`_ and those marked with the
``.. kernel-doc-man::`` directive.

Mostly authors will use this feature in their reST documents in conjunction with
the :ref:`.. kernel-doc:: <kernel-doc-directive>` directive, to create man pages
from kernel-doc comments.  This could be done, by setting the `Manual section
number`_ with the ``:man-sect:`` :ref:`kernel-doc option <kernel-doc-options>`.
See: :ref:`kernel-doc-man-sect`

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
       :functions: user_function
       :man-sect: 1

With this ``:man-sect: <man-sect no>`` option, the kernel-doc parser will insert
a directive in the reST output:

.. code-block:: rst

   .. kernel-doc-man:: <declaration-name>.<man-sect no>

The ``<declaration-name>`` is the name of the manual page. Therefor the name of
the :ref:`kernel-doc comment <kernel-doc-syntax>` is used.  Which is the name of
the :ref:`struct, union <kernel-doc-syntax-structs-unions>`, :ref:`enum, typedef
<kernel-doc-syntax-enums-typedefs>` or :ref:`function
<kernel-doc-syntax-functions>`.

.. _kernel-doc-man_builder:

``kernel-doc-man`` Builder
==========================

As described above, the ``kernel-doc-man`` builder will build all the manuals
which are defined in the `conf.py man-pages`_ and from all sections marked with
the ``.. kernel-doc-man`` directive.  To place and gzip the man-pages in
``dist/docs/man`` use::

  $ sphinx-build -b kernel-doc-man docs dist/docs/man
  building [kernel-doc-man]: all manpages ...
  scan master tree for kernel-doc man-pages ...
  writing man pages ... user_function.2 internal_function.2 ...

  $ find dist/docs/man -name '*.[0-9]' -exec gzip -nf {} +

To see how it works, jump to the :ref:`opt_man-sect` example.
