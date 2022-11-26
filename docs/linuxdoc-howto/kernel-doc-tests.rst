.. -*- coding: utf-8; mode: rst -*-

.. _conf.py: http://www.sphinx-doc.org/en/stable/config.html

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


.. _opt_man-sect:

option ``:man-sect:``
=====================

.. _man_pages: http://www.sphinx-doc.org/en/stable/config.html#confval-man_pages

In the :ref:`opt_export` example, we can add a ``:man-sect: 2`` option, to
generate man pages with the :ref:`kernel-doc-man builder <man-pages>` for all
exported symbols.  The usage is:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./all-in-a-tumble.h
      :module: test
      :man-sect: 2

In the conf.py_ file we set man_pages_ and :ref:`kernel_doc_mansect
<kernel-doc-config>`::

  kernel_doc_mansect = None
  man_pages = [ ]

To place and gzip the manuals in ``dist/docs/man`` Folder see
:ref:`kernel-doc-man_builder`.

.. only:: builder_html

   You can include the man-page as a download item in your HTML like this
   (relative build path is needed):

   .. code-block:: rst

      :download:`user_function.2.gz   <../../dist/docs/man/user_function.2.gz>`

   .. admonition:: download directive
      :class: rst-example

      :download:`user_function.2.gz   <../../dist/docs/man/user_function.2.gz>`

   Or just set a link to the man page file (relative HTML URL is needed)

   .. code-block:: rst

      hyperlink to: `user_function.2.gz <../man/user_function.2.gz>`_

   .. admonition:: link man folder ``/man``
      :class: rst-example

      hyperlink to: `user_function.2.gz <../man/user_function.2.gz>`_

To view a (downloaded) man-page use::

  $ man ~/Downloads/user_function.2.gz


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
      :man-sect: 2


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
      :module: test.fnattrs

The ``exp-method`` and ``exp-ids`` could be respectively omitted if
``kernel_doc_exp_method`` and ``kernel_doc_exp_ids`` are set in the sphinx
configuration.

.. admonition:: exported symbols
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :export:  ./all-in-a-tumble.h
      :exp-method: attribute
      :exp-ids: API_EXPORTED
      :module: test.fnattrs

.. _opt_internal:

option ``:internal:``
---------------------

Include documentation of all documented definitions, **not** exported.  This
test gathers exports from :origin:`test_internals.h
<docs/linuxdoc-howto/test_internals.h>` and :origin:`test_internals.c
<docs/linuxdoc-howto/test_internals.c>` and parses comments from
:origin:`test_internals.c <docs/linuxdoc-howto/test_internals.c>`, from where
only the *not exported* definitions are used in the reST output.

.. attention::

   The both examples below also demonstrate that it is not good to mix the
   export methods (``:exp-method: [macro|attribute]``) in one source
   ``test_internals.[hc]``.  Only one methode can be used by the ``:internal:``
   option to identfy a symbol to be exported.

.. tabs::

   .. group-tab:: exp-method is ``macro``

      From :``test_internals.h``:

      .. kernel-doc::  ./test_internals.h
	 :snippets: EXP_SYMB

      From ``test_internals.c``:

      .. kernel-doc::  ./test_internals.c
	 :snippets: EXP_SYMB

   .. group-tab:: exp-method is ``attribute``

      From ``test_internals.c``:

      .. kernel-doc::  ./test_internals.c
	 :snippets: API_EXP

      From ``test_internals.h``:

      .. kernel-doc::  ./test_internals.h
	 :snippets: API_EXP

.. tabs::

   .. group-tab:: exp-method is ``macro``

      .. code-block:: rst

	 .. kernel-doc::  ./test_internals.c
	    :internal:  ./test_internals.h
	    :module: test_internals_A
	    :exp-method: macro
	    :exp-ids: EXP_SYMB

      .. admonition:: internal symbols (when exp-method is ``macro``)
	 :class: rst-example

	 .. kernel-doc::  ./test_internals.c
	    :internal:  ./test_internals.h
	    :module: test_internals_A
	    :exp-method: macro
	    :exp-ids: EXP_SYMB

   .. group-tab:: exp-method is ``attribute``

      .. code-block:: rst

	 .. kernel-doc::  ./test_internals.c
	    :internal:  ./test_internals.h
	    :module: test_internals_B
	    :exp-method: attribute
	    :exp-ids: API_EXP

      .. admonition:: internal symbols (when exp-method is ``attribute``)
	 :class: rst-example

	 .. kernel-doc::  ./test_internals.c
	    :internal:  ./test_internals.h
	    :module: test_internals_B
	    :exp-method: attribute
	    :exp-ids: API_EXP


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
      :symbols:  sys_tgkill

.. admonition:: missing exports
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.c
      :symbols:  sys_tgkill
