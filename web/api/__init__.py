#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""API microservice porviding the activities and model APIs"""

from connexion import App
from flask import Flask


def setup_app(flask_app: Flask) -> None:
    """
    Setup the flask modules used in the app
    :param flask_app: the app
    """
    from ..flask_modules.celery import setup_celery
    from ..flask_modules.database import setup_db
    from ..flask_modules.mail import setup_mail
    from ..flask_modules.jwt import setup_jwt
    from ..flask_modules.cors import setup_cors
    from ..flask_modules.logging import setup_logging

    setup_logging(flask_app)
    setup_db(flask_app)
    setup_mail(flask_app)
    setup_jwt(flask_app)
    setup_cors(flask_app)
    setup_celery(flask_app)


def create_app() -> App:
    """:return: lazily created and initialized app"""

    new_app = App(__name__, specification_dir='swagger')
    setup_app(new_app.app)

    from ..flask_modules import SimpleResolver
    from .controller import activities, model
    new_app.add_api('activities.yaml', validate_responses=True, resolver=SimpleResolver(activities))
    new_app.add_api('model.yaml', validate_responses=True, resolver=SimpleResolver(model))
    new_app.add_url_rule('/', 'health', lambda: 'ok')

    return new_app


app = create_app()
