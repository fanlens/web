#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Security relevant modules and configurations."""

from typing import Optional, Tuple

from flask import Flask, g, jsonify, request
from flask_security import RoleMixin, SQLAlchemyUserDatastore, Security, UserMixin, auth_required, current_user
from flask_security.utils import verify_and_update_password
from flask_wtf.csrf import CSRFProtect

from common.config import get_config
from common.db.models.users import Role, User
from .database import db
from .jwt import create_jwt_for_user

csrf = CSRFProtect()
security = Security()

# will be set in before_first_request
# then it will be populated to `g` for the requests
_DEMO_USER: Optional[User] = None


class WebRole(db.Model, RoleMixin, Role):
    # pylint: disable=too-few-public-methods
    """Web tier view of the `Role` model"""
    pass


class WebUser(db.Model, UserMixin, User):
    # pylint: disable=too-few-public-methods
    """Web tier view of the `User` model"""
    pass


def setup_security(app: Flask, allow_login: bool = False) -> None:
    """
    :param app: the Flask app
    :param allow_login: allow the service to provide login/user management routes.
    """
    config = get_config()
    prefix = '/%s/user' % config.get('DEFAULT', 'version')
    app.config['SECRET_KEY'] = config.get('WEB', 'secret_key')
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    app.config['SECURITY_PASSWORD_SALT'] = config.get('WEB', 'salt')  # unnecessary but required
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

    # adding user related routes to the app pylint: disable=unused-variable
    @app.route('%s/swagger.json' % prefix, methods=['GET'])
    def get_definition() -> str:
        """ :return: the Swagger definition for the user endpoints. """
        swagger_json: str = jsonify(
            {
                "basePath": "/" + config.get('DEFAULT', 'version'),
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
            })
        return swagger_json

    @app.route(prefix, methods=['GET'])
    @auth_required('token', 'session')
    def get_user() -> str:
        """
        Get a JSON-fied user object including a JWT to be used for api endpoints.
        The user needs to have a proper auth token / login session in order to exchange it for a JWT that can be used
        in a non session context.
        :return: the JSON-fied user object.
        """
        user = (current_user
                if current_user.has_role('tagger')
                else g.demo_user)
        user_json: str = jsonify(email=user.email,
                                 active=user.active,
                                 confirmed_at=user.confirmed_at,
                                 auth_token=current_user.get_auth_token(),
                                 jwt=create_jwt_for_user(current_user),
                                 roles=[role.name for role in user.roles])
        return user_json

    @app.route('%s/token' % prefix, methods=['POST'])
    @csrf.exempt
    def get_jwt() -> Tuple[str, int]:
        """
        Get a JWT to use for accessing the api.
        Works outside of a session context by posting the user credentials. This is conceptually equivalent to logging
        in via the login form.
        :return: JWT provided via a JSON object (or error)
        """
        if current_user and current_user.is_authenticated:
            return jsonify(jwt=create_jwt_for_user(current_user)), 200

        credentials = request.get_json(force=True)
        if not credentials or 'email' not in credentials or 'password' not in credentials:
            return jsonify(error="Incomplete credentials."), 400

        user = user_datastore.find_user(email=credentials['email'])
        if verify_and_update_password(credentials['password'], user):
            jwt_json: str = jsonify(jwt=create_jwt_for_user(user))
            return jwt_json, 200

        jwt_error_json: str = jsonify(error="Could not authenticate user.")
        return jwt_error_json, 401

    @app.before_first_request
    def fetch_demo_user() -> None:
        """populate the demo user object"""
        global _DEMO_USER  # populate after everything is set up pylint: disable=global-statement
        _DEMO_USER = user_datastore.find_user(email="demo@example.com")

    @app.before_request
    def set_demo_user() -> None:
        """populate g demo user"""
        g.demo_user = _DEMO_USER
