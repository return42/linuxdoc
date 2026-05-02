.. include:: refs.txt

.. _install_linuxdoc:

================
Install LinuxDoc
================

Install / update from `pypi.org <https://pypi.org/project/linuxdoc/>`_::

  python -m pip install -U linuxdoc

Alternative method: install bleeding edge into `user site-packages
<https://docs.python.org/3/library/sysconfig.html#sysconfig-user-scheme>`_::

  python -m pip install -U --user git+http://github.com/return42/linuxdoc.git

Below you see how to integrate the LinuxDoc sphinx extensions into your sphinx
build process. In the ``conf.py`` (`sphinx config`_) add the LinuxDoc
extensions:

.. code-block:: python

   extensions = [
     "linuxdoc.rstFlatTable",    # Implementation of the "flat-table" reST-directive.
     "linuxdoc.rstKernelDoc",    # Implementation of the "kernel-doc" reST-directive.
     "linuxdoc.kernel_include",  # Implementation of the "kernel-include" reST-directive.
     "linuxdoc.manKernelDoc",    # Implementation of the "kernel-doc-man" builder
     "linuxdoc.cdomain",         # Replacement for the sphinx c-domain.
     "linuxdoc.kfigure",         # Sphinx extension which implements scalable image handling.
     ]
