#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""web entry point"""

import argparse
import sys
import os

# fix python path for running as python -mweb
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from web import app

parser = argparse.ArgumentParser(description='run the standalone flask server')
parser.add_argument('-d', action='store_true', required=False)
parser.add_argument('-b', '--bind', type=str, help='the address to bind to', required=False)
parser.add_argument('-p', '--port', type=int, help='the port to bind to', required=False)
args = parser.parse_args()

app.run(host=args.bind, port=args.port, debug=args.d)
