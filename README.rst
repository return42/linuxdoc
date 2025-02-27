========
LinuxDoc
========

The LinuxDoc library contains Sphinx-doc extensions and command line tools to
extract documentation from C/C++ source file comments.  Even if this project
started in context of the Linux-Kernel documentation, you can use these
extensions in common Sphinx-doc projects.


Install
=======

`Install LinuxDoc <https://return42.github.io/linuxdoc/install.html>`__ using `pip
<https://pip.pypa.io/en/stable/getting-started/>`__::

  pip install --user -U linuxdoc


Development
===========

This project is managed by `hatch <https://hatch.pypa.io>`_, for development
tasks you should install ``hatch``::

  $ pipx install hatch

Format and *lint* your code before commit::

  $ hatch run fix
  $ hatch run check

To enter the development environment use ``shell``::

  $ hatch shell


Links
=====

- Documentation:   https://return42.github.io/linuxdoc
- Releases:        https://pypi.org/project/linuxdoc/
- Code:            https://github.com/return42/linuxdoc
- Issue tracker:   https://github.com/return42/linuxdoc/issues
- License:         `AGPLv3+ <https://github.com/return42/linuxdoc/blob/master/LICENSE>`__
