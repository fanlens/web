#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_cache import Cache

from config.db import Config

cache = Cache()


def setup_cache(app: Flask) -> Flask:
    web_config = Config('redis')
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = web_config['connection_string']
    cache.init_app(app)
    return app
