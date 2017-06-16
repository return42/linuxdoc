.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _kernel-doc-intro:

=======================
kernel-doc introduction
=======================

In order to embed **"C" friendly** and extractable documentation into C/C++
source code comments, the Kernel community adopted a consistent style for
documentation comments. The markup for this documentation is called the
**kernel-doc format**.  This style embeds the documentation within the source
files, using a few simple conventions for adding documentation paragraphs and
documenting functions and their parameters, structures and unions and their
members, enumerations, and typedefs.

.. note::

   The kernel-doc format is deceptively similar to Doxygen, javadoc or `Sphinx's
   autodoc`_ which grabs for comments in `Sphinx's Python domain`_.  The kernel-doc
   format has a long tradition, e.g. its also well highlighted in your emacs ;)

If you are familiar with Sphinx, you might know about `Sphinx's C domain`_
markup. Compared with the kernel-doc markup is less verbose, more **"C"
friendly** and there exists a kernel-doc parser. The kernel-doc parser grabs the
documentation from your C sources and generates proper reST, which contain
markup of `Sphinx's C domain`_. The descriptions are filtered for special
kernel-doc highlights and cross-references.

The opening comment mark ``/**`` is reserved for kernel-doc comments.  Only
comments so marked will be considered by the kernel-doc tools, and any comment
so marked must be in kernel-doc format.  The closing comment marker for
kernel-doc comments can be either ``*/`` or ``**/``, but ``*/`` is preferred in
the Linux kernel tree.  The lines in between should be prefixed by `` * ``
(space star space).

Example kernel-doc function comment:

.. code-block:: c

   /**
    * foobar() - short function description of foobar
    *
    * @arg1: Describe the first argument to foobar.
    * @arg2: Describe the second argument to foobar.
    *        One can provide multiple line descriptions
    *        for arguments.
    *
    * A longer description, with more discussion of the function foobar()
    * that might be useful to those using or modifying it.  Begins with
    * empty comment line, and may include additional embedded empty
    * comment lines.
    *
    * The longer description can have multiple paragraphs.
    *
    * Return:
    * Describe the return value of foobar.
    */
   int foobar(int arg1, int arg2);

Compare this example with the reST needed by Sphinx (see below) and produced by
the kernel-doc parser and you will see why kernel-doc markup is much more **C
friendly**.

.. code-block:: rst

  .. _`foobar`:

  foobar
  ======

  .. c:function:: int foobar(int arg1, int arg2)

      short function description of foobar

      :param int arg1:
          Describe the first argument to foobar.

      :param int arg2:
          Describe the second argument to foobar.
          One can provide multiple line descriptions
          for arguments.

  .. _`foobar.description`:

  Description
  -----------

  A longer description, with more discussion of the function :c:func:`foobar`
  that might be useful to those using or modifying it.  Begins with empty
  comment line, and may include additional embedded empty comment lines. Within
  you can refer other definitions (names like :c:type:`struct foos_struct
  <foos_struct>` or  :c:type:`struct bars_typedef <bars_typedef>`).

  The longer description can have multiple paragraphs.

  .. _`foobar.return`:

  Return
  ------

  Describe the return value of foobar.

