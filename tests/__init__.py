#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    linuxdoc unit test driver
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright:  Copyright (C) 2017 Markus Heiser
    :license:    GPL Version 2, June 1991 see linux/COPYING for details.
"""

try:
    import os
    if os.environ.get("DEBUG", None):
        from pytest import set_trace
        __builtins__["DEBUG"] = set_trace
except ImportError:
    pass
