========
LinuxDoc
========

The LinuxDoc library contains Sphinx-doc extensions and command line tools to
extract documentation from C/C++ source file comments.  Even if this project
started in context of the Linux-Kernel documentation, you can use these
extensions in common Sphinx-doc projects.

``linuxdoc`` is distributed under the terms of the `AGPL-3.0-or-later`_ license.


Install
=======

`Install LinuxDoc`_ release from pypi_ using pip_::

  python -m pip install --user -U linuxdoc


Development
===========

This project is managed by hatch_, for development tasks you should install
``hatch``:

.. code:: sh

   pipx install hatch

The tools required for the developer environment are provided in the
`mise.toml`_ configuration file (*Mise En Place*).

.. code:: sh

   git clone https://github.com/return42/linuxdoc.git
   cd linuxdoc
   mise install

Format and *lint* your code before commit:

.. code:: sh

   hatch run fix
   hatch run check

To enter the development environment use ``shell dev``:

.. code:: sh

   hatch shell dev
   # source "/share/linuxdoc/.venv/bin/activate"
   # (.venv) $

To get a *live* build of documentation:

.. code:: sh

   hatch run doc:man
   hatch run doc:live

.. hint::

   Don't forget to `build manual pages`_, otherwise you will see a message::

     WARNING: download file not readable: dist/doc/man/user_function.2.gz [download.not_readable]

For project tasks & maintenance use:

.. code:: sh

   hatch run prj --help


Build & Deploy
--------------

To force push online doc to the ``gh-pages`` branch:

.. code:: sh

   hatch run doc:man
   hatch run ./prj doc.gh-pages

Use `hatch build`_ command to build sdist_ an wheel_:

.. code:: sh

   hatch build -c

and `hatch publish`_ command to deploy on pypi_ (or ``test.pypi.org``):

.. code:: sh

   hatch publish -r https://test.pypi.org/legacy/ ./dist/linuxdoc-YYYYMMDD*
   hatch publish ./dist/linuxdoc-YYYYMMDD*


.. _hatch build: https://hatch.pypa.io/1.7/build/#building
.. _hatch publish: https://hatch.pypa.io/1.7/publish/
.. _twine: https://twine.readthedocs.io/en/stable/
.. _sdist: https://hatch.pypa.io/1.7/plugins/builder/sdist/)
.. _wheel: https://hatch.pypa.io/1.7/plugins/builder/wheel/


Mise En Place
-------------

For the developer environment, `mise en place`_ is recommended:

.. code:: sh

   $ curl https://mise.run | sh

   # to install shell completions .. and mises's backends dependencies
   $ mise use -g usage

To activate ``mise`` in the current bash session see ``mise activate --help``.
For a more streamlined setup, you can configure activation in your shell's
configuration file.

For the Bash_ shell, the following lines can be added to the ``~/.bashrc``
file:

.. code:: bash

   if [ -f "${HOME}/.local/bin/mise" ]; then
       eval "$("${HOME}/.local/bin/mise" activate bash --shims)"
   fi


References
==========

- Documentation:   https://return42.github.io/linuxdoc
- Releases:        https://pypi.org/project/linuxdoc/
- Code:            https://github.com/return42/linuxdoc
- Issue tracker:   https://github.com/return42/linuxdoc/issues
- License file:    `AGPLv3+ <https://github.com/return42/linuxdoc/blob/master/LICENSE>`__
- `mise en place`_: mise.toml_
- Python_
- Bash_
- shellcheck_

.. _AGPL-3.0-or-later: https://spdx.org/licenses/AGPL-3.0-or-later.html
.. _Bash: https://www.gnu.org/software/bash/
.. _Install LinuxDoc: https://return42.github.io/linuxdoc/install.html
.. _Python: https://www.python.org/
.. _build manual pages: https://return42.github.io/linuxdoc/linuxdoc-howto/man-pages.html#kernel-doc-man-builder
.. _hatch: https://hatch.pypa.io
.. _mise en place: https://mise.jdx.dev/getting-started.html
.. _mise.toml: https://github.com/return42/linuxdoc/blob/master/mise.toml
.. _pip: https://pip.pypa.io/en/stable/getting-started/
.. _pypi: https://pypi.org/project/linuxdoc/
.. _shellcheck: https://github.com/koalaman/shellcheck/wiki/Checks
