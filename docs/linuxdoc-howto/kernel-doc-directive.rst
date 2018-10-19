.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _conf.py: http://www.sphinx-doc.org/en/stable/config.html

.. _kernel-doc-directive:

============================
kernel-doc in reST documents
============================

To integrate :ref:`kernel-doc <kernel-doc-syntax>` comments into a reST document
(e.g. in a *book*), there exists a reST-directive_ named ``kernel-doc`` .  The
directive comes with options to fine grain control which parts should be placed
into the reST document.  With no options given, the complete kernel-doc comments
from a source file will be inserted. So, the first and very simple example is:

.. code-block:: rst

   My Media Book
   =============

   .. kernel-doc:: include/media/media-device.h

With this small example the kernel-doc comments from the media-device.h will be
inserted direct under the chapter "My Media Book". The "DOC:" sections, the function
and the type descriptions will be inserted in the order they appear in the source file.
Mostly you want to select more fine grained, read on to see how.

.. _kernel-doc-options:

kernel-doc options
==================

Here is a short overview of the directives options:

.. code-block:: rst

    .. kernel-doc:: <src-filename>
        :doc: <section title>
        :no-header:
        :export:
        :internal:
        :exp-method: <method>
        :exp-ids:    <identifier [, identifiers [, ...]]>
        :functions: <function [, functions [, ...]]>
        :module:    <prefix-id>
        :man-sect:  <man sect-no>
        :snippets:  <snippet [, snippets [, ...]]>
        :language:  <snippet-lang>
        :linenos:
        :debug:

The argument ``<src-filename>`` is required, it points to a source file in the
kernel source tree. The pathname is relative to kernel's root folder.  The
options have the following meaning, but be aware that not all combinations of
these options make sense:

``:doc: <section title>`` (:ref:`doc_sections`)
    Include content of the ``DOC:`` section titled ``<section title>``.  Spaces
    are allowed in ``<section title>``; do not quote the ``<section title>``.

    The next option make only sense in conjunction with option ``doc``:

    ``:no-header:`` (:ref:`opt_no-header`)
        Do not output DOC: section's title. Useful, if the surrounding context
        already has a heading, and the DOC: section title is only used as an
        identifier.  Take in mind, that this option will not suppress any native
        reST heading markup in the comment.

``:export: [<src-fname-pattern> [, ...]]`` (:ref:`exported_symbols`)
    Include documentation for all function, struct or whatever definition in
    ``<src-filename>``, exported using EXPORT_SYMBOL macro (``EXPORT_SYMBOL``,
    ``EXPORT_SYMBOL_GPL`` & ``EXPORT_SYMBOL_GPL_FUTURE``) either in
    ``<src-filename>`` or in any of the files specified by
    ``<src-fname-pattern>``.

    The ``<src-fname-pattern>`` (glob) is useful when the kernel-doc comments
    have been placed in header files, while EXPORT_SYMBOL are next to the
    function definitions.

``:internal: [<src-fname-pattern> [, ...]]`` (:ref:`opt_internal`)
    Include documentation for all documented definitions, **not** exported using
    EXPORT_SYMBOL macro either in ``<src-filename>`` or in any of the files
    specified by ``<src-fname-pattern>``.

``:exp-method: <method>``
    Change the way exported symbols are specified in source code.  Default value
    ``macro`` if not provided, can be set globally by
    :ref:`kernel_doc_exp_method <kernel-doc-config>` in the sphinx conf.py_.


    The ``<method>`` must one of
    the following value:

    ``macro``
        Exported symbols are specified by macros (whose names are controlled by
        ``exp-ids`` option) invoked in the source the following way:
        ``THIS_IS_AN_EXPORTED_SYMBOL(symbol)``

    ``attribute``
        Exported symbols are specified definition using a specific attribute
        (controlled by ``exp-ids`` option) either in their declaration or
        definition: ``THIS_IS_AN_EXPORTED_SYMBOL int symbol(void* some_arg)
        {...}``

``:exp-ids: <identifier [, identifiers [, ...]]>``
    Use the specified list of identifiers instead of default value:
    EXPORT_SYMBOL, EXPORT_SYMBOL_GPL, EXPORT_SYMBOL_GPL_FUTURE.  Default value
    can be overriden globally by sphinx conf.py_ option :ref:`kernel_doc_exp_ids
    <kernel-doc-config>`.

