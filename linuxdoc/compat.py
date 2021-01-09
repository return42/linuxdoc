# -*- coding: utf-8; mode: python -*-
# SPDX-License-Identifier: GPL-2.0
# pylint: disable=C, unused-import, invalid-name, missing-docstring
"""\
compat
~~~~~~

Implementation of a compatibility layer for sphinx and docutils related modules.

Downward compatibility is unfortunately no strength of sphinx-doc `[ref]
<https://github.com/sphinx-doc/sphinx/issues/3212#issuecomment-283756374>`__ and
patch levels are not really exists or if so they are not shipped within LTS
distributions.  Therefor a minimal *compatibility layer* is needed.  Even if we
do our best here, there are also a lot of incompatibilities in between sphinx
and docutils whose fixing is out of the scope of this linuxdoc project `[ref]
<https://www.kernel.org/doc/html/latest/doc-guide/sphinx.html#sphinx-install>`__.

To get best results (and less warnings) its inevitable to use latest sphinx-doc
version.

More details see Sphinx-doc’s `CHANGELOG
<http://www.sphinx-doc.org/en/master/changes.html>`__ and docutils
`RELEASE-NOTES <http://docutils.sourceforge.net/RELEASE-NOTES.html>`__

"""

import docutils
import sphinx

from pkg_resources import parse_version

sphinx_version = parse_version(sphinx.__version__)
docutils_version = parse_version(docutils.__version__)

def sphinx_has_c_namespace():
    """Checks wether Sphinx version supports `.. c:namespace::
    <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#namespacing>`__

    """
    return sphinx_version >= parse_version('3.1')

def sphinx_has_c_types():
    """Checks wether Sphinx version supports `.. c:struct::, c:union and other C types
    <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#the-c-domain>`__

    """
    return sphinx_version >= parse_version('3.1')
