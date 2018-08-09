.. -*- coding: utf-8; mode: rst -*-

.. _kernel-doc-tests:

================
Additional tests
================


DOC sections
============

The DOC section tests are based on this comment:

.. kernel-doc::  ./all-in-a-tumble.h
    :snippets:  theory-of-operation

multiple DOC sections
---------------------

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.h
       :doc: multiple DOC sections
       :no-header:

.. admonition:: DOC section
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.h
        :doc: multiple DOC sections
        :no-header:


option no-header
----------------

.. code-block:: rst

    .. kernel-doc::  ./all-in-a-tumble.h
        :doc:  Theory of Operation
        :no-header:

.. admonition:: DOC section with "no-header"
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.h
        :doc:  Theory of Operation
        :no-header:


exported symbols
================

Get documentation of exported symbols
-------------------------------------

This test gathers exports from ``all-in-a-tumble.h`` and ``all-in-a-tumble.c``
and parses comments from ``all-in-a-tumble.c``.

.. code-block:: rst

    .. kernel-doc::  ./all-in-a-tumble.c
        :export:  ./all-in-a-tumble.h
        :module: test-example
        :man-sect: 2

.. admonition:: exported symbols
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.c
        :export:  ./all-in-a-tumble.h
        :module: test-example
        :man-sect: 2


This test gathers function ``all-in-a-tumble.c`` whose function attributes
mark them as exported and that are present in ``all-in-a-tumble.h``.

.. code-block:: rst

    .. kernel-doc::  ./all-in-a-tumble.c
        :export:  ./all-in-a-tumble.h
        :exp-method: attribute
        :exp-ids: API_EXPORTED
        :module: test-example-fnattrs
        :man-sect: 2

.. admonition:: exported symbols
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.c
        :export:  ./all-in-a-tumble.h
        :exp-method: attribute
        :exp-ids: API_EXPORTED
        :module: test-example-fnattrs
        :man-sect: 2

The ``exp-method`` and ``exp-ids`` could be respectively omitted if
``kernel_doc_exp_method`` and ``kernel_doc_exp_ids`` are set in the sphinx
configuration.


Get documentation of internal symbols
-------------------------------------

This test gathers exports from ``all-in-a-tumble.h`` and ``all-in-a-tumble.c``
and parses comments from ``all-in-a-tumble.c``, from where only the *not
exported* definitions are used in the reST output:

.. code-block:: rst

    .. kernel-doc::  ./all-in-a-tumble.c
        :internal:  ./all-in-a-tumble.h
        :module: additional-tests

.. admonition:: internal symbols
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.c
        :internal:  ./all-in-a-tumble.h
        :module: additional-tests


Missing exports
---------------

In the next test, the ``:export: {file glob pattern}`` is used, but it does not
match any file, or there are no exports in the matching files. Whatever, An
empty list of exported symbols is treated as an error:

.. code-block:: rst

    .. kernel-doc::  ./all-in-a-tumble.c
        :export:  ./match_files_without_exports*

.. admonition:: missing exports
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.c
        :export:  ./match_files_without_exports*

SYSCALL & EVENT
===============

Source code:

.. kernel-doc::  ./all-in-a-tumble.c
    :snippets: test_SYSCALL

.. code-block:: rst

    .. kernel-doc::  ./all-in-a-tumble.c
        :functions:  sys_rt_sigprocmask

.. admonition:: missing exports
    :class: rst-example

    .. kernel-doc::  ./all-in-a-tumble.c
        :functions:  sys_rt_sigprocmask
