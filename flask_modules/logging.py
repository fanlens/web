#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import get_config

logger = object


def setup_logging(app):
    config = get_config()
    app.config['PROPAGATE_EXCEPTIONS'] = config.getboolean('WEB', 'logexception', fallback=False)
    global logger
    logger = app.logger