``:known-attrs: <attr [, attrs [, ...]]>``
    Specified a list of function attributes that are known and must be hidden
    when displaying function prototype.

    When ``:exp-method:`` is set to ``attribute`` the list in ``:exp-ids:`` is
    considered as known and added implicitly to this list of known attributes.
    The default list is empty and can be adjusted by the sphinx configuration
    option :ref:`kernel_doc_known_attrs <kernel-doc-config>`.

``:functions: <name [, names [, ...]]>`` (:ref:`kernel-doc-functions`, :ref:`kernel-doc-structs`)
   Include documentation for each named definition.

``:module: <prefix-id>``
    The option ``:module: <id-prefix>`` sets a module-name.  The module-name is
    used as a prefix for automatic generated IDs (reference anchors).  To give a
    example, if you like to refer ``my_struct`` from module ``example`` use
    ``:ref:`example.my_struct``` (:ref:`example.my_struct`).  See module
    ``test`` in the :ref:`doc_sections` example.

``:man-sect: <sect-no>``
  Section number of the manual pages (see "``$ man man-pages``"").  Optional set
  :ref:`kernel_doc_mansect <kernel-doc-config>` option in sphinx conf.py_.  The
  man-pages are build by the ``kernel-doc-man`` builder.  Read on here:
  :ref:`man-pages`

``:snippets: <name [, names [, ...]]>``
    Inserts the source-code passage(s) marked with the snippet ``name``. The
    snippet is inserted with a `code-block:: <http://www.sphinx-doc.org/en/stable/markup/code.html>`_
    directive.

    The next options make only sense in conjunction with option ``snippets``:

    ``language <highlighter>``
        Set highlighting language of the snippet code-block.

    ``linenos``
        Set line numbers in the snippet code-block.

``:debug:``
    Inserts a code-block with the generated reST source. This might sometimes
    helpful to see how the kernel-doc parser transforms the kernel-doc markup to
    reST markup.


.. _kernel-doc-functions:

functions
=========

The following example inserts the documentation of struct 'user_function'.

.. code-block:: rst

     .. kernel-doc:: ./all-in-a-tumble.h
        :functions:  user_function
        :module:     example

These ``example`` module has already been defined in our :ref:`all-in-a-tumble
examples <all-in-a-tumble-debug>`, lets use it to show how to link such a
documentation:

.. code-block:: rst

   * Rendered example by ID with module prefix: :ref:`example.user_function`
   * Function reference: :c:func:`user_function`

.. admonition:: option ``:functions:``
   :class: rst-example

   * Rendered example by ID with module prefix: :ref:`example.user_function`
   * Function reference: :c:func:`user_function`


.. _kernel-doc-structs:
.. _kernel-doc-unions:
.. _kernel-doc-enums:
.. _kernel-doc-typedefs:

structs, unions, enums and typedefs
===================================

The following example inserts the documentation of struct 'my_long_struct'.

.. code-block:: rst

     .. kernel-doc:: ./all-in-a-tumble.h
        :functions:  my_long_struct
        :module:     example

To link into the :ref:`all-in-a-tumble examples <all-in-a-tumble-debug>` use:

.. code-block:: rst

   * Rendered example by ID with module prefix: :ref:`example.my_long_struct`
   * Type reference: :c:type:`my_long_struct` or the alternativ notation
     with title :c:type:`struct my_long_struct <my_long_struct>`

.. admonition:: option ``:functions: structs, unions, enums and typedefs``
   :class: rst-example

   * Rendered example by ID with module prefix: :ref:`example.my_long_struct`
   * Type reference: :c:type:`my_long_struct` or the alternativ notation
     with title :c:type:`struct my_long_struct <my_long_struct>`


.. _kernel-doc-snippets:

Snippets
========

The kernel-doc Parser supports a markup for :ref:`kernel-doc-syntax-snippets`.
By example; In the the :ref:`all-in-a-tumble examples <all-in-a-tumble.c-src>`
we have a small source code example:

.. code-block:: c

    /* parse-SNIP: hello-world */
    #include<stdio.h>
    int main() {
        printf("Hello World\n");
        return 0;
    }
    /* parse-SNAP: */

To insert the code passage between SNIP & SNAP use:

.. code-block:: rst

   .. kernel-doc::  ./all-in-a-tumble.c
      :snippets:  hello-world
      :language:  c
      :linenos:

And here is the rendered example:

   .. kernel-doc::  ./all-in-a-tumble.c
      :snippets:  hello-world
      :language:  c
      :linenos:

.. _kernel-doc-man-sect:

man pages (:man-sect:)
======================

To get man pages from kernel-doc comments, add the ``:man-sect:`` option to your
kernel-doc directives.  E.g. to get man-pages of media's remote control (file
``media/kapi/rc-core.rst``) add ``:man-sect: 9`` to all the kernel-doc includes.

