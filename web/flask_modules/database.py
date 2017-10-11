#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Database module"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from common.config import get_config
from common.db import Base

db = SQLAlchemy(metadata=Base.metadata)


def setup_db(app: Flask) -> None:
    """
    Set up database functionality for the app.
    :param app: the `Flask` app
    """
    config = get_config()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s' % \
                                            dict(config.items('DB'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
