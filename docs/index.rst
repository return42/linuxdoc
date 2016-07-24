.. -*- coding: utf-8; mode: rst -*-

========
LinuxDoc
========

.. automodule:: linuxdoc
    :members:
    :undoc-members:
    :show-inheritance:

* documentation: http://return42.github.io/linuxdoc
* reposetory:    `github return42/fspath <https://github.com/return42/linuxdoc>`_
* Author e-mail: *markus.heiser*\ *@*\ *darmarIT.de*

Installing
==========

Install bleading edge::

  pip install [--user] git+http://github.com/return42/linuxdoc.git

Update regualar with::

  pip install --upgrade git+http://github.com/return42/linuxdoc.git

If you are a developer, fork on github or clone and install::

  git clone https://github.com/return42/linuxdoc
  cd linuxdoc
  make install


Linux Kernel Documentation
==========================

In the 4.8 kernel and beyond a sphinx-doc build is available, if you like to see
how (fast) *linuxdoc* builds your kernel documentation, add the following patch
to the ``conf.py``. The patch deactivates the sphinx extensions from the kernel
source tree and activates linuxdoc sphinx extensions. Currently (Jul 2016) there
is a dump "man_pages" setting wich has to be deactivated.

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

The next patch adds a list of TODO entries with kernel-doc *Oops*. The *Oops*
entries are generated if the kernel-doc parser can't generate requested
documentation. For more details see: :ref:`kernel-doc:kernel-doc-directive`.

.. code-block:: diff

    --- a/Documentation/index.rst
    +++ b/Documentation/index.rst
    @@ -6,6 +6,8 @@
     Welcome to The Linux Kernel's documentation!
     ============================================

    +.. todolist::
    +
     Nothing for you to see here *yet*. Please move along.

To get in use of kernel-doc-man pages, apply the following diff to the
Makefile.sphinx.

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
    +	$(MAKE) BUILDDIR=$(BUILDDIR) -f $(srctree)/Documentation/media/Makefile htmldocs
    +	$(call cmd,sphinx,kernel-doc-man)
    +
     installmandocs:
     cleanmediadocs:

To get man pages from kernel-doc comments add the ``:man-sect:`` option to your
kernel-doc directive::

    .. kernel-doc:: drivers/media/dvb-core/dvb_math.h
       :man-sect: 9


Source Code Documentation
=========================

.. toctree::
   :maxdepth: 2

   linuxdoc/linuxdoc


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
