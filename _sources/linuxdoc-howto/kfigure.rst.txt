.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _kfigure:

==================================
Scalable figure and image handling
==================================

LinuxDoc brings the :py:mod:`linuxdoc.kfigure` Sphinx extension which implements
scalable image handling.  Scalable here means; *scalable* in sense of the build
process.  The build for image formats depends on image's source format and
output's destination format.  Different builder prefer different image formats,
e.g. *latex* builder prefer PDF while *html* builder prefer SVG format for
images.  To get a pdf from a SVG input a third party converter is needed.
Normally in absence of such a converter tool, the build process will break.
From the authors POV it's annoying to care about the build process when handling
with images, especially since he has no possibility to influence the build
process on every build host out there.

With the directives of :py:mod:`linuxdoc.kfigure`, if a third party converter is
missed, the build process will spit out a message about and continues with a
lower quality in the output.  Even if the output is e.g. a raw SVG or DOT, in
some use cases it might be a solution that fits.  As we say, its *scalable*: If
you are the operator of a build host, install the recommended tools and you will
always get the best quality.  For this the :py:mod:`linuxdoc.kfigure` implements
a central :py:func:`convert_image <linuxdoc.kfigure.convert_image>` function
which is used by the directives:

``.. kernel-figure`` :ref:`[ref] <kernel-figure>`
  Except remote URI and glob pattern, it's a full replacement for the
  :rst-directive:`figure` directive (:py:class:`KernelFigure
  <linuxdoc.kfigure.KernelFigure>`)

``.. kernel-image`` :ref:`[ref] <kernel-image>`
  A full replacement (except remote URI and glob pattern) for the
  :rst-directive:`image` directive (:py:class:`KernelImage
  <linuxdoc.kfigure.KernelImage>`)

``.. kernel-render`` :ref:`[ref] <kernel-render>`
  Renders the block content by a converter tool (:py:class:`KernelRender
  <linuxdoc.kfigure.KernelRender>`).  Comparably to the :rst-directive:`figure`
  directive with the assumption that the content of the image is given in the
  block and not in an external image file.  This directive is helpful for use
  cases where the image markup is editable and written by the author himself
  (e.g. a small DOT graph).

  Has all the options known from the figure directive, plus option caption.  If
  caption has a value, a figure node with the caption is inserted.  If not, a
  image node is inserted.

  Supported markups:

  - DOT_: render embedded Graphviz's DOC language (`Graphviz's dot`_)
  - SVG_: render embedded Scalable Vector Graphics
  - ... *developable*

As already mentioned, the directives kernel-figure, kernel-image and
kernel-render are based on one central function.  In the current expansion stage
:py:func:`convert_image <linuxdoc.kfigure.convert_image>` uses the following
tools (latex builder is used when generating PDF):

- ``dot(1)`` `Graphviz's dot`_ command
- ``convert(1)`` command from ImageMagick_

To summarize the build strategies:

- DOT_ content, if `Graphviz's dot`_ command is not available

  - html builder: the DOT language is inserted as literal block.
  - latex builder: the DOT language is inserted as literal block.

- SVG_ content

  - html builder: always insert SVG
  - latex builder: if ImageMagick_ is not available the raw SVG is inserted as
    literal-block.

.. _kfigure_build_tools:

.. admonition:: recommended build tools

   With the directives from :py:mod:`linuxdoc.kfigure` the build process is
   flexible.  To get best results in the generated output format, install
   ImageMagick_ and Graphviz_.


.. _kernel-figure:
.. _kernel-image:

kernel-figure & kernel-image
============================

If you want to add an image, you should use the ``kernel-figure`` and
``kernel-image`` directives.  Except remote URI and glob pattern, they are full
replacements for the :rst-directive:`figure` and :rst-directive:`image`
directive.  Here you will find a few recommendations for use, for a complete
description see :rst-directive:`reST markup <images>`.

If you want to insert a image into your documentation, prefer a scalable
vector-graphics_ format over a raster-graphics_ format.  With scalable
vector-graphics_ there is a chance, that the rendered output going to be best.
SVG_ is a common and standardized vector-graphics_ format and there are many
tools available to create and edit SVG_ images.  That's why its recommended
to use SVG_ in most use cases.

