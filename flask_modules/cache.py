#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_cache import Cache

from config import get_config

cache = Cache()


def setup_cache(app: Flask) -> Flask:
    config = get_config()
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = 'redis://%(username)s:%(password)@%(host)s:%(port)d/%(db)d' % dict(
        username=config.get('REDIS', 'username'),
        password=config.get('REDIS', 'password'),
        host=config.get('REDIS', 'host'),
        port=config.getint('REDIS', 'port'),
        db=0
    )
    cache.init_app(app)
    return app
