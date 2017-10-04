from flask import Flask
from flask_cors import CORS

cors = CORS()


def setup_cors(app: Flask, **kwargs):
    cors.init_app(app, **kwargs)