In the literal block below, you will find a simple example on how to insert a
SVG_ figure (image) with the ``kernel[-figure|image]`` directive, about
rendering please note :ref:`build tools <kfigure_build_tools>`:

.. code-block:: rst

   .. _svg_image_example:

   .. kernel-figure::  svg_image.svg
      :alt:    simple SVG image

       SVG figure example

   The first line in this example is only to show how an anchor is set and what
   a reference to it looks like :ref:`svg_image_example`.

.. admonition:: kernel-figure SVG
   :class: rst-example

   .. _svg_image_example:

   .. kernel-figure::  svg_image.svg
      :alt:    simple SVG image

      SVG figure example

   The first line in this example is only to show how an anchor is set and what
   a reference to it looks like :ref:`svg_image_example`.

In addition to the :rst-directive:`figure` and :rst-directive:`image`,
kernel-figure and kernel-image also support DOT_ formated files.  A simple
example is shown in figure :ref:`hello_dot_file`.

.. code-block:: rst

   .. kernel-figure::  hello.dot
     :alt:    hello world

     DOT's hello world example

.. admonition:: kernel-figure DOT
   :class: rst-example

   .. _hello_dot_file:

   .. kernel-figure::  hello.dot
      :alt:    hello world

      DOT's hello world example

.. _kernel-render:

kernel-render
=============

Embed *render* markups (languages) like Graphviz's DOT_ or SVG_ are provided by
the kernel-render directive. The kernel-render_ directive has all the options
known from the :rst-directive:`image` directive (kernel-figure_), plus option
``caption``.  If ``caption`` has a value, a :rst-directive:`figure` like node is
inserted into the doctree_.  If not, a :rst-directive:`image` like node is
inserted.

DOT markup
----------

A simple example of embedded DOT_ is shown in figure :ref:`hello_dot_render`:

.. code-block:: rst

   .. _hello_dot_render:

   .. kernel-render:: DOT
      :alt: foobar digraph
      :caption: Embedded **DOT** (Graphviz) code

      digraph foo {
        "bar" -> "baz";
      }

    A ``caption`` is needed, if you want to refer the figure:
    :ref:`hello_dot_render`.

Please note :ref:`build tools <kfigure_build_tools>`.  If Graphviz_ is
installed, you will see an vector image.  If not, the raw markup is inserted as
*literal-block*.

.. admonition:: kernel-render DOT
   :class: rst-example

   .. _hello_dot_render:

   .. kernel-render:: DOT
      :alt: foobar digraph
      :caption: Embedded **DOT** (Graphviz) code

      digraph foo {
        "bar" -> "baz";
      }

   A ``caption`` is needed, if you want to refer the figure:
   :ref:`hello_dot_render`.


SVG markup
----------

A simple example of embedded SVG_ is shown in figure :ref:`hello_svg_render`:

.. code-block:: rst

   .. _hello_svg_render:

   .. kernel-render:: SVG
      :caption: Embedded **SVG** markup
      :alt: so-nw-arrow

      <?xml version="1.0" encoding="UTF-8"?>
      <svg xmlns="http://www.w3.org/2000/svg" version="1.1"
           baseProfile="full" width="70px" height="40px"
           viewBox="0 0 700 400"
           >
        <line x1="180" y1="370"
              x2="500" y2="50"
              stroke="black" stroke-width="15px"
              />
        <polygon points="585 0 525 25 585 50"
                 transform="rotate(135 525 25)"
                 />
      </svg>

.. admonition:: kernel-render SVG
   :class: rst-example

   .. _hello_svg_render:

   .. kernel-render:: SVG
      :caption: Embedded **SVG** markup
      :alt: so-nw-arrow

      <?xml version="1.0" encoding="UTF-8"?>
      <svg xmlns="http://www.w3.org/2000/svg" version="1.1"
           baseProfile="full" width="70px" height="40px"
           viewBox="0 0 700 400"
           >
        <line x1="180" y1="370"
              x2="500" y2="50"
              stroke="black" stroke-width="15px"
              />
        <polygon points="585 0 525 25 585 50"
                 transform="rotate(135 525 25)"
                 />
      </svg>
