#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""web entry point for local dev server"""

import argparse
import sys
import os

# fix python path for running as python -mweb
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from login import app

parser = argparse.ArgumentParser(description='run the standalone flask server')
parser.add_argument('-d', action='store_true', required=False)
parser.add_argument('-b', '--bind', type=str, help='the address to bind to', required=False)
parser.add_argument('-p', '--port', type=int, help='the port to bind to', required=False)
args = parser.parse_args()

extra_dirs = [os.path.join(os.getcwd(), 'web/login/static'), os.path.join(os.getcwd(), 'web/login/templates')]
extra_files = extra_dirs[:]


def walk_dir(extra_dir):
    for dirname, dirs, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)
        for dir in dirs:
            walk_dir(dir)


for extra_dir in extra_dirs:
    walk_dir(extra_dir)


app.run(host=args.bind, port=args.port, debug=args.d, extra_files=extra_files)
