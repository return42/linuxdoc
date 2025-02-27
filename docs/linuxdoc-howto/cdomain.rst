.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _customized-c-domain:

==========================
Customized sphinx c-domain
==========================

.. sidebar::  WIP :py:mod:`linuxdoc.cdomain`

   Sphinx v3.0 and above includes a `C, initial rewrite`_ which is not downward
   compatible and the Sphinx C-Domain is still *WIP* (`Sphinx-doc PR-8313`_).
   Therefore not all the features of :ref:`customized-c-domain` has been
   migrated right now (some are obsolete since V3.1).

.. _C, initial rewrite:   https://github.com/sphinx-doc/sphinx/commit/0f49e30c51b5cc5055cda5b4b294c2dd9d1df573#r38750737
.. _Sphinx-doc PR-8313: https://github.com/sphinx-doc/sphinx/pull/8313

LinuxDoc brings a customized `Sphinx's C Domain`_ extension.  Here is a list of
customizations of the :py:class:`CObject <linuxdoc.cdomain.CObject>`:

* Handle signatures of function-like macros well. Don't try to deduce arguments
  types of function-like macros.

* Moved the *duplicate C object description* warnings for function declarations
  in the nitpicky mode.  See Sphinx documentation for the config values for
  nitpicky_ and nitpick_ignore_.

* Add option ``name`` to the ``c:function:`` directive.  With option ``name``
  the ref-name of a function can be modified.  E.g. you can *rename* the
  reference name of a function with a common name like ``open`` or ``ioctl``:

  .. code-block:: rst

     .. c:function:: int ioctl( int fd, int request )
        :name: VIDIOC_LOG_STATUS

  The func-name (e.g. ioctl) remains in the output but the ref-name changed from
  ``ioctl`` to ``VIDIOC_LOG_STATUS``.  The index entry for this function is also
  changed to ``VIDIOC_LOG_STATUS`` and the function can now referenced by:

  .. code-block:: rst

     :c:func:`VIDIOC_LOG_STATUS`
