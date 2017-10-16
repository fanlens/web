"""CORS module"""
from typing import Any

from flask import Flask
from flask_cors import CORS

cors = CORS()


def setup_cors(app: Flask, **kwargs: Any) -> None:
    """
    Enable CORS for app
    :param app: the `Flask` app
    :param kwargs: additional parameters for CORS
    """
    cors.init_app(app, **kwargs)
