#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""web entry point for local dev server"""
# pylint: disable=invalid-name

import os
import sys
from typing import List

# fix python path for running as python -mweb.ui

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

# path needs to be fixed pylint: disable=wrong-import-position
from web.ui import app
from web import dev_server

extra_dirs: List[str] = [os.path.join(os.getcwd(), 'web/ui/templates'), os.path.join(os.getcwd(), 'web/ui/static/css')]

dev_server(app, extra_dirs=extra_dirs)
