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
tasks you should install ``hatch``:

.. code:: sh

   pipx install hatch

The tools required for the developer environment are provided in the
`mise.toml`_ configuration file (*Mise En Place*).

.. code:: sh

   git clone https://codeberg.org/return42/linuxdoc.git
   cd linuxdoc
   mise install

Format and *lint* your code before commit:

.. code:: sh

  hatch run fix
  hatch run check

To enter the development environment use ``shell dev``:

.. code:: sh

  hatch shell dev

For project tasks & maintenance use:

.. code:: sh

  hatch run prj

For example, to get a *live* build of documentation:

.. code:: sh

  hatch run prj doc.live


Links
=====

- Documentation:   https://return42.github.io/linuxdoc
- Releases:        https://pypi.org/project/linuxdoc/
- Code:            https://github.com/return42/linuxdoc
- Issue tracker:   https://github.com/return42/linuxdoc/issues
- License:         `AGPLv3+ <https://github.com/return42/linuxdoc/blob/master/LICENSE>`__

- Python_
- `mise en place`_: mise.toml_
- shellcheck_
- Bash_

.. _Python: https://www.python.org/
.. _mise en place: https://mise.jdx.dev/getting-started.html
.. _mise.toml: https://codeberg.org/return42/mt4os/src/branch/main/mise.toml
.. _shellcheck: https://github.com/koalaman/shellcheck/wiki/Checks
.. _Bash: https://www.gnu.org/software/bash/
