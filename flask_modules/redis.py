#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_redis import FlaskRedis

from config.db import Config

redis_store = FlaskRedis(strict=True)


def setup_redis(app):
    web_config = Config('web')
    app.config['REDIS_URL'] = web_config['redis']['url']
    redis_store.init_app(app)
    return app
