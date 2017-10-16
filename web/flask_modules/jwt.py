
"""Database module"""
from functools import wraps
from typing import Any, Callable, Iterable

from flask import Flask, jsonify
from flask_jwt_simple import JWTManager, create_jwt, get_jwt_identity

from common.config import get_config
from common.db.models.users import User
from . import TJsonResponse

jwt = JWTManager()


def _expired_token() -> TJsonResponse:
    err_json = {"error": "JWT expired"}
    return jsonify(err_json), 403


def _invalid_token(error: str) -> TJsonResponse:
    err_json = {"error": error}
    return jsonify(err_json), 400


def _unauthorized(error: str) -> TJsonResponse:
    err_json = {"error": error}
    return jsonify(err_json), 401


def setup_jwt(app: Flask) -> None:
    """
    Set up JWT handling for the app
    :param app: the `Flask` app
    """
    config = get_config()
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ALGORITHM'] = 'HS256'
    app.config['JWT_SECRET_KEY'] = config.get('WEB', 'jwt_secret_key')
    jwt.init_app(app)

    jwt.expired_token_loader(_expired_token)
    jwt.invalid_token_loader(_invalid_token)
    jwt.unauthorized_loader(_unauthorized)


class IdentityException(BaseException):
    """For JWT identity exceptions"""
    pass


def current_user() -> dict:
    """:raises IdentityException if identity can't be loaded"""
    identity: dict = get_jwt_identity()
    if not identity:
        raise IdentityException('no identity')
    if 'id' not in identity:
        raise IdentityException('id field missing')
    if 'roles' not in identity:
        raise IdentityException('roles field missing')
    return identity


def is_admin() -> bool:
    """:raises IdentityException if identity can't be loaded"""
    user = current_user()
    roles: Iterable[str] = user['roles']
    return 'admin' in roles


def current_user_id() -> int:
    """:raises IdentityException if identity can't be loaded"""
    user = current_user()
    user_id: int = user['id']
    return user_id


def roles_any(*roles: str) -> Callable[[Callable[..., TJsonResponse]], Callable[..., TJsonResponse]]:
    """
    Decorator which limits access to users possessing at least one of the roles specified
    :param roles: the roles
    :return: the decorator
    """

    def _wrapper(fun: Callable[..., TJsonResponse]) -> Callable[..., TJsonResponse]:
        @wraps(fun)
        def _wrapped(*args: Any, **kwargs: Any) -> TJsonResponse:
            user = current_user()
            if user and set(user.get('roles', [])).intersection(roles):
                return fun(*args, **kwargs)
            return dict(error='Missing roles for this endpoint. Contact an admin.'), 403

        return _wrapped

    return _wrapper


def roles_all(*roles: str) -> Callable[[Callable[..., TJsonResponse]], Callable[..., TJsonResponse]]:
    """
    Decorator which limits access to users possessing at least one of the roles specified
    :param roles: the roles
    :return: the decorator
    """

    def _wrapper(fun: Callable[..., TJsonResponse]) -> Callable[..., TJsonResponse]:
        @wraps(fun)
        def _wrapped(*args: Any, **kwargs: Any) -> TJsonResponse:
            user = current_user()
            if user and set(user['roles']).issuperset(roles):
                return fun(*args, **kwargs)
            return dict(error='Missing roles for this endpoint. Contact an admin.'), 403

        return _wrapped

    return _wrapper


def create_jwt_for_user(user: User) -> str:
    """
    Creates a JWT for the `User`. The token contains the user id and her roles.
    {
        identity: {
            id: user.id
            roles: ['a', 'b',...]
        }
    }
    :param user: `User` to create the JWT for
    :return: proper JWT as string
    """
    user_jwt: str = create_jwt(identity=dict(id=user.id, roles=[role.name for role in user.roles]))
    return 'Bearer ' + user_jwt
