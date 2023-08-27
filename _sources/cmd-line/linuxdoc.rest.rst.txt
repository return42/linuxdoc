.. include:: ../refs.txt

.. _linuxdoc.rest:

=================
``linuxdoc.rest``
=================

Parse kernel-doc comments from source code and print the reST to stdout.  This
command exits, to see the generated reST, normally you use the :ref:`kernel-doc
directive <kernel-doc-directive>` in your reST documentation.::

  $ linuxdoc.rest /share/linux/include/media/lirc_dev.h

To see the difference between :ref:`vintage-kernel-doc-mode` and
:ref:`reST-kernel-doc-mode` use the option ``--markup kernel-doc``.
