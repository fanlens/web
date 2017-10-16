"""Caching module"""

from flask import Flask
from flask_cache import Cache

from common.config import get_config

cache = Cache()


def setup_cache(app: Flask) -> None:
    """
    Add caching capabilities
    :param app: the `Flask` app
    """
    config = get_config()
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = 'redis://%(username)s:%(password)s@%(host)s:%(port)d/%(db)d' % dict(
        username=config.get('REDIS', 'username'),
        password=config.get('REDIS', 'password'),
        host=config.get('REDIS', 'host'),
        port=config.getint('REDIS', 'port'),
        db=0
    )
    cache.init_app(app)
