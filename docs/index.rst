.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc:

========
LinuxDoc
========

The *linuxdoc* lib contains sphinx-doc_ extensions and command line tools
related to the build process of the Linux-Kernel documentation. Even if this
project started in context of the Linux-Kernel documentation, you can use these
extensions in common sphinx-doc_ projects.

.. toctree::
   :maxdepth: 1

   install
   linuxdoc-howto/index
   cmd-line
   linux



Remarks for Kernel developer
============================

Some of the LinuxDoc features are already a part of the kernel source others not
(yet). E.g. the Sphinx-doc extensions ``kernel-figure``, ``kernel-include`` and
``flat-table`` are merged into Kernel's source tree. On the other side, e.g. for
parsing kernel-doc comments, the Linux Kernel build process uses a Perl scripts
while LinuxDoc brings a python module with a kernel-doc parser. With this, the
documentation build becomes more reliable, flexible and faster.

There is a patch :ref:`[ref] <patch-linux-kernel>` for Kernel's sources
available with you can use LinuxDoc when building the Kernel (and its
documentation). There is also a *POC* to demonstrate/test some *alternative*
Linux-Kernel documentation concepts which uses the LinuxDoc lib.

* https://github.com/return42/sphkerneldoc for the output see
* https://h2626237.stratoserver.net/kernel


Source Code Documentation
=========================

.. toctree::
   :maxdepth: 2

   linuxdoc/linuxdoc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`


.. automodule:: linuxdoc
    :members:
    :undoc-members:
    :show-inheritance:
