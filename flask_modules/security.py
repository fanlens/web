#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import g, jsonify, Flask, request
from flask_security import Security, SQLAlchemyUserDatastore, RoleMixin, UserMixin, auth_required, current_user
from flask_security.utils import verify_and_update_password, hash_password
from flask_wtf.csrf import CSRFProtect

from config.db import Config
from db.models.users import Role, User

from .database import db
from .jwt import create_jwt_for_user

csrf = CSRFProtect()
security = Security()
_demo_user = None


class WebRole(db.Model, RoleMixin, Role):
    pass


class WebUser(db.Model, UserMixin, User):
    pass


def setup_security(app: Flask, allow_login=False):
    web_config = Config('web')
    prefix = '/v4/user'
    app.config['SECRET_KEY'] = web_config['secret_key']
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = web_config['salt']  # unnecessary but required
    app.config['SECURITY_CONFIRMABLE'] = True
    app.config['SECURITY_REGISTERABLE'] = False
    app.config['SECURITY_RECOVERABLE'] = False
    app.config['SECURITY_CHANGEABLE'] = False
    app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization'
    app.config['SECURITY_TOKEN_AUTHENTICATION_KEY'] = 'auth_token'

    app.config['SECURITY_URL_PREFIX'] = prefix

    csrf.init_app(app)

    user_datastore = SQLAlchemyUserDatastore(db, WebUser, WebRole)

    security.init_app(app, user_datastore, register_blueprint=allow_login)

    @app.route('%s/swagger.json' % prefix, methods=['GET'])
    def get_definition():
        return jsonify(
            {
                "basePath": "/v4",
                "definitions": {
                    "Error": {
                        "properties": {
                            "error": {
                                "type": "string"
                            }
                        },
                        "type": "object"
                    }
                },
                "info": {
                    "description": "API related to users",
                    "title": "Fanlens User API",
                    "version": "4.0.0"
                },
                "paths": {
                    "/user": {
                        "get": {
                            "responses": {
                                "200": {
                                    "description": "User information",
                                    "schema": {
                                        "properties": {
                                            "active": {
                                                "type": "boolean"
                                            },
                                            "api_key": {
                                                "type": "string"
                                            },
                                            "confirmed_at": {
                                                "format": "date-time",
                                                "type": "string"
                                            },
                                            "email": {
                                                "format": "email",
                                                "type": "string"
                                            },
                                            "roles": {
                                                "items": {
                                                    "type": "string"
                                                },
                                                "type": "array",
                                                "uniqueItems": "true"
                                            }
                                        },
                                        "required": [
                                            "active",
                                            "confirmed_at",
                                            "email",
                                            "roles"
                                        ],
                                        "type": "object"
                                    }
                                },
                                "403": {
                                    "description": "not logged in",
                                    "schema": {
                                        "$ref": "#/definitions/Error"
                                    }
                                }
                            },
                            "summary": "get user data",
                            "tags": [
                                "user"
                            ]
                        }
                    },
                    "/user/token": {
                        "post": {
                            "parameters": [
                                {
                                    "in": "body",
                                    "name": "credentials",
                                    "required": "true",
                                    "schema": {
                                        "properties": {
                                            "email": {
                                                "type": "string",
                                                "format": "email"
                                            },
                                            "password": {
                                                "type": "string"
                                            }
                                        },
                                        "type": "object"
                                    }
                                }
                            ],
                            "responses": {
                                "200": {
                                    "description": "The users jwt token",
                                    "schema": {
                                        "properties": {
                                            "jwt": {
                                                "type": "string"
                                            },
                                        },
                                        "required": [
                                            "jwt"
                                        ],
                                        "type": "object"
                                    }
                                },
                                "400": {
                                    "description": "Bad request",
                                    "schema": {
                                        "$ref": "#/definitions/Error"
                                    }
                                },
                                "401": {
                                    "description": "Could not authenticate User",
                                    "schema": {
                                        "$ref": "#/definitions/Error"
                                    }
                                }
                            },
                            "summary": "Get a JWT Token",
                            "tags": [
                                "user"
                            ]
                        }
                    }
                },
                "produces": [
                    "application/json"
                ],
                "schemes": [
                    "https"
                ],
                "security": [
                    {
                        "api_key": []
                    }
                ],
                "securityDefinitions": {
                    "api_key": {
                        "in": "header",
                        "name": "Authorization-Token",
                        "type": "apiKey"
                    }
                },
                "swagger": "2.0"
            }
        )

    @app.route(prefix, methods=['GET'])
    @auth_required('token', 'session')
    def get_user():
        user = (current_user
                if current_user.has_role('tagger')
                else g.demo_user)
        return jsonify(email=user.email,
                       active=user.active,
                       confirmed_at=user.confirmed_at,
                       auth_token=current_user.get_auth_token(),
                       jwt=create_jwt_for_user(current_user),
                       roles=[role.name for role in user.roles])

    @app.route('%s/token' % prefix, methods=['POST'])
    @csrf.exempt
    def get_jwt():
        if current_user and current_user.is_authenticated:
            return jsonify(jwt=create_jwt_for_user(current_user))

        credentials = request.get_json(force=True)
        if not credentials or 'email' not in credentials or 'password' not in credentials:
            return jsonify(error="Incomplete credentials."), 400

        user = user_datastore.find_user(email=credentials['email'])
        if verify_and_update_password(credentials['password'], user):
            return jsonify(jwt=create_jwt_for_user(user))
        else:
            return jsonify(error="Could not authenticate user."), 401

    @app.before_first_request
    def fetch_demo_user():
        global _demo_user
        _demo_user = user_datastore.find_user(email="demo@example.com")

    @app.before_request
    def set_demo_user():
        g.demo_user = _demo_user
