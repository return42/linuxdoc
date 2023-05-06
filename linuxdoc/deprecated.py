# SPDX-License-Identifier: AGPL-3.0-or-later
"""
deprecated
~~~~~~~~~~

Deprecated Operations implemented for compatibility.

"""
# pylint: disable=import-outside-toplevel

import sys

def _report(msg):
    sys.stderr.write(' '.join(line.strip() for line in msg.splitlines()) + '\n')

# ------------------------------------------------------------------------------
# command-lines deprecated
# ------------------------------------------------------------------------------

def cmd_kernel_doc():
    """DEPRECATED: The maintenance of the ``kernel-doc`` command ended in
    version 20230321.  The command will be removed in a future release: use
    command ``linuxdoc.rest``!

    """
    _report(cmd_kernel_doc.__doc__)
    from .rest import main
    return main()

def cmd_kernel_autodoc():
    """DEPRECATED: The maintenance of the ``kernel-autodoc`` command ended in
    version 20230321.  The command will be removed in a future release: use
    command ``linuxdoc.autodoc``!

    """
    _report(cmd_kernel_autodoc.__doc__)
    from .autodoc import main
    return main()

def cmd_kernel_lintdoc():
    """DEPRECATED: The maintenance of the ``kernel-lintdoc`` command ended in
    version 20230321.  The command will be removed in a future release: use
    command ``linuxdoc.lintdoc``!

    """
    _report(cmd_kernel_lintdoc.__doc__)
    from .lint import main
    return main()

def cmd_kernel_grepdoc():
    """DEPRECATED: The maintenance of the ``kernel-grepdoc`` command ended in
    version 20230321.  The command will be removed in a future release: use
    command ``linuxdoc.grepdoc``!

    """
    _report(cmd_kernel_grepdoc.__doc__)
    from .grepdoc import main
    return main()
