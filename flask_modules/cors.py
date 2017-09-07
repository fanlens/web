from flask import Flask
from flask_cors import CORS


def setup_cors(app: Flask, **kwargs):
    CORS(**kwargs).init_app(app)
