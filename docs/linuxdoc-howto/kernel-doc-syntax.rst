.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _kernel-doc-syntax:

=================
kernel-doc syntax
=================

The format of a block comment is like this::

    /**
     * (data-type|DOC)? name(:)? (- short description)?
    (* @x: (description of parameter/member x)?)*
    (* a blank line)?
     * (Description of function or data structure)?
    (* a blank line)?
     * (sub-section header:
     * (sub-section description) )*
     (*)?*/


* ``(...)?`` signifies optional structure and
* ``(...)*`` signifies 0 or more structure elements

The name of the function, data-type respectively DOC is used as the section
header. The names of section headers must be unique per source file.

.. _kernel-doc-syntax-functions:

functions
=========

::

    /**
     * function_name(:)? (- short description)?
    (* @parameterx: (description of parameter x)?)*
    (* a blank line)?
     * (Description of function)?
    (* a blank line)?
     * (sub-section header:
     * (sub-section description) )*
     (*)?*/

All *description* text can span multiple lines, although the ``function_name`` &
its short description are traditionally on a single line.  Description text may
also contain blank lines (i.e., lines that contain only a "*").

So, the trivial example would be:

.. code-block:: c

    /**
     * my_function
     */

If the Description: header tag is omitted, then there must be a blank line
after the last parameter specification.:

.. code-block:: c

    /**
     * my_function - does my stuff
     * @my_arg: its mine damnit
     *
     * Does my stuff explained.
     */

or, could also use:

.. code-block:: c

    /**
     * my_function - does my stuff
     * @my_arg: its mine damnit
     * Description:
     * Does my stuff explained.
     */

You can also add additional sections. When documenting kernel functions you
should document the ``Context:`` of the function, e.g. whether the functions can
be called form interrupts. Unlike other sections you can end it with an empty
line.

A non-void function should have a ``Return:`` section describing the return
value(s).  Example-sections should contain the string ``EXAMPLE`` so that
they are marked appropriately in the output format.

.. kernel-doc::  ./all-in-a-tumble.c
    :snippets:  user_function
    :language:  c
    :linenos:

Rendered example: :ref:`example.user_function`

.. _kernel-doc-syntax-structs-unions:

structs, unions
===============

Beside functions you can also write documentation for ``structs``,
``unions``. Instead of the function name you must write the name of the
declaration; the ``struct`` or ``union`` must always precede the name. Nesting
of declarations is supported.  Use the ``@argument`` mechanism to document
members or constants.

Inside a ``struct`` description, you can use the 'private:' and 'public:' comment
tags.  Structure fields that are inside a 'private:' area are not listed in the
generated output documentation.  The 'private:' and 'public:' tags must begin
immediately following a ``/*`` comment marker.  They may optionally include
comments between the ``:`` and the ending ``*/`` marker.

.. kernel-doc::  ./all-in-a-tumble.h
    :snippets:  my_struct
    :language:  c
    :linenos:

Rendered example: :ref:`example.my_struct`

All descriptions can be multi-line, except the short function description.  For
really longs ``structs``, you can also describe arguments inside the body of the
``struct``.  There are two styles, single-line comments where both the opening
``/**`` and closing ``*/`` are on the same line, and multi-line comments where
they are each on a line of their own, like all other kernel-doc comments:

.. kernel-doc::  ./all-in-a-tumble.h
    :snippets:  my_long_struct
    :language:  c
    :linenos:

Rendered example: :ref:`example.my_long_struct`


.. _kernel-doc-syntax-enums-typedefs:

enums, typedefs
===============

To write documentation for enums and typedefs, you must write the name of the
declaration; the ``enum`` or ``typedef`` must always precede the name.

.. kernel-doc::  ./all-in-a-tumble.h
    :snippets:  my_enum
    :language:  c
    :linenos:

Rendered example: :ref:`example.my_enum`

.. kernel-doc::  ./all-in-a-tumble.h
    :snippets:  my_typedef
    :language:  c
    :linenos:

Rendered example: :ref:`example.my_typedef`


.. _kernel-doc-syntax-doc:

documentation blocks
====================

To facilitate having source code and comments close together, you can include
kernel-doc documentation blocks that are *free-form* comments instead of being
kernel-doc for functions, structures, unions, enumerations, or typedefs.  This
could be used for something like a theory of operation for a driver or library
code, for example.

This is done by using a ``DOC:`` section keyword with a section title. A small
example:

.. kernel-doc::  ./all-in-a-tumble.h
    :snippets:  theory-of-operation
    :language:  c
    :linenos:

Rendered example: :ref:`example.theory-of-operation`

.. _kernel-doc-highlights:

highlight pattern
=================

All kernel-doc markup is processed as described above, all descriptive text is
further processed, scanning for the following special patterns, which are
highlighted appropriately.

- ``user_function()`` : function
- ``@a`` : name of a parameter
- ``&struct my_struct`` : name of a structure (including the word struct)
- ``&union my_union`` : name of a union
- ``&my_struct->a`` or ``&my_struct.b`` -  member of a struct or union.
- ``&enum my_enum`` : name of a enum
- ``&typedef my_typedef`` : name of a typedef
- ``%CONST`` : name of a constant.
- ``$ENVVAR`` : environmental variable

The kernel-doc parser translates the pattern above to the corresponding reST_
markups (`sphinx domains`_)::

  - :c:func:`user_function` : function
  - ``a`` : name of a parameter
  - :c:type:`struct my_struct <my_struct>` : name of a structure (including the word struct)
  - :c:type:`union my_union <my_union>` : name of a union
  - :c:type:`my_struct->a <my_struct>` or :c:type:`my_struct.b <my_struct>` -  member of a struct or union.
  - :c:type:`enum my_enum <my_enum>` : name of a enum
  - :c:type:`typedef my_typedef <my_typedef>` : name of a typedef
  - ``CONST`` : name of a constant.
  - ``$ENVVAR`` : environmental variable

The `sphinx-doc`_ generator highlights these markups and tries to cross
referencing to arbitrary locations (`sphinx cross references`_). The result of a
cross reference depends on the context of the document which includes the
kernel-doc comment. You don't have to use the *highlight* pattern, if you prefer
*pure* reST, use the reST markup.

Since the prefixes ``$...``, ``&...`` and ``@...`` are used to markup the
highlight pattern, you have to escape them in other uses: ``\$...``, ``\&...``
and ``\@...``.

.. hint::

  The highlight pattern, are non regular reST markups. They are only available
  within kernel-doc comments, helping C developers to write short and compact
  documentation in source code comments. You can't use them in plain reST files
  (".rst"). If you are editing ".rst" files (e.g. files under ``Documentation``)
  please use the corresponding reST_ markups (`sphinx domains`_).


.. _kernel-doc-syntax-snippets:

Snippets
========

The kernel-doc Parser supports a comment-markup for snippets out of the source
code. To start a region to snip insert::

  /* parse-SNIP: <snippet-name> */

The snippet region stops with a new snippet region or at the next::

  /* parse-SNAP: */

Jump to :ref:`kernel-doc-snippets` to see an example.
