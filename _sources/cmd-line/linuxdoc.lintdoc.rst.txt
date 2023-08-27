.. include:: ../refs.txt

.. _linuxdoc.lintdoc:

====================
``linuxdoc.lintdoc``
====================

Lint the kernel-doc comments in the source code.  E.g. to lint the kernel-doc
comments of a source-file.::

  $ linuxdoc.lintdoc /share/linux/include/media/lirc_dev.h

Alternative you could also *lint* whole parts of the source tree, e.g. the
include folder::

  $ linuxdoc.lintdoc /share/linux/include/

