.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _reST-kernel-doc-mode:

====================
reST kernel-doc mode
====================

To distinguish between the vintage markup and the new markup (with reST in), it
is recommended to add the following comment at the top of your source code
file.::

    /* parse-markup: reST */

This forces the kernel-doc parser to switch into the reST mode, no matter in
which context the parser runs (see :ref:`vintage-kernel-doc-mode`).

.. _reST-section-structure:

reST section structure
======================

Since a section title in reST mode needs a line break after the colon, the colon
handling is less ugly (:ref:`vintage-mode-quirks`).  E.g.::

    prints out: hello world

is rendered as expected in one line. If non text follows the colon, a section is
inserted.  To avoid sectioning in any case, place a space in front of the
column.::

   lorem list :

   * lorem
   * ipsum

On the opposite, super-short sections from :ref:`vintage-kernel-doc-mode` like::

    Section name: lorem ipsum

are no longer supported, you have to enter at least one line break::

    Section name:
    lorem ipsum

There is an exception for special section names like "Description:", "Context:"
or "Return:", which exists mainly for backward compatibility. Nevertheless, it
is recommended to add a newline after the colon.

Beside these *sectioning* of the kernel-doc syntax, reST_ has it's own chapter,
section etc. markup (e.g. see `Sections
<http://www.sphinx-doc.org/en/stable/rest.html#sections>`_).  Normally, there
are no heading levels assigned to certain characters as the structure is
determined from the succession of headings. However, there is a common
convention, which is used by the kernel-doc parser also:

* ``#`` with over-line, for parts
* ``*`` with over-line, for chapters
* ``=`` for sections
* ``-`` for subsections
* ``^`` for sub-subsections
* ``"`` for paragraphs

Within kernel-doc comments you should use this sectioning with care.  A
kernel-doc section like the ``Return:`` section above is translated into a reST_
sub-section with the following markup.

.. code-block:: rst

    Return
    ------

    sum of a and b

As you see, a kernel-doc section is a reST_ *subsection* level. This means, you
can only use the following *sub-levels* within a kernel-doc section.

* ``^`` for sub-subsections
* ``"`` for paragraphs

In contrast to subsections like "Return:", a "DOC:" section has no subsection,
thats why reST *sub-levels* in "DOC:" sections start a the subsection level,
tagged with a minus:

* ``-`` for subsections
* ``^`` for sub-subsections
* ``"`` for paragraphs

Need an detailed example of kernel-doc comment using subsections and more?  Take
a look here ...

.. kernel-doc::  ./all-in-a-tumble.h
   :snippets:  rst_mode

.. admonition:: reST markup in kernel-doc comments
   :class: rst-example

   .. kernel-doc::  ./all-in-a-tumble.h
      :functions:  rst_mode
