#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Wrapping the app logger into a module for easier access in non standard `Flask` controllers"""
from logging import LoggerAdapter

from flask import Flask

from common.config import get_config
from . import FlaskModule


class Logger(FlaskModule, LoggerAdapter):
    """Wraps the app logger into a flask module"""

    def init_app(self, app: Flask) -> None:
        app.config.setdefault('PROPAGATE_EXCEPTIONS', False)
        LoggerAdapter.__init__(self, app.logger, {})


logger = Logger()


def setup_logging(app: Flask) -> None:
    """
    Set up logging for app
    :param app: the `Flask` app
    """
    config = get_config()
    app.config['PROPAGATE_EXCEPTIONS'] = config.getboolean('WEB', 'logexception', fallback=False)
    logger.init_app(app)
