.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc:

========
LinuxDoc
========

.. automodule:: linuxdoc
    :members:
    :undoc-members:
    :show-inheritance:


Documentation
=============

.. toctree::
   :maxdepth: 1

   install
   cmd-line
   linux


About
=====

The LinuxDoc project brings a straight forward implementation in pure python (no
Perl script or other executable calls). Including the reference implementation
of kernel-doc parser described in the :ref:`kernel-doc:kernel-doc-howto`. Some
features of this suite are:

* lint :ref:`[ref] <kernel-lintdoc>`
* man pages  :ref:`[ref] <create-manpages>`
* autodoc :ref:`[ref] <kernel-autodoc>`
* flat-table directive :ref:`[ref] <kernel-doc:rest-flat-table>`
* kernel-include directive :ref:`[ref] <kernel-doc:kernel-include-directive>`

Some of theses features are already a part of the kernel source others not
(yet). E.g. the Sphinx-doc extensions ``flat-table`` and ``kernel-include`` are
merged into the kernel source tree. On the other side, e.g. for parsing
kernel-doc comments, the Linux kernel build uses a Perl scripts while linuxdoc
brings a python module with a kernel-doc parser. With this, the documentation
build becomes much more clear and flexible and faster.

.. hint::

   Please contact me (*markus.heiser*\ *@*\ *darmarIT.de*) if you want to see
   more features merged to the Linux-Kernel source tree.

Examples
========

Examples which make use of the linuxdoc lib extracting kernel-doc comments and
build HTML documentation.:

* Kernel documents: http://return42.github.io/sphkerneldoc/

    Include the DocBook-XML books which has been migrated with the
    :ref:`DocBook-XML to reST project <dbxml2rst:dbxml2rst>`.

* Kernel-Doc source tree: http://return42.github.io/sphkerneldoc/linux_src_doc/index.html

    Full scan of the kernel source tree with the command-line tool
    :ref:`kernel-autodoc`. The scan gather all kernel-doc comments and builds a
    analogous tree (`reST linux_src_doc`_)

.. _`reST linux_src_doc`: https://github.com/return42/sphkerneldoc/tree/master/doc/linux_src_doc


Source Code Documentation
=========================

.. toctree::
   :maxdepth: 2

   linuxdoc/linuxdoc


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
