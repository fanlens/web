#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_wtf.csrf import CsrfProtect

from .database import db
from ..model.user import User, Role
from config.db import Config

csrf = CsrfProtect()
security = Security()


def setup_security(app):
    web_config = Config('web')
    app.config['SECRET_KEY'] = web_config['secret_key']
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = web_config['salt']  # unnecessary but required
    app.config['SECURITY_URL_PREFIX'] = '/user'
    app.config['SECURITY_CONFIRMABLE'] = False
    app.config['SECURITY_REGISTERABLE'] = False
    app.config['SECURITY_RECOVERABLE'] = False
    app.config['SECURITY_CHANGEABLE'] = False

    csrf.init_app(app)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
