# -*- coding: utf-8; mode: python -*-
u"""
    cdomain
    ~~~~~~~

    Replacement for the sphinx c-domain.

    :copyright:  Copyright (C) 2018 Markus Heiser
    :license:    GPL Version 2, June 1991 see Linux/COPYING for details.

    For user documentation see :ref:`customized-c-domain`.
"""

import sphinx

# Get Sphinx version
major, minor, patch = sphinx.version_info[:3]  # pylint: disable=invalid-name

if major >= 3:
    from .cdomainv3 import CDomain
    __version__ = 3
else:
    from .cdomainv2 import CDomain
    __version__ = 2

def setup(app):  # pylint: disable=missing-docstring

    app.add_domain(CDomain, override=True)
    return dict(
        version = __version__,
        parallel_read_safe = True,
        parallel_write_safe = True
    )
