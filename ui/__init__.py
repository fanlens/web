#!/usr/bin/env python
# -*- coding: utf-8 -*-


def create_app():
    import connexion

    from flask_modules.mail import setup_mail
    from flask_modules.jwt import setup_jwt
    from flask_modules.security import setup_security
    from flask_modules.cors import setup_cors
    from flask_modules.database import setup_db
    from flask_modules.logging import setup_logging
    from flask_modules.celery import setup_celery
    from flask_modules.twitter import setup_twitter

    app = connexion.App(__name__, specification_dir='swagger')

    setup_logging(app.app)
    setup_db(app.app)
    setup_mail(app.app)
    setup_jwt(app.app)
    setup_security(app.app, allow_login=True)
    setup_cors(app.app, resources={"/static/fonts/*": {"origins": "*"}})
    setup_celery(app.app)
    setup_twitter(app.app)

    from flask_modules import SimpleResolver
    from .controller.ui import ui, ui_nonauth
    from .controller.landing import landing
    from .controller.forwards import forwards
    from .controller import ui_api, twitter, eev

    app.app.register_blueprint(ui_nonauth)
    app.app.register_blueprint(ui)
    app.app.register_blueprint(forwards)
    app.app.register_blueprint(landing)
    app.add_api('ui.yaml', validate_responses=True, resolver=SimpleResolver(ui_api))
    app.add_api('twitter.yaml', validate_responses=True, resolver=SimpleResolver(twitter))
    app.add_api('eev.yaml', validate_responses=True, resolver=SimpleResolver(eev))
    app.add_url_rule('/', 'health', lambda: 'ok', methods=['HEAD'])
    return app


app = create_app()
