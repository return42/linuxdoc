#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LinuxDoc unit test driver
~~~~~~~~~~~~~~~~~~~~~~~~~

This script runs the LinuxDoc unit test suite.

:copyright:  Copyright (C) 2016 Markus Heiser
:license:    GPL Version 2, June 1991 see linux/COPYING for details.
"""

from __future__ import print_function

import os
import sys

from os.path import dirname, abspath

ROOT_FOLDER = abspath( dirname(__file__) or "." + os.sep + os.pardir)
sys.path.insert(0, ROOT_FOLDER)

from fspath import FSPath, OS_ENV

TEST_FOLDER = FSPath(dirname(__file__) or ".")

if not OS_ENV.get("TEST_TEMPDIR"):
    OS_ENV.TEST_TEMPDIR = TEST_FOLDER / "build"

TEST_TEMPDIR = FSPath(OS_ENV.TEST_TEMPDIR)

print('Temporary files will be placed in %s.' % TEST_TEMPDIR)
TEST_TEMPDIR.makedirs()

print('Running LinuxDoc test suite (with Python %s)...' % sys.version.split()[0])
sys.stdout.flush()

import nose
nose.main()
