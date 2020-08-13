.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc:

========
LinuxDoc
========

.. sidebar::  update 2020-08

   ATM LinuxDoc does not support Sphinx v3.0 or above (:commit:`a5290d5`).  The
   v3.0 includes a `C, initial rewrite`_ which is not downward compatible.  The
   :py:mod:`linuxdoc.cdomain` needs a complete revision within the model used by
   Sphinx v3.

.. _C, initial rewrite:   https://github.com/sphinx-doc/sphinx/commit/0f49e30c51b5cc5055cda5b4b294c2dd9d1df573#r38750737

The LinuxDoc library contains sphinx-doc_ extensions and command line tools to
extract documentation from C/C++ source file comments. Even if this project
started in context of the Linux-Kernel documentation (where the name comes
from), you can use these extensions in common sphinx-doc_ projects.  If this is
unclear to you, take a look at our :ref:`Introduction <kernel-doc-intro>`.

.. toctree::
   :maxdepth: 3

   Introduction <kernel-doc-intro>
   install
   linuxdoc-howto/index
   cmd-line
   kernel_dev_remarks
   linux

LinuxDoc is hosted at github: https://github.com/return42/linuxdoc


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
