.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc_cmdline:

==================
Command line tools
==================

Beside the library, the installation of the LinuxDoc :ref:`[ref]
<install_linuxdoc>` also installs some command-line tools described here (or use
the ``--help`` option).

.. _kernel-autodoc:

``kernel-autodoc``
==================

Suitable for automatic API documentation.  Parses your source tree, grabs
kernel-doc comments and generates analogous tree of reST files with the content
from the kernel-doc comments. E.g. to parse kernel's whole source tree::

  $ kernel-autodoc /share/linux ./out

This parses the whole folder ``/share/linux`` and outputs a analogous tree with
reST files in the ``./out`` folder. Alternative you could also parse only parts
of the source tree, e.g. the include folder::

  $ kernel-autodoc --markup kernel-doc /share/linux/include ./out

The option ``--markup kernel-doc`` is a tribute to the historical fact, that
most of the kernel-doc comments are old and not reST compliant. This
circumstance is also described see :ref:`[ref] <vintage-kernel-doc-mode>`

.. _kernel-lintdoc:

``kernel-lintdoc``
==================

Lint *kernel-doc* comments from source code. E.g. to lint the kernel-doc
comments of a source-file.::

  $ kernel-lintdoc /share/linux/include/media/lirc_dev.h

Alternative you could also *lint* whole parts of the source tree, e.g. the
include folder::

  $ kernel-lintdoc /share/linux/include/

.. _kernel-doc-cmd:

``kernel-doc``
==============

Parse kernel-doc comments from source code and print the reST to stdout.  This
command exits, to see the generated reST, normally you use the :ref:`kernel-doc
directive <kernel-doc-directive>` in your reST documentation.::

  $ kernel-doc /share/linux/include/media/lirc_dev.h

To see the difference between :ref:`vintage-kernel-doc-mode` and
:ref:`reST-kernel-doc-mode` use the option ``--markup kernel-doc``.
