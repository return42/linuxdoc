.. -*- coding: utf-8; mode: rst -*-

.. include:: refs.txt

==========================
Linux Kernel Documentation
==========================

Starting with Linux Kernel v4.8 a `sphinx-doc`_ build is available to build
formats like HTML from reStructuredText (`reST`_) markup. E.g. with::

  make DOCBOOKS= htmldocs

the sphinx build produce a HTML representation of the reST files *in and below*
the ``Documentation/`` folder. The sphinx extensions for this build, which are
shipped by the kernel source tree, are placed in the ``Documentation/sphinx``
folder.

If you like to see how (and how fast) the *linuxdoc* extensions build your
kernel documentation, install *linuxdoc* and replace the extensions in the
``conf.py``.

.. hint::

   From the user's scope of view, most of the extensions work like the one from
   the kernel source tree. Mainly the ``kernel-doc`` extension from source tree
   is replaced by the ``rstKernelDoc`` extension.

   The ``rstKernelDoc`` replacement is a *superset* with additional options
   :ref:`[ref] <kernel-doc:kernel-doc-directive>`. The ``rstKernelDoc``
   extension uses a the kernel-doc parser from the *linuxdoc* project.  Compared
   to the kernel-doc Perl script from the kernel's source tree, especially the
   sectioning of the reST output is different and the ERROR/WARNING log is more
   strict/verbose - take this in mind!

To get *linuxdoc* into your kernel-build install it::

  pip install [--user] git+http://github.com/return42/linuxdoc.git

and add the following patch to the Linux source tree:

* :download:`linux docs-next patch <downloads/patch_linux.patch>` e.g::

    $ cd /folder/with/linux-docs-next
    $ git apply /download/folder/patch_linux.patch

.. hint::

   ATM the linux documentation build is heavily WIP, with hope the patch above
   should fit on Jon's doc-next (see DOCUMENTATION at MAINTAINERS-file)::

     git://git.lwn.net/linux.git docs-next

   If the patch file won't work for you, below you will find the description of
   the patch, so you should be able to patch your kernel build files manually.


Patch linux Documentation build
===============================

In the ``Makefile.sphinx``, the patch adds a target to build man pages from
kernel-doc comments. For building man pages the ``kernel-doc-man`` builder from
the *linuxdoc* project is used (part of ``linuxdoc.manKernelDoc``), but be
aware: for creating man pages, you have to define the content for, read section
:ref:`create-manpages`.

The ``KERNELDOC_CONF`` is droped, since it is not needed by *linuxdoc*.

.. code-block:: diff

   --- a/Documentation/Makefile.sphinx
   +++ b/Documentation/Makefile.sphinx
   @@ -35,8 +35,7 @@ HAVE_PDFLATEX := $(shell if which xelatex >/dev/null 2>&1; then echo 1; else ech
    PAPEROPT_a4     = -D latex_paper_size=a4
    PAPEROPT_letter = -D latex_paper_size=letter
    KERNELDOC       = $(srctree)/scripts/kernel-doc
   -KERNELDOC_CONF  = -D kerneldoc_srctree=$(srctree) -D kerneldoc_bin=$(KERNELDOC)
   -ALLSPHINXOPTS   =  $(KERNELDOC_CONF) $(PAPEROPT_$(PAPER)) $(SPHINXOPTS)
   +ALLSPHINXOPTS   =  $(PAPEROPT_$(PAPER)) $(SPHINXOPTS)
    # the i18n builder cannot share the environment and doctrees with the others
    I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) .

   @@ -88,9 +87,11 @@ xmldocs:
    # no-ops for the Sphinx toolchain
    sgmldocs:
    psdocs:
   -mandocs:
    installmandocs:

   +mandocs:
   +	@$(foreach var,$(SPHINXDIRS),$(call loop_cmd,sphinx,kernel-doc-man,$(var),man,$(var)))
   +


In the ``conf.py`` (`sphinx config`_), the patch deactivates the sphinx
extensions from the kernel source tree and activates *linuxdoc* sphinx
extensions. At this time (in Sept. 2016) there is also a dump "man_pages" setup
which must be disabled.

.. code-block:: diff

   diff --git a/Documentation/conf.py b/Documentation/conf.py
   index 46e69db..9e457b6 100644
   --- a/Documentation/conf.py
   +++ b/Documentation/conf.py
   @@ -34,7 +34,13 @@ from load_config import loadConfig
    # Add any Sphinx extension module names here, as strings. They can be
    # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
    # ones.
   -extensions = ['kernel-doc', 'rstFlatTable', 'kernel_include', 'cdomain']
   +extensions = [
   +    'linuxdoc.rstKernelDoc'
   +    , 'linuxdoc.rstFlatTable'
   +    , 'linuxdoc.kernel_include'
   +    , 'linuxdoc.manKernelDoc'
   +    , 'linuxdoc.cdomain'
   +    , 'sphinx.ext.todo' ]

    # The name of the math extension changed on Sphinx 1.4
    if minor > 3:
   @@ -133,7 +139,7 @@ pygments_style = 'sphinx'
    #keep_warnings = False

    # If true, `todo` and `todoList` produce output, else they produce nothing.
   -todo_include_todos = False
   +todo_include_todos = True

    primary_domain = 'C'
    highlight_language = 'guess'
   @@ -367,10 +373,7 @@ latex_documents = [

    # One entry per manual page. List of tuples
    # (source start file, name, description, authors, manual section).
   -man_pages = [
   -    (master_doc, 'thelinuxkernel', 'The Linux Kernel Documentation',
   -     [author], 1)
   -]
   +man_pages = []

    # If true, show URL addresses after external links.
    #man_show_urls = False
   @@ -487,8 +490,9 @@ pdf_documents = [
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
requested documentation. For more details see *kernel-doc-HOWTO* at :ref:`[ref]
<kernel-doc:kernel-doc-directive>`.

.. code-block:: diff

   --- a/Documentation/index.rst
   +++ b/Documentation/index.rst
   @@ -21,3 +21,7 @@ Indices and tables
    ==================

    * :ref:`genindex`
   +
   +
   +.. todolist::
   +

Build the HTML documentation::

  make DOCBOOKS= htmldocs

and scroll to the bottom of the ``index.html``, there you will find the TODO
entries generated by *Oops*.  If you want to add this *Oops* feature to your
sub-folder build, add the following to your sub-folder's index file
(e.g. ``media/index.rst``).

.. code-block:: rst

   .. only::  subproject

      .. todolist::

Build HTML of your sub-folder (e.g. media)::

    make SPHINXDIRS=media htmldocs

If kernel-doc get some *Oops* for your sub-folder, you will find them in the
bottom of your ``index.html`` file.

.. _create-manpages:

Create man pages
================

To get man pages from kernel-doc comments, add the ``:man-sect:`` option to your
kernel-doc directives. E.g. to build all man pages of the media's remote control
(file ``media/kapi/rc-core.rst``) add ``:man-sect: 9`` to all the kernel-doc
includes.

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

To create man pages call the mandocs target::

    make DOCBOOKS= mandocs

or alternatively compile only the sub-folder::

    make SPHINXDIRS=media mandocs

