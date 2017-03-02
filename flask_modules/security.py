#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.db import Config
from db.models.users import Role, User
from flask import g, jsonify
from flask_modules.database import db
from flask_security import Security, SQLAlchemyUserDatastore, RoleMixin, UserMixin, auth_required, current_user
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
security = Security()
_demo_user = None


class WebRole(db.Model, RoleMixin, Role):
    pass


class WebUser(db.Model, UserMixin, User):
    pass


def setup_security(app):
    web_config = Config('web')
    app.config['SECRET_KEY'] = web_config['secret_key']
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = web_config['salt']  # unnecessary but required
    app.config['SECURITY_URL_PREFIX'] = '/v3/user'
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_REGISTERABLE'] = True
    app.config['SECURITY_RECOVERABLE'] = False
    app.config['SECURITY_CHANGEABLE'] = False
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization-Token'
    app.config['SECURITY_TOKEN_AUTHENTICATION_KEY'] = 'api_key'

    csrf.init_app(app)

    user_datastore = SQLAlchemyUserDatastore(db, WebUser, WebRole)
    security.init_app(app, user_datastore)

    @app.route('/v3/user/swagger.json', methods=['GET'])
    def get_definition():
        return jsonify({"swagger": "2.0", "info": {"title": "Fanlens User API", "version": "3.0.0",
                                                   "description": "API related to users"}, "schemes": ["https"],
                        "basePath": "/v3", "securityDefinitions": {
                "api_key": {"type": "apiKey", "name": "Authorization-Token", "in": "header"}},
                        "security": [{"api_key": []}], "produces": ["application/json"], "paths": {"/user": {
                "get": {"summary": "get user data", "tags": ["user"], "responses": {
                    "200": {"description": "A token and associated conversationId",
                            "schema": {"type": "object", "required": ["active", "confirmed_at", "email", "roles"],
                                       "properties": {"active": {"type": "boolean"}, "api_key": {"type": "string"},
                                                      "confirmed_at": {"type": "string", "format": "date-time"},
                                                      "email": {"type": "string", "format": "email"},
                                                      "roles": {"type": "array", "uniqueItems": "true",
                                                                "items": {"type": "string"}}}}},
                    "403": {"description": "not logged in", "schema": {"$ref": "#/definitions/Error"}}}}}},
                        "definitions": {"Error": {"type": "object", "properties": {"error": {"type": "string"}}}}})

    @app.route('/v3/user', methods=['GET'])
    @auth_required('token', 'session')
    def get_user():
        user = (current_user
                if current_user.has_role('tagger')
                else g.demo_user)
        return jsonify(email=user.email, active=user.active, confirmed_at=user.confirmed_at,
                       api_key=user.get_auth_token(),
                       roles=[role.name for role in user.roles])


    @app.before_first_request
    def fetch_demo_user():
        global _demo_user
        _demo_user = user_datastore.find_user(email="demo@example.com")

    @app.before_request
    def set_demo_user():
        g.demo_user = _demo_user
