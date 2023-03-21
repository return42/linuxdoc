# SPDX-License-Identifier: AGPL-3.0-or-later
"""\
cdomain
~~~~~~~

Replacement for the sphinx c-domain.  For user documentation see
:ref:`customized-c-domain`.

"""

from .compat import sphinx_has_c_namespace

__version__  = '3.0'

if sphinx_has_c_namespace():
    from .cdomainv3 import CDomain
else:
    from .cdomainv2 import CDomain

def setup(app):  # pylint: disable=missing-docstring

    app.add_domain(CDomain, override=True)
    return dict(
        version = __version__,
        parallel_read_safe = True,
        parallel_write_safe = True,
    )
