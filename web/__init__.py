#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The main web tier module and helper methods to run a dev server"""
import argparse
import os
from typing import List, Optional

from flask import Flask


def collect_directory(extra_dir: str, extra_files: List[str]) -> None:
    """
    Recursively add file paths to the "extra_files" list.
    :param extra_dir: initial directory to scan recursively
    :param extra_files: target mutable aggregator for filenames
    """
    for dirname, directories, files in os.walk(extra_dir):
        for filename in files:
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                extra_files.append(filename)
        for directory in directories:
            collect_directory(directory, extra_files)


def collect_directories(extra_dirs: List[str], extra_files: List[str]) -> None:
    """
    Recursively scan list of directories for files and add their paths to the "extra_files" list.
    :param extra_dirs: list of directories to scan
    :param extra_files: target mutable aggregator for filenames
    """
    for extra_dir in extra_dirs:
        collect_directory(extra_dir, extra_files)


def argument_parser() -> argparse.ArgumentParser:
    """
    :return: a CLI argument parser for dev server usage. Allows:
        -d for debug mode
        -b/--bind for bind IP address
        -p/--port for the port
    """
    parser = argparse.ArgumentParser(description='run the standalone flask server')
    parser.add_argument('-d', action='store_true', required=False)
    parser.add_argument('-b', '--bind', type=str, help='the address to bind to', required=False)
    parser.add_argument('-p', '--port', type=int, help='the port to bind to', required=False)
    return parser


def dev_server(app: Flask, extra_dirs: Optional[List[str]] = None) -> None:
    """
    Run a development server
    :param app: the app to run (`Flask` or compatible)
    :param extra_dirs: extra directories to track for hot redeploy on changes
    """
    parser = argument_parser()
    args = parser.parse_args()

    extra_files = None
    if extra_dirs:
        extra_files = extra_dirs[:]
        collect_directories(extra_dirs, extra_files)

    app.run(host=args.bind, port=args.port, debug=args.d, extra_files=extra_files)
