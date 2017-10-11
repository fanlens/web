#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""User interface layer of the web tier."""
from connexion import App
from flask import Flask


def setup_app(flask_app: Flask) -> None:
    """
    Setup the flask modules used in the app
    :param flask_app: the app
    """
    from ..flask_modules.mail import setup_mail
    from ..flask_modules.jwt import setup_jwt
    from ..flask_modules.security import setup_security
    from ..flask_modules.cors import setup_cors
    from ..flask_modules.database import setup_db
    from ..flask_modules.logging import setup_logging
    from ..flask_modules.celery import setup_celery
    from ..flask_modules.twitter import setup_twitter

    setup_logging(flask_app)
    setup_db(flask_app)
    setup_mail(flask_app)
    setup_jwt(flask_app)
    setup_security(flask_app, allow_login=True)
    setup_cors(flask_app, resources={"/static/fonts/*": {"origins": "*"}})
    setup_celery(flask_app)
    setup_twitter(flask_app)


def create_app() -> App:
    """:return: lazily created and initialized app"""

    new_app = App(__name__, specification_dir='swagger')
    setup_app(new_app.app)

    from ..flask_modules import SimpleResolver
    from .controller.ui import UI_BP, UI_NONAUTH_BP
    from .controller.landing import LANDING_BP
    from .controller.forwards import FORWARDS_BP
    from .controller import ui_api, twitter, eev

    new_app.app.register_blueprint(UI_NONAUTH_BP)
    new_app.app.register_blueprint(UI_BP)
    new_app.app.register_blueprint(FORWARDS_BP)
    new_app.app.register_blueprint(LANDING_BP)
    new_app.add_api('ui.yaml', validate_responses=True, resolver=SimpleResolver(ui_api))
    new_app.add_api('twitter.yaml', validate_responses=True, resolver=SimpleResolver(twitter))
    new_app.add_api('eev.yaml', validate_responses=True, resolver=SimpleResolver(eev))
    new_app.add_url_rule('/', 'health', lambda: 'ok', methods=['HEAD'])
    return new_app


app = create_app()
