#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

from config.env import Environment
from db import Base

db = SQLAlchemy(metadata=Base.metadata)


def setup_db(app):
    env = Environment()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(username)s:%(password)s@%(host)s:%(port)s/%(database)s' % \
                                            env['DB']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.before_first_request
    def before_first_request():
        db.create_all()
