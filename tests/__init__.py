#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    linuxdoc unit test driver
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright:  Copyright (C) 2017 Markus Heiser
    :license:    AGPL-3.0-or-later; see LICENSE for details.
"""

try:
    import os
    if os.environ.get("DEBUG", None):
        from pytest import set_trace
        __builtins__["DEBUG"] = set_trace
except ImportError:
    pass
