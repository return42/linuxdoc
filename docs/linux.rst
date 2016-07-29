.. -*- coding: utf-8; mode: rst -*-

.. include:: refs.txt

==========================
Linux Kernel Documentation
==========================

Starting with Linux Kernel v4.8 a `sphinx-doc`_ build is available to build
formats like HTML from reStructuredText (`reST`_) markup. E.g. with::

  make IGNORE_DOCBOOKS=1 htmldocs

the sphinx build produce a HTML representation of the reST files *in and below*
the ``Documentation/`` folder. The sphinx extensions for this build, which are
shipped by the kernel source tree, are placed in the ``Documentation/sphinx``
folder.  If you like to see how (fast) the *linuxdoc* extensions build your
kernel documentation, install *linuxdoc* and replace the extensions in the
conf.py. In more detail ...::

  pip install [--user] git+http://github.com/return42/linuxdoc.git

and add the following patch to the linux source tree:

* :download:`linux docs-next patch <downloads/patch_linux.patch>`

In the ``conf.py`` (`sphinx config`_), the patch deactivates the sphinx
extensions from the kernel source tree and activates linuxdoc sphinx
extensions. At this time (in Jul 2016) there is also a dump "man_pages" setup
which must be disabled.

.. code-block:: diff

    --- a/Documentation/conf.py
    +++ b/Documentation/conf.py
    @@ -18,7 +18,7 @@ import os
     # If extensions (or modules to document with autodoc) are in another directory,
     # add these directories to sys.path here. If the directory is relative to the
     # documentation root, use os.path.abspath to make it absolute, like shown here.
    -sys.path.insert(0, os.path.abspath('sphinx'))
    +#sys.path.insert(0, os.path.abspath('sphinx'))

     # -- General configuration ------------------------------------------------

    @@ -28,7 +28,12 @@ sys.path.insert(0, os.path.abspath('sphinx'))
     # Add any Sphinx extension module names here, as strings. They can be
     # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
     # ones.
    -extensions = ['kernel-doc', 'rstFlatTable', 'kernel_include']
    +extensions = [
    +    'linuxdoc.rstKernelDoc'
    +    , 'linuxdoc.rstFlatTable'
    +    , 'linuxdoc.kernel_include'
    +    , 'linuxdoc.manKernelDoc'
    +    , 'sphinx.ext.todo' ]

     # Gracefully handle missing rst2pdf.
     try:
    @@ -128,7 +133,7 @@ pygments_style = 'sphinx'
     #keep_warnings = False

     # If true, `todo` and `todoList` produce output, else they produce nothing.
    -todo_include_todos = False
    +todo_include_todos = True

     primary_domain = 'C'
     highlight_language = 'C'
    @@ -297,10 +302,7 @@ latex_documents = [

     # One entry per manual page. List of tuples
     # (source start file, name, description, authors, manual section).
    -man_pages = [
    -    (master_doc, 'thelinuxkernel', 'The Linux Kernel Documentation',
    -     [author], 1)
    -]
    +man_pages = []

     # If true, show URL addresses after external links.
     #man_show_urls = False
    @@ -417,5 +419,6 @@ pdf_documents = [
     # kernel-doc extension configuration for running Sphinx directly (e.g. by Read
     # the Docs). In a normal build, these are supplied from the Makefile via command
     # line arguments.
    -kerneldoc_bin = '../scripts/kernel-doc'
    -kerneldoc_srctree = '..'
    +kernel_doc_verbose_warn = False
    +kernel_doc_raise_error = False
    +kernel_doc_mode = "reST"

In the ``index.rst``, the patch adds a list of TODO entries with kernel-doc
*Oops*. A *Oops* entrie is generated when the kernel-doc parser can't parse
requested documentation. For more details see:
:ref:`kernel-doc:kernel-doc-directive`.

.. code-block:: diff

    --- a/Documentation/index.rst
    +++ b/Documentation/index.rst
    @@ -6,6 +6,8 @@
     Welcome to The Linux Kernel's documentation!
     ============================================

    +.. todolist::
    +
     Nothing for you to see here *yet*. Please move along.

In the ``Makefile.sphinx``, the patch adds a target to build man pages from
kernel-doc comments.

.. code-block:: diff

    diff --git a/Documentation/Makefile.sphinx b/Documentation/Makefile.sphinx
    index fd565e1..ef164d7 100644
    --- a/Documentation/Makefile.sphinx
    +++ b/Documentation/Makefile.sphinx
    @@ -61,7 +61,11 @@ xmldocs:
     # no-ops for the Sphinx toolchain
     sgmldocs:
     psdocs:
    +
     mandocs:
    +        $(MAKE) BUILDDIR=$(BUILDDIR) -f $(srctree)/Documentation/media/Makefile htmldocs
    +	     $(call cmd,sphinx,kernel-doc-man)
    +
     installmandocs:
     cleanmediadocs:


.. _create-manpages:

Create man pages
================

To get man pages from kernel-doc comments add the ``:man-sect:`` option to your
kernel-doc directives, e,g.

.. code-block:: rst

    .. kernel-doc:: drivers/media/dvb-core/dvb_math.h
       :man-sect: 9

To create man pages call the mandocs target::

    make IGNORE_DOCBOOKS=1 mandocs

