#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""web entry point for local dev server"""

import os
import sys

# fix python path for running as python -mweb
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

# path needs to be fixed pylint: disable=wrong-import-position
from web.api import app
from web import dev_server

EXTRA_DIRS = [os.path.join(os.getcwd(), sub_path) for sub_path in
              ('web/api/templates', 'web/api/static', 'web/api/swagger')]

dev_server(app, extra_dirs=EXTRA_DIRS)
