.. -*- coding: utf-8; mode: rst -*-

.. include:: refs.txt

.. _patch-linux-kernel:

================================
Patch Linux Kernel Documentation
================================

Starting with Linux Kernel v4.8 a `sphinx-doc`_ build is available to build
formats like HTML from reStructuredText (`reST`_) markup. E.g. with ``make
SPHINXDIRS="driver-api" htmldocs`` the HTML of *The Linux driver implementer's
API guide* is build.  The sphinx extensions for this build, which are shipped by
the kernel source tree, are placed in the ``Documentation/sphinx`` folder.

If you like to see how the LinuxDoc extensions build your kernel documentation
(HTML, man, ...) install LinuxDoc and replace the extensions in the
``conf.py``.

.. hint::

   From the user's scope of view, most of the extensions work like the one from
   the kernel source tree. Mainly the ``kernel-doc`` extension from source tree
   is replaced by the ``rstKernelDoc`` Sphinx extension and a *man page* builder
   is added.  The ``rstKernelDoc`` replacement is a *superset* with additional
   options :ref:`[ref] <kernel-doc-directive>`. The ``rstKernelDoc`` extension
   uses a the kernel-doc parser from the LinuxDoc project.  Compared to the
   kernel-doc parser from the kernel's source tree (written in Perl), especially
   the sectioning of the reST output is different and the ERROR/WARNING log is
   more strict/verbose.

To get LinuxDoc into your kernel-build install it::

  pip install --user git+http://github.com/return42/linuxdoc.git

and add the following patch to the Linux source tree:

* :download:`linux docs-next patch <downloads/patch_linux.patch>` e.g::

    $ cd /folder/with/linux-docs-next
    $ git apply /download/folder/patch_linux.patch

ATM the linux documentation build is heavily WIP, with hope the patch above
should fit on Jon's docs-next (see DOCUMENTATION at MAINTAINERS-file)::

  git://git.lwn.net/linux.git docs-next

Its also recommended to install a sticky Sphinx version::

  pip install --user Sphinx==1.5.6

With the patched kernel sources, you are able to build the HTML and man
pages. E.g. build *The Linux driver implementer's API guide* with::

  make SPHINXDIRS="driver-api" htmldocs mandocs

ATM the PDF build is fragile and mostly broken. Both, the *linux kernel
documentation* and the LinuxDoc have problems to build PDF. If you give it a
try use target ``pdfdocs``.

The build shows much more log messages, particularly the *kernel-doc* parser is
more strict and spits out a lot of warnings and errors to improve your
kernel-doc comments in the source code.

A *Oops* entrie is inserted in the output (e.g. HTML) when the kernel-doc parser
can't parse requested documentation. For more details see
``kernel_doc_raise_error`` in the :ref:`kernel-doc-config`. If you want to
refer all *Oops* messages in front of the document add the *todolist* directive
to your ``index.rst`` file. E.g. for driver-api:

.. code-block:: diff

   diff --git a/Documentation/driver-api/index.rst b/Documentation/driver-api/index.rst
   index 3cf1ace..5aa6f87 100644
   --- a/Documentation/driver-api/index.rst
   +++ b/Documentation/driver-api/index.rst
   @@ -51,3 +51,5 @@ available subsections can be seen below.
       =======

       * :ref:`genindex`
   +
   +   .. todolist::
