.. -*- coding: utf-8; mode: rst -*-
.. include:: linuxdoc-howto/refs.txt

.. _kernel-doc-intro:

=======================
kernel-doc introduction
=======================

In order to embed **"C" friendly** and extractable documentation into C/C++
source code comments, the Kernel community adopted a consistent style for
documentation comments.  The markup for this documentation is called the
**kernel-doc markup**.  This style embeds the documentation within the source
files, using a few simple conventions for adding documentation paragraphs and
documenting functions and their parameters, structures, unions and their
members, enumerations, and typedefs.  It also includes lightweight markups for
highlights and cross-references in your source code.

The kernel-doc format is deceptively similar to Doxygen, javadoc or `Sphinx's
autodoc`_ which grabs for comments in `Sphinx's Python domain`_.  The kernel-doc
format has a long tradition, e.g. its also well highlighted in your emacs ;) If
you are familiar with Sphinx_, you might know about `Sphinx's C domain`_ markup.

.. note::

   - Compared `Sphinx's C domain`_, the :ref:`kernel-doc-syntax` is less verbose
     and much more coder friendly (:ref:`kernel-doc comment
     <kernel-doc-intro-example>` and :ref:`reST <kernel-doc-intro-example-out>`).

   - The opening comment mark ``/**`` is reserved for kernel-doc comments.

The **kernel-doc parser** of the LinuxDoc package grabs the documentation from
your C sources and translates the **kernel-doc markup** into proper reST_.  From
coder's POV, the C-friendly kernel-doc markup is translated into the more
verbosely `Sphinx's C domain`_ which can be included at any place in the
documentation.

Only comments so marked will be considered by the kernel-doc tools, and any
comment so marked must be in kernel-doc format.  The closing comment marker for
kernel-doc comments can be either ``*/`` or ``**/``, but ``*/`` is preferred in
the Linux kernel tree.  The lines in between should be prefixed by `` * ``
(space star space).

.. _kernel-doc-intro-example:

by example
==========

Lets start with a simple example, documenting our elaborate *foobar* function.

.. code-block:: c

    /**
     * foobar() - short function description of foobar
     *
     * @arg1: Describe the first argument to foobar.
     * @arg2: Describe the second argument to foobar.  One can provide multiple line
     *        descriptions for arguments.
     *
     * A longer description, with more discussion of the function foobar() that
     * might be useful to those using or modifying it.  Begins with empty comment
     * line and may include additional embedded empty comment lines.  Within, you
     * can refer other definitions (e.g. &struct my_struct, &typedef my_typedef,
     * %CONSTANT, $ENVVAR etc.).
     *
     * The longer description can have multiple paragraphs and you can use reST
     * inline markups like *emphasise* and **emphasis strong**.  You also have reST
     * block markups like lists or literal available:
     *
     * Ordered List:
     * - item one
     * - item two
     * - literal block::
     *
     *      a + b --> x
     *
     * Return:
     * Describe the return value of foobar.
     */
    int foobar(int arg1, int arg2);

Pause here and recap what we have seen in the example above.  It is a mix-up of
kernel-doc markup and reST_ markup.  Markups like the function description in
the first line and the following argument descriptions are covered by the
kernel-doc markup, while other markups like the ordered list, the literal block
or the inline emphasis are all a part of the reST_ markup.  The combination of
these markups enables us to write compact (*"C" friendly*) documentation within
the source code.

From coder's point, we made a great job documenting our ``foorbar()`` function.
Now lets take the POV of an author who like to use this description in his
detailed API documentation.  This is where the :ref:`kernel-doc directive
<kernel-doc-directive>` comes in use.  To include the ``foobar()`` description,
which might be located in file ``include/foobar.h``, the author can use the
kernel-doc directive like this:

.. code-block:: rst

    .. kernel-doc:: include/foobar.h
        :functions: foobar

Now, if the documentation build process takes places, the kernel-doc directive
runs the **kernel-doc parser** which grabs the documentation and translates the
**kernel-doc markup** into proper reST_.  Within the output, the directive is
replaced by the generated reST_.  Later we will see some rendered examples, here
to complete the example lets take a look at the generated doctree, printed out
in reST_ format:

