import typing
from flask import Flask, jsonify
from flask_jwt_simple import JWTManager, get_jwt_identity, create_jwt

from db.models.users import User

jwt = JWTManager()


def setup_jwt(app: Flask):
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_SECRET_KEY'] = 'super-secret'
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token():
        err_json = {
            "error": "JWT expired"
        }
        return jsonify(err_json), 403

    @jwt.invalid_token_loader
    def invalid_token(error):
        err_json = {
            "error": error
        }
        return jsonify(err_json), 400

    @jwt.unauthorized_loader
    def unauthorized(error):
        err_json = {
            "error": error
        }
        return jsonify(err_json), 401


class IdentityException(BaseException):
    pass


def current_user() -> dict:
    """:raises IdentityException if identity can't be loaded"""
    identity = get_jwt_identity()
    if not identity:
        raise IdentityException('no identity')
    if 'id' not in identity:
        raise IdentityException('id field missing')
    if 'roles' not in identity:
        raise IdentityException('roles field missing')
    return identity


def is_admin():
    """:raises IdentityException if identity can't be loaded"""
    user = current_user()
    return 'admin' in user['roles']


def current_user_id() -> int:
    """:raises IdentityException if identity can't be loaded"""
    user = current_user()
    return user['id']


def roles_any(*roles: typing.AnyStr):
    def wrapper(fun):
        def wrapped(*args, **kwargs):
            user = current_user()
            if user and set(user.get('roles', [])).intersection(roles):
                return fun(*args, **kwargs)
            else:
                return dict(error='Missing roles for this endpoint. Contact an admin.'), 403

        return wrapped

    return wrapper


def roles_all(*roles: typing.AnyStr):
    def wrapper(fun):
        def wrapped(*args, **kwargs):
            user = current_user()
            if user and set(user['roles']).issuperset(roles):
                return fun(*args, **kwargs)
            else:
                return dict(error='Missing roles for this endpoint. Contact an admin.'), 403

        return wrapped

    return wrapper


def create_jwt_for_user(user: User):
    return 'Bearer ' + create_jwt(identity=dict(id=user.id, roles=[role.name for role in user.roles]))
