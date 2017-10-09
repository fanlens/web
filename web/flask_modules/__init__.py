#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This package contains ready configured and set up flask modules"""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple, Union

from connexion.operation import Operation
from connexion.resolver import Resolution, Resolver
from flask import Flask, Response, request

TJson = Dict[str, Any]
TJsonResponse = Union[TJson, Tuple[TJson, int]]
TResponse = Union[Response, TJsonResponse]


class NotInitializedException(RuntimeError):
    """Exception class to handle uninitialized Flask Modules"""
    pass


class FlaskModule(ABC):
    """Base class for custom `Flask` modules"""

    def __init__(self, app: Optional[Flask] = None) -> None:
        """
        :param app: the `Flask` app, if None init_app needs to be used later. Allows for lazy init.
        """
        self.app = app

        if app is not None:
            self.init_app(app)

    @abstractmethod
    def init_app(self, app: Flask) -> None:
        """
        :param app: the `Flask` app to initialize
        """
        raise NotImplementedError("Must be implemented by subclass")


def request_wants_json() -> bool:
    """Helper method to check whether request expects a JSON response"""
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return bool(best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html'])


class SimpleResolver(Resolver):
    """
    A custom `connexion` `Resolver` that works without relying on operation ids
    paths are translated into methods by joining the path with '_', removing '{}'s
    e.g. /hello/world:
            get
    will be resolved to
    hello_world_get()
    a plain / will be resolved to 'root'
    """

    def __init__(self, controller_module: object) -> None:
        """
        :param controller_module: the python module where the path implementations can be found
        """
        super().__init__(lambda _: _)  # we do it our own way, see resolve
        self._controller_module = controller_module

    def resolve(self, operation: Operation) -> Resolution:
        """
        :param operation: operation which will be resolved for this module
        :return: a resolved endpoint
        """
        parts = []
        if operation.path == '/':
            parts.append('root')
        else:
            for part in operation.path.split('/'):
                if part:
                    parts.append(part)
        parts.append(operation.method)
        func_name = '_'.join(parts).replace('{', '').replace('}', '')
        func = getattr(self._controller_module, func_name)

        return Resolution(func, func_name)


_TDecorator = Callable[[Callable[..., TJsonResponse]], Callable[..., TJsonResponse]]


def annotation_composer(*decs: _TDecorator) -> _TDecorator:
    """
    small helper that combines multiple decorators into a single one
    :param decs: the decorators to combine, will be applied right to left, e.g.:
        annotation_composer(f, g, h) -> f(g(h(x)))
    :return: combined decorations
    """

    def deco(fun: Callable[..., TJsonResponse]) -> Callable[..., TJsonResponse]:
        """
        :param fun: function to decorate
        :return: decorated function
        """
        for dec in reversed(decs):
            fun = wraps(fun)(dec(fun))
        return fun

    return deco


def bad_arg(err: ValueError) -> TJsonResponse:
    """
    :param err: a ValueError
    :return: a ValueError turned into a proper response
    """
    msg, = err.args
    return dict(error=msg), 400


def simple_response(msg: str, status: int = 200, **kwargs: Any) -> TJsonResponse:
    """
    create a quick "ok" json message
    :param msg: the message text
    :param status: the status code to use, default 200
    :param kwargs: additional properties for the returned json object
    :return: a json object of the form
        {"ok":`msg`, **kwargs}
    """
    return dict(ok=msg, **kwargs), status


def ok_response(**kwargs: Any) -> TJsonResponse:
    """:return: a quick "ok" json response"""
    return simple_response('ok', **kwargs)


def updated_response(**kwargs: Any) -> TJsonResponse:
    """:return: a quick "updated" json response"""
    return simple_response('updated', **kwargs)


def deleted_response(**kwargs: Any) -> TJsonResponse:
    """:return: a quick "deleted" json response"""
    return simple_response('deleted', **kwargs)