.. _kernel-doc-intro-example-out:

.. code-block:: rst

    .. _`foobar`:

    foobar
    ======

    .. c:function:: int foobar(int arg1, int arg2)

	short function description of foobar

	:param int arg1:
	    Describe the first argument to foobar.

	:param int arg2:
	    Describe the second argument to foobar.  One can provide multiple line
	    descriptions for arguments.

    .. _`foobar.description`:

    Description
    -----------

    A longer description, with more discussion of the function :c:func:`foobar`
    that might be useful to those using or modifying it.  Begins with empty
    comment line, and may include additional embedded empty comment lines.
    Within you can refer other definitions (e.g. :c:type:`struct my_struct
    <my_struct>`, :c:type:`typedef my_typedef <my_typedef>`, ``CONSTANT``,
    ``$ENVVAR`` etc.).

    The longer description can have multiple paragraphs and you can use reST
    inline markups like *emphasise* and **emphasis strong**.  You also have reST

    .. _`foobar.ordered-list`:

    Ordered List
    ------------


    - item one
    - item two
    - literal block::

	 a + b --> x

    .. _`foobar.return`:

    Return
    ------

    Describe the return value of foobar.


Compare this reST with the kernel-doc comment from the beginning.  This reST is
what you have to type if do not have kernel-doc markups, isn't it coder
friendly?  If you look closer, you will also see that there is a subsection
named *Ordered List*.  Be not surprised, this subsection is also made by a
kernel-doc markup, read on in the the :ref:`kernel-doc-syntax` chapter for a
detailed description of the markup.

So far we have hyped the kernel-doc, to be complete we also have to look what
the drawbacks and restrictions are.  In your daily work you won’t discover any
huge drawback, but you will be aware of some restrictions. These are given by
the fact, that in some circumstances the mix of the very condensed kernel-doc
markup and the reST markup will bite each other.  There you will need some
quotes (``\``) to escape, that might partial cutting your joy in kernel-doc.
Anyway, overall you should be able to recognize the daily benefit of using
kernel-doc markup in your projects.

LinuxDoc feature overview
=========================

kernel-doc
  A "C" friendly markup, the parser, the Sphinx-doc extension and some tools.
  The kernel-doc markup embeds documentation within the C source files, using a
  few simple conventions. The parser grabs the documentation from source and
  generates proper reST :ref:`[ref] <kernel-doc-intro>`.  The parser is written
  in Python and its API is used by the corresponding Sphinx-doc extension.
  Command line tools shipped with:

  - kernel-autodoc: Suitable for automatic API documentation :ref:`[ref]
    <kernel-autodoc>`.

  - kernel-lintdoc: *Lint* kernel-doc comments from source code :ref:`[ref]
    <kernel-lintdoc>`.

  - kernel-doc: A command line interface for kernel-doc's parser API :ref:`[ref]
    <kernel-doc-cmd>`.

kernel-doc-man
  A man page builder. An extension/replacement of the common Sphinx-doc *man*
  builder also integrated in the kernel-doc Sphinx-doc extension :ref:`[ref]
  <man-pages>`.

flat-table
  A diff and author friendly list-table replacement with *column-span*,
  *row-span* and *auto-span* :ref:`[ref] <rest-flat-table>`.

cdomain
  A customized `Sphinx's C Domain`_ extension. Suitable for demanding projects
  :ref:`[ref] <customized-c-domain>`.

kfigure
  Sphinx extension which implements scalable image handling. Simplifies image
  handling from the author's POV. Wins where Sphinx-doc image handling
  fails. Whatever graphic tools available on your build host, you always get the
  best output-format. Graphviz's DOT format included :ref:`[ref] <kfigure>`.

kernel-include
  A replacement for the ``include`` reST directive. The directive expand
  environment variables in the path name and allows to include files from
  arbitrary locations ref:`[ref] <kernel-include-directive>`.

