.. -*- coding: utf-8; mode: rst -*-

.. include:: refs.txt

.. _kernel_dev_remarks:

============================
Remarks for Kernel developer
============================

.. sidebar::  update 2020-08

   This article left here for historical reasons.

   (TL;DR) Now we have kernel v5.9 and something in kernel's doc-build chain has
   been changed.

Starting with Linux Kernel v4.8 a `sphinx-doc`_ build is available to build
formats like HTML from reStructuredText (`reST`_) markup.  The Makefile target
``htmldocs`` builds the HTML documentation::

  make htmldocs

The sphinx extensions for this build, which are shipped by the kernel source
tree, are placed in the ``Documentation/sphinx`` folder.  Some of the LinuxDoc
features are already a part of the Kernel's ``Documentation/sphinx`` folder
others not (yet).  E.g. the sphinx-doc_ extensions :ref:`rest-flat-table`,
:ref:`cdomain <customized-c-domain>`, :ref:`kfigure <kfigure>` and
:ref:`kernel-include <kernel-include-directive>` are merged into Kernel's source
tree.  On the other side, e.g. for parsing kernel-doc comments, the Linux Kernel
build process uses a Perl script while LinuxDoc brings a python module with a
kernel-doc parser.

One drawback of the Perl script is, that it fits not very well into
sphinx-extensions_ which are normally written in python.  As a stand-alone
parser it might be good enough, but mostly the parser is driven by the
:ref:`kernel-doc directive <kernel-doc-directive>` and this can't be done
in-process when you need a separate process for the Perl interpreter.  The only
thing that such a parser can do, is to pipe its results to ``stdout``, which can
be read by the kernel-doc directive.  For a starting point at that time (2016),
the reuse of the given Perl parser in Kernel's sources was good enough but
nowerdays it has its limits.  This was the time, I started a spin-off with a
POC, implementing a python variant of the parser together with it's
:ref:`kernel-doc directive <kernel-doc-directive>`.

There was also a attempt in 2017 where I send a RFC replacing the Perl parser
with the python variant, some parts of the discussion are worth to mention:

- Start with `lwn article <https://lwn.net/Articles/712395/>`_ or the ML entry
  :mid:`[RFC PATCH v1 0/6] pure python kernel-doc parser and more
  <1485287564-24205-1-git-send-email-markus.heiser@darmarit.de>` ... there are
  also helpful remarks and thoughts from the community I won't miss:
- from Jon :mid:`20170126115005.7bf0e4a6@lwn.net`
- from Jani :mid:`8B5A4B93-5497-4BEE-8A88-51A7C0E75E32@darmarit.de`
- about using *other* parser :mid:`87a8ad39nr.fsf@intel.com`

Everything has evolved in the meantime.  Meanwhile the LinuxDoc project is also
used in other projects and covers more use-cases than only to build Kernel's
documentation.  Anyway both implementations, the python and the Perl one support
kernel-doc markup while the Python one always serves a superset over the Perl
script from Kernel's source.  That's why it is possible to (drop-in) replace
Kernel's sphinx-extensions_ and the Perl parser with the LinuxDoc extension.  To
see how, take a look at chapter :ref:`patch-linux-kernel`.

It is worth to mention, that both scripts will produce different reST_ from the
same kernel-doc markup.  This is only logical and consistent, because the python
variant is further more developed and integrates better into Sphinx.

To give you a picture of such a difference, lets take the :ref:`example from
introduction <kernel-doc-intro-example>`, take a look at output from the Perl
variant below and compare it with the :ref:`output of the Python variant
<kernel-doc-intro-example-out>`.

.. code-block:: rst

    .. c:function:: int foobar (int arg1, int arg2)

       short function description of foobar

    **Parameters**

    ``int arg1``
      Describe the first argument to foobar.

    ``int arg2``
      Describe the second argument to foobar.  One can provide multiple line
      descriptions for arguments.

    **Description**

    A longer description, with more discussion of the function :c:func:`foobar()` that
    might be useful to those using or modifying it.  Begins with empty comment
    line and may include additional embedded empty comment lines.  Within, you
    can refer other definitions (e.g. :c:type:`struct my_struct <my_struct>`,
    :c:type:`typedef my_typedef <my_typedef>`,``CONSTANT``, $ENVVAR etc.).

    The longer description can have multiple paragraphs and you can use reST
    inline markups like *emphasise* and **emphasis strong**.  You also have reST
    block markups like lists or literal available:

    Ordered List:
    - item one
    - item two
    - literal block::

	 a + b --> x

    **Return**

    Describe the return value of foobar.

As you can see, Perl's output is a flatten stream of markups and emphasis while
the the Python variant produce a structured and valid reST_ document.  One might
think, that we can fix the Perl script to be more structural.  As far as I know,
it is not possible to embed structured reST into the doctree without being
in-process where you have access to the *in memory* doctree_.  I don't know
where the Kernel development goes in the future, IMO there are three choices:

1. Stay with Perl implementation of the kernel-doc parser and fumble around with
   its limitations.

2. Take over the Python implementation of the parser and it's kernel-doc
   directive.

3. Or simply add LinuxDoc as one external requirement more to the build chain
   and drop/ignore the extension currently in the source tree (for a POC see
   :ref:`patch <patch-linux-kernel>`).

