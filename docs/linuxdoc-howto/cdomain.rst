.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _customized-c-domain:

==========================
Customized sphinx c-domain
==========================

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
