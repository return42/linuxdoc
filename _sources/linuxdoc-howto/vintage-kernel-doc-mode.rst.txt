.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _vintage-kernel-doc-mode:

=======================
Vintage kernel-doc mode
=======================

.. hint::

    This section exists mainly for historical reasons. The *vintage* kernel-doc
    mode is only relevant for those who have to work with old kernel-doc
    comments (e.g. `Kernel's Source code documentation`_).

Within the *vintage* kernel-doc mode the kernel-doc parser ignores any
whitespace formatting/markup. Since formatting with whitespace is substantial
for ASCII markups, it's recommended to use the :ref:`reST-kernel-doc-mode` on
any new or changed comment!

Determined by the history of the kernel-doc comments, the *vintage* kernel-doc
comments contain characters like "*" or strings with e.g. leading/trailing
underscore ("_"), which are in-line markups in reST. Here a short example from a
*vintage* comment::

    <SNIP> -----
    * In contrast to the other drm_get_*_name functions this one here returns a
    * const pointer and hence is threadsafe.
    <SNAP> -----

Within reST markup (the new base format), the wildcard in the string
``drm_get_*_name`` has to be masked by the kernel-doc parser:
``drm_get_\\*_name``. Some more examples from reST markup:

* Emphasis "*":  like ``*emphasis*`` or ``**emphasis strong**``
* Leading "_" :  is a *anchor* in reST markup (``_foo``).
* Trailing "_:  is a reference in reST markup (``foo_``).
* interpreted text: "`"
* in-line literals: "``"
* substitution references: "|"

As long as the kernel-doc parser runs in the *vintage* kernel-doc mode, these
special strings will be masked in the reST output and can't be used as
*plain-text markup*.

.. hint::

  The kernel source contains tens of thousands of vintage kernel-doc comments,
  applications which has to work with them must be able to distinguish between
  vintage and the new reST markup.


To force the parser to switch into the reST mode add the following comment
(e.g.) at the top of your source code file (or at any line where reST content
starts).::

    /* parse-markup: reST */ *

In reST mode the kernel-doc parser pass through all text unchanged to the reST
tool-chain including any whitespace and reST markup. To toggle back to
:ref:`vintage-kernel-doc-mode` type the following line::

    /* parse-markup: kernel-doc */


.. _vintage-mode-quirks:

vintage mode quirks
===================

In the following, you will find some quirks of the *vintage* kernel-doc mode.


* Since a colon introduce a new section, you can't use colons. E.g. a comment
  line like::

      prints out: hello world

  will result in a section with the title "prints out" and a paragraph with only
  "hello world" in, this is mostly not what you expect. To avoid sectioning,
  place a space in front of the column::

      prints out : hello world

* The multi-line descriptive text you provide does *not* recognize
  line breaks, so if you try to format some text nicely, as in::

      Return:
         0 - cool
         1 - invalid arg
         2 - out of memory

  this will all run together and produce::

      Return: 0 - cool 1 - invalid arg 2 - out of memory

* If the descriptive text you provide has lines that begin with some phrase
  followed by a colon, each of those phrases will be taken as a new section
  heading, which means you should similarly try to avoid text like::

      Return:
        0: cool
        1: invalid arg
        2: out of memory

  every line of which would start a new section.  Again, probably not what you
  were after.