.. code-block:: rst

  Remote Controller devices
  =========================

  Remote Controller core
  ----------------------

  .. kernel-doc:: include/media/rc-core.h
     :man-sect: 9

  .. kernel-doc:: include/media/rc-map.h
     :man-sect: 9

  LIRC
  ----

  .. kernel-doc:: include/media/lirc_dev.h
     :man-sect: 9

If you don't want to edit all your kernel-doc directives to get man page from,
set a global man-sect in your ``conf.py``, see sphinx configuration
:ref:`kernel_doc_mansect <kernel-doc-config>` and about build look at:
:ref:`man-pages`

Highlights and cross-references
===============================

The following special patterns are recognized in the kernel-doc comment
descriptive text and converted to proper reStructuredText markup and `Sphinx's C
Domain`_ references.

.. attention::

  The below are **only** recognized within kernel-doc comments, **not** within
  normal reStructuredText documents.

``funcname()``
  Function reference.

``@parameter``
  Name of a function parameter. (No cross-referencing, just formatting.)

``%CONST``
  Name of a constant. (No cross-referencing, just formatting.)

````literal````
  A literal block that should be handled as-is. The output will use a
  ``monospaced font``.

  Useful if you need to use special characters that would otherwise have some
  meaning either by kernel-doc script of by reStructuredText.

  This is particularly useful if you need to use things like ``%ph`` inside
  a function description.

``$ENVVAR``
  Name of an environment variable. (No cross-referencing, just formatting.)

``&struct name``
  Structure reference.

``&enum name``
  Enum reference.

``&typedef name``
  Typedef reference.

``&struct_name->member`` or ``&struct_name.member``
  Structure or union member reference. The cross-reference will be to the struct
  or union definition, not the member directly.

``&name``
  A generic type reference. Prefer using the full reference described above
  instead. This is mostly for legacy comments.

.. _kernel-doc-config:

kernel-doc config
=================

Within the `sphinx config`_ file (``conf.py`` or ``my_project.conf``) you can
set the following option.

kernel_doc_exp_method: ``macro``
  Set parser's default value for kernel-doc directive option  ``:exp-method:``
  (details see: :ref:`kernel-doc-options`)

kernel_doc_exp_ids: ``['EXPORT_SYMBOL', 'EXPORT_SYMBOL_GPL', 'EXPORT_SYMBOL_GPL_FUTURE']``
  Set parser's default value for kernel-doc directive option ``:exp-ids:``.
  (details see: :ref:`kernel-doc-options`)

kernel_doc_known_attrs: ``[...]``
  Set parser's default value for kernel-doc directive option  ``:known-attrs:``
  (details see: :ref:`kernel-doc-options`)

kernel_doc_mansect: ``None``
  Global fallback for man section of kernel-doc directives.  Set this value if
  you want to create man pages for those kernel-doc directives, which has not
  been set a ``:man-sect:`` value.  The default is ``None``, which means; do the
  opposite and create only man pages for those directives which has been set the
  ``:man-sect:`` option (``None`` is what you mostly want).

kernel_doc_mode: ``reST``
  Set parser's default kernel-doc mode ``[reST|kernel-doc]``.  Normally you wont
  set anything other than the default! See :ref:`reST-kernel-doc-mode` and
  :ref:`vintage-kernel-doc-mode`.

kernel_doc_verbose_warn: ``True``
  If true, more warnings will be logged.  E.g. a missing description of a
  function's return value will be logged.

kernel_doc_raise_error: ``True``
  If ``True`` fatal errors (like missing function descriptions) raise an error.
  The default is ``True``. This means that the build process break every time a
  serve error in the documentation build occur.  Often it might be better the
  build continues and inserts Oops on serve errors.  For this, set
  ``kernel_doc_raise_error`` to ``False``.  In the next example, the
  documentation of a non existing definition name ``no_longer_exists`` is
  required:

  .. code-block:: rst

      .. kernel-doc::  ./all-in-a-tumble.h
          :functions:  no_longer_exist

  Since this definition not exists (anymore), the following TODO entry with Oops
  is inserted (again; only when ``kernel_doc_raise_error`` is ``False``).

  .. admonition:: parser error inserts a ".. todo::" directive with *Oops* in
     :class: rst-example

     .. kernel-doc::  ./all-in-a-tumble.h
        :functions:  no_longer_exist

