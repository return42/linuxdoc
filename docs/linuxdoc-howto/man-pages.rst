.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _man-pages:

==================================
man pages from kernel-doc comments
==================================

The :py:class:`linuxdoc.manKernelDoc.KernelDocManBuilder` produces manual pages
in the groff format.  It is a *man* page builder for Sphinx-doc, mainly written
to generate manual pages from kernel-doc comments by scanning Sphinx's master
``doc-tree`` for *sections* marked with a

.. code-block:: rst

   .. kernel-doc-man:: <declaration-name>.<man-sect no>

directive and build manual pages from those marked *sections*.

Usage::

  $ sphinx-build -b kernel-doc-man ...

Since the ``kernel-doc-man`` is an extension of the common `sphinx *man* builder
<http://www.sphinx-doc.org/en/stable/config.html#confval-man_pages>`_, it is
also a full replacement, building booth, the common sphinx man-pages and those
marked with the ``.. kernel-doc-man::`` directive.

Mostly authors will use this feature in their reST documents in conjunction with
the ``.. kernel-doc::`` :ref:`directive <kernel-doc-man-sect>`, to create man
pages from kernel-doc comments.  This could be done, by setting the man section
number with the option ``man-sect``, e.g.:

.. code-block:: rst

  .. kernel-doc:: include/linux/debugobjects.h
      :export:
      :man-sect: 9

With this ``:man-sect: 9`` option, the kernel-doc parser will insert a:

.. code-block:: rst

   .. kernel-doc-man:: <declaration-name>.<man-sect no>

directive in the reST output, for all :ref:`exported <kernel-doc-options>`
functions, unions etc. which are documented with by kernel-doc comments in the
source code.
