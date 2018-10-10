.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _kfigure:

==================================
Scalable figure and image handling
==================================

LinuxDoc brings the ``kfigure`` Sphinx extension which implements scalable image
handling.  The build for image formats depend on image's source format and
output's destination format.  This extension implement methods to simplify image
handling from the author's POV.  Directives like ``kernel-figure`` implement
methods *to* always get the best output-format even if some tools are not
installed.

* ``.. kernel-image``: for image handling / a ``.. image::`` replacement

* ``.. kernel-figure``: for figure handling / a ``.. figure::`` replacement

* ``.. kernel-render``: for render markup / a concept to embed *render*
  markups (or languages). Supported markups:

  - ``DOT``: render embedded Graphviz's **DOC**
  - ``SVG``: render embedded Scalable Vector Graphics (**SVG**)
  - ... *developable*

Used tools:

* ``dot(1)``: Graphviz (http://www.graphviz.org). If Graphviz is not
  available, the DOT language is inserted as literal-block.

* SVG to PDF: To generate PDF, you need at least one of this tools:

  - ``convert(1)``: ImageMagick (https://www.imagemagick.org)

List of customizations:

* generate PDF from SVG / used by PDF (LaTeX) builder

* generate SVG (html-builder) and PDF (latex-builder) from DOT files.
  DOT: see http://www.graphviz.org/content/dot-language


Figures & images
================

If you want to add an image, you should use the ``kernel-figure`` and
``kernel-image`` directives. E.g. to insert a figure with a scalable image
format use SVG (:ref:`svg_image_example`)::

    .. kernel-figure::  svg_image.svg
       :alt:    simple SVG image

       SVG image example

.. _svg_image_example:

.. kernel-figure::  svg_image.svg
   :alt:    simple SVG image

   SVG image example

The kernel figure (and image) directive support **DOT** formated files, see

* DOT: http://graphviz.org/pdf/dotguide.pdf
* Graphviz: http://www.graphviz.org/content/dot-language

A simple example (:ref:`hello_dot_file`)::

  .. kernel-figure::  hello.dot
     :alt:    hello world

     DOT's hello world example

.. _hello_dot_file:

.. kernel-figure::  hello.dot
   :alt:    hello world

   DOT's hello world example

Embed *render* markups (or languages) like Graphviz's **DOT** is provided by the
``kernel-render`` directives.::

  .. kernel-render:: DOT
     :alt: foobar digraph
     :caption: Embedded **DOT** (Graphviz) code

     digraph foo {
      "bar" -> "baz";
     }

How this will be rendered depends on the installed tools. If Graphviz is
installed, you will see an vector image. If not the raw markup is inserted as
*literal-block* (:ref:`hello_dot_render`).

.. _hello_dot_render:

.. kernel-render:: DOT
   :alt: foobar digraph
   :caption: Embedded **DOT** (Graphviz) code

   digraph foo {
      "bar" -> "baz";
   }

The *render* directive has all the options known from the *figure* directive,
plus option ``caption``.  If ``caption`` has a value, a *figure* node is
inserted. If not, a *image* node is inserted. A ``caption`` is also needed, if
you want to refer it (:ref:`hello_svg_render`).

Embedded **SVG**::

  .. kernel-render:: SVG
     :caption: Embedded **SVG** markup
     :alt: so-nw-arrow

     <?xml version="1.0" encoding="UTF-8"?>
     <svg xmlns="http://www.w3.org/2000/svg" version="1.1" ...>
        ...
     </svg>

.. _hello_svg_render:

.. kernel-render:: SVG
   :caption: Embedded **SVG** markup
   :alt: so-nw-arrow

   <?xml version="1.0" encoding="UTF-8"?>
   <svg xmlns="http://www.w3.org/2000/svg"
     version="1.1" baseProfile="full" width="70px" height="40px" viewBox="0 0 700 400">
   <line x1="180" y1="370" x2="500" y2="50" stroke="black" stroke-width="15px"/>
   <polygon points="585 0 525 25 585 50" transform="rotate(135 525 25)"/>
   </svg>

