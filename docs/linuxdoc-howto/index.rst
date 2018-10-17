.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _linuxdoc-howto:

==============
LinuxDoc HowTo
==============

As you might already noticed, the LinuxDoc project has a focus on kernel-doc.
Most of the documentation you will find here deal with this markup, its syntax,
use-cases and tools. But that's not all ..

  The LinuxDoc project was founded at the time where the linux Kernel migrates
  its documentation from XML-DocBook to the plain text format reST_ (OT: if
  interested :lwn:`692704` and :lwn:`692705`).  In that context we also touched
  other topics.  To name just two; the ":ref:`Scalable figure and image handling
  <kfigure>`" and the ":ref:`diff friendly table markup <rest-flat-table>`".
  All these and more topics are dealing with the same parent topic: *The various
  aspects of documenting software developments* and are incorporated into the
  LinuxDoc project.


kernel-doc
==========

.. toctree::
   :maxdepth: 2

   kernel-doc-syntax
   kernel-doc-directive
   kernel-doc-examples
   kernel-doc-modes


other topics
============

.. toctree::
   :maxdepth: 2

   kfigure
   table-markup
   cdomain
   man-pages
   kernel-include-directive

At least some handy links about reST_  and the `Sphinx markup constructs`_:

* reST_ primer, `reST (quickref)`_, `reST (spec)`_
* `Sphinx markup constructs`_
* `sphinx domains`_
* `sphinx cross references`_
* `intersphinx`_, `sphinx.ext.intersphinx`_
* `sphinx-doc`_, `sphinx-doc FAQ`_
* `docutils`_, `docutils FAQ`_
* :ref:`process:codingstyle` and in absence of a more detailed C style guide
  for documentation, the `Python's Style Guide for documentation
  <https://docs.python.org/devguide/documenting.html#style-guide>`_ provides a
  good orientation.
