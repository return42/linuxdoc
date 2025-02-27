.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _kernel-include-directive:

====================================
Use kernel-include in reST documents
====================================

The ``kernel-include`` reST-directive is a replacement for the ``include``
directive. The ``kernel-include`` directive expand environment variables in
the path name and allows to include files from arbitrary locations.

.. hint::

   Including files from arbitrary locations (e.g. from ``/etc``) is a
   security risk for builders. This is why the ``include`` directive from
   docutils *prohibit* pathnames pointing to locations *above* the file-system
   tree where the reST document with the include directive is placed.

Substrings of the form ``$name`` or ``${name}`` are replaced by the value of
environment variable name. Malformed variable names and references to
non-existing variables are left unchanged.

.. code-block:: rst

    .. _media_header:

    ****************************
    Media Controller Header File
    ****************************

    .. kernel-include:: $BUILDDIR/media.h.rst

Since the ``kernel-include`` reST-directive is a replacement for the existing
``include`` directive, the options are the same, see `reST include directive`_.
