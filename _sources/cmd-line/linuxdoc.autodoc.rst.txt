.. include:: ../refs.txt

.. _linuxdoc.autodoc:

====================
``linuxdoc.autodoc``
====================

Suitable for automatic API documentation.  Parses your source tree, grabs
kernel-doc comments and generates analogous tree of reST files with the content
from the kernel-doc comments.  E.g. to parse kernel's whole source tree::

  $ linuxdoc.autodoc /share/linux ./out

This parses the whole folder ``/share/linux`` and outputs a analogous tree with
reST files in the ``./out`` folder.  Alternative you could also parse only parts
of the source tree, e.g. the include folder::

  $ linuxdoc.autodoc --markup kernel-doc /share/linux/include ./out

The option ``--markup kernel-doc`` is a tribute to the historical fact, that
most of the kernel-doc comments (in the Linux kernel) are old and not reST
compliant. This circumstance is also described see :ref:`[ref]
<vintage-kernel-doc-mode>`
