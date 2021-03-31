# -*- coding: utf-8; mode: python -*-
u"""
    cdomainv3 (Sphinx v>=3.0)
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Replacement for the sphinx c-domain.

    :copyright:  Copyright (C) 2020 Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    For user documentation see :ref:`customized-c-domain`.
"""

from sphinx.domains.c import CObject as Base_CObject
from sphinx.domains.c import CDomain as Base_CDomain

# fixes https://github.com/sphinx-doc/sphinx/commit/0f49e30c51b5cc5055cda5b4b294c2dd9d1df573#r38750737

class CObject(Base_CObject): # pylint: disable=abstract-method
    """Description of a C language object.

    """

class CDomain(Base_CDomain): # pylint: disable=abstract-method
    """C language domain.

    """
