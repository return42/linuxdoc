.. -*- coding: utf-8; mode: rst -*-

.. _conf.py: http://www.sphinx-doc.org/en/stable/config.html#confval-man_pages

.. _kernel-doc-tests:

===============
kernel-doc Test
===============

Wtihin this section you will find some :ref:`linuxdoc-howto` tests and examples
for common use cases.  The kernel-doc comments are taken from the source files
:ref:`all-in-a-tumble.c-src` and :ref:`all-in-a-tumble.h-src`.

.. contents::
   :local:

.. _doc_sections:

DOC sections
============

For a very simple example we use this DOC section from :ref:`all-in-a-tumble.h-src`:

.. kernel-doc::  ./all-in-a-tumble.h
   :snippets:  lorem

To insert content with heading use:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: lorem ipsum
      :module: test

With the module name ``test`` the title can be linked with:

.. code-block:: rst

    Here is a link to DOC: :ref:`test.lorem-ipsum`

Here is a link to DOC :ref:`test.lorem-ipsum` ...

.. admonition:: DOC section with header
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: lorem ipsum
      :module: test


.. _opt_no-header:

option ``:no-header:``
----------------------

To insert just the content, without the header use :ref:`option :no-header:
<kernel-doc-options>`:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: lorem ipsum
      :no-header:

.. admonition:: DOC section without header
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: lorem ipsum
      :no-header:


.. _multiple_doc_sections:

multiple DOC sections
---------------------

Its always recommended to separate different DOC sections in different comments.
Nevertheless, a few tests are to be carried out here with it.  The DOC section
tests are based on this comment:

.. kernel-doc::  ./all-in-a-tumble.h
   :snippets:  theory-of-operation

----

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: Theory of Operation
      :no-header:

.. admonition:: DOC section
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: Theory of Operation
      :no-header:

----

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: multiple DOC sections

.. admonition:: DOC section
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.h
      :doc: multiple DOC sections


.. _exported_symbols:

exported symbols
================

.. _opt_export:

option ``:export:``
-------------------

In the :ref:`all-in-a-tumble.h-src` header file we export:

.. kernel-doc::  ./all-in-a-tumble.h
   :snippets: EXPORT_SYMBOL

The documentation of the exported symbols is in :ref:`all-in-a-tumble.c-src`.
To gather exports from :ref:`all-in-a-tumble.h-src` and
:ref:`all-in-a-tumble.c-src` and parses comments from
:ref:`all-in-a-tumble.c-src` use :ref:`kernel-doc-options`:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./all-in-a-tumble.h
      :module: test

.. admonition:: exported symbols
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./all-in-a-tumble.h
      :module: test


options ``:export:, :exp-method:, :exp-ids:``
---------------------------------------------

This test gathers function from :ref:`all-in-a-tumble.c-src` whose function
attributes mark them as exported:

.. kernel-doc::  ./all-in-a-tumble.c
   :snippets: user_sum-c

and that are present in :ref:`all-in-a-tumble.h-src`:

.. kernel-doc::  ./all-in-a-tumble.h
   :snippets: user_sum-h

To insert the documentation use:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./all-in-a-tumble.h
      :exp-method: attribute
      :exp-ids: API_EXPORTED
      :module: test-fnattrs

The ``exp-method`` and ``exp-ids`` could be respectively omitted if
``kernel_doc_exp_method`` and ``kernel_doc_exp_ids`` are set in the sphinx
configuration.

.. admonition:: exported symbols
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./all-in-a-tumble.h
      :exp-method: attribute
      :exp-ids: API_EXPORTED
      :module: test-fnattrs

.. _opt_internal:

option ``:internal:``
---------------------

Include documentation for all documented definitions, **not** exported.  This
test gathers exports from :ref:`all-in-a-tumble.h-src` and
:ref:`all-in-a-tumble.c-src` and parses comments from
:ref:`all-in-a-tumble.c-src`, from where only the *not exported* definitions are
used in the reST output:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :internal:  ./all-in-a-tumble.h
      :module: tests-internal

The example also shows, that mixing different values for

- ``:exp-method:`` --> ``[macro|attribute]`` and
- ``:exp-ids:``    --> ``[EXPORT_SYMBOL|API_EXPORTED]``

in one source file is not well supported:

.. admonition:: internal symbols
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :internal:  ./all-in-a-tumble.h
      :module: tests-internal


Missing exports
---------------

In the next test, the ``:export: {file glob pattern}`` is used, but it does not
match any file, or there are no exports in the matching files.  Whatever, an
empty list of exported symbols is treated as an error:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./match_files_without_exports*

.. admonition:: missing exports
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./match_files_without_exports*


SYSCALL macro
=============

In the Kernel's source is a macro: `SYSCALL_DEFINEn()
<https://www.kernel.org/doc/html/latest/process/adding-syscalls.html#generic-system-call-implementation>`_.
By example:


.. kernel-doc::  ./all-in-a-tumble.c
   :snippets: test_SYSCALL

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :functions:  sys_tgkill

.. admonition:: missing exports
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :functions:  sys_tgkill
