.. -*- coding: utf-8; mode: rst -*-

.. include:: refs.txt

.. _patch-linux-kernel:

================================
Patch Linux Kernel Documentation
================================

.. sidebar::  update 2020-08

   This article left here for historical reasons.

   (TL;DR) Now we have kernel v5.9 and something in kernel's doc-build chain has
   been changed.  The LinuxDoc project is **no longer a drop-in replacement for
   the sphinx-doc build chain of the linux Kernel.**

The LinuxDoc project is a drop-in replacement for the sphinx-doc build chain of
the linux Kernel (see :ref:`kernel_dev_remarks`).  If you like to see how the
LinuxDoc extensions build your kernel documentation (HTML, man, ...) install
LinuxDoc and replace the extensions in the ``conf.py``.  Here is the patch:

* :download:`linux patch <downloads/patch_linux.patch>`

You might need a virtualenv to install LinuxDoc.  If this is all to much for
you, just clone LinuxDoc and work like a developer will do.  Here is what we
recommend:

1. jump to a folder we can use and clone LinuxDoc. If not already done, clone
   Kernel's sources also::

     $ cd ~/Downloads
     $ git clone https://github.com/return42/linuxdoc.git
     $ git clone git://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git

2. Patch Kernel's sources.  The variable ``srctree`` points to Kernel's sources
   and is optional, its default is ``../linux``::

     $ cd linuxdoc
     $ make srctree=../linux patch_linux

3. build the virtualenv in ``local/py3``::

     $ make pyenv-install
       PYENV     local/py3
       ACTIVATE  source ./local/py3/bin/activate

4. To use sphinx-build from virtualenv, activate it::

     $ source local/py3/bin/activate
     (py3) $

   Within the virtualenv you see a ``(py3)`` in bash's prompt.  Now lets look
   what ``sphinx-build`` command will be used within this environment::

     (py3) $ which sphinx-build
     /home/user/Downloads/linuxdoc/local/py3/bin/sphinx-build

With the ``(py3)`` environment we build Kernel's Makefile targets::

  (py3) $ cd ../linux
  (py3) $ make SPHINXOPTS="-j auto" htmldocs mandocs

To speed up build, we used a ``sphinx-build`` option ``-j`` to build in parallel
with N processes where possible (see `man sphinx-build
<http://www.sphinx-doc.org/en/1.5.1/man/sphinx-build.html#options>`_).


Discussion
==========

Even if LinuxDoc is a drop-in replacement, the result is not the same.  Not in
performance manner nor in the produced output.  Lets discuss this various
aspects.

.. hint::

   From the user's scope of view, most of the extensions work like the one from
   the kernel source tree.  Mainly the ``kernel-doc`` extension from source tree
   is replaced by the ``rstKernelDoc`` Sphinx extension and a *man page* builder
   is added.  The ``rstKernelDoc`` replacement is a *superset* with additional
   options :ref:`[ref] <kernel-doc-directive>`.  The ``rstKernelDoc`` extension
   uses a the kernel-doc parser from the LinuxDoc project.  Compared to the
   kernel-doc parser from the kernel's source tree (written in Perl), especially
   the sectioning of the reST output is different and the ERROR/WARNING log is
   more strict/verbose.

Some comments about the build:

- ATM the PDF build is fragile and mostly broken. Both, the *linux kernel
  documentation* and the LinuxDoc have problems to build PDF.  If you give it a
  try use target ``pdfdocs``.

- The build shows much more log messages, particularly the *kernel-doc* parser
  is more strict and spits out a lot of warnings and errors to improve your
  kernel-doc comments in the source code.

