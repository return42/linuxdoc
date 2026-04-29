# SPDX-License-Identifier: AGPL-3.0-or-later
"""\
cdomain
~~~~~~~

Replacement for the sphinx c-domain.  For user documentation see
:ref:`customized-c-domain`.

"""

from sphinx.domains.c import CDomain as Base_CDomain

# from sphinx.domains.c import CObject as Base_CObject

__version__ = "3.0"


# fixes https://github.com/sphinx-doc/sphinx/commit/0f49e30c51b5cc5055cda5b4b294c2dd9d1df573#r38750737


# class CObject(Base_CObject):  # pylint: disable=abstract-method
#     """Description of a C language object."""


class CDomain(Base_CDomain):  # pylint: disable=abstract-method
    """C language domain."""


def setup(app):  # pylint: disable=missing-docstring

    app.add_domain(CDomain, override=True)
    return dict(
        version=__version__,
        parallel_read_safe=True,
        parallel_write_safe=True,
    )
