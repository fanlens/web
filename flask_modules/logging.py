#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from logging import Logger

logger = object  # type: Logger


def setup_logging(app):
    app.config['PROPAGATE_EXCEPTIONS'] = None if os.environ.get('FL_WEB_LOGEXCEPTION') != 'True' else True
    global logger
    logger = app.logger
