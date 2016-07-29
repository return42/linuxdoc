.. -*- coding: utf-8; mode: rst -*-
.. include:: refs.txt

.. _install_linuxdoc:

================
Install LinuxDoc
================

Install bleeding edge.::

  pip install [--user] git+http://github.com/return42/linuxdoc.git

As the linuxdoc lib evolving constantly, an update should be carried out
regularly.::

  pip install --upgrade git+http://github.com/return42/linuxdoc.git

If you are a developer and like to contribute to the linuxdoc lib, fork on
github or clone and make a developer install::

  git clone https://github.com/return42/linuxdoc
  cd linuxdoc
  make install

Below you see how to integrate the linuxdoc sphinx extensions into your sphinx
build process. In the ``conf.py`` (`sphinx config`_) add the linuxdoc
extensions:

.. code-block:: python

   extensions = [ 'linuxdoc.rstKernelDoc', 'linuxdoc.rstFlatTable'
                  , 'linuxdoc.kernel_include', 'linuxdoc.manKernelDoc' ]

