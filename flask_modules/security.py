#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import g
from flask_security import Security, SQLAlchemyUserDatastore, RoleMixin, UserMixin
from flask_wtf.csrf import CsrfProtect

from flask_modules.database import db
from db.models.users import Role, User
from config.db import Config

csrf = CsrfProtect()
security = Security()
_demo_user = None


class WebRole(db.Model, Role, RoleMixin):
    pass


class WebUser(db.Model, UserMixin, User):
    pass


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
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization-Token'
    app.config['SECURITY_TOKEN_AUTHENTICATION_KEY'] = 'api_key'

    csrf.init_app(app)

    user_datastore = SQLAlchemyUserDatastore(db, WebUser, WebRole)
    security.init_app(app, user_datastore)

    @app.before_first_request
    def fetch_demo_user():
        global _demo_user
        _demo_user = user_datastore.find_user(email="demo@example.com")

    @app.before_request
    def set_demo_user():
        g.demo_user = _demo_user
