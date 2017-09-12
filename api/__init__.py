#!/usr/bin/env python
# -*- coding: utf-8 -*-


def create_app():
    import connexion

    from flask_modules.celery import setup_celery
    from flask_modules.database import setup_db
    from flask_modules.mail import setup_mail
    from flask_modules.jwt import setup_jwt
    from flask_modules.cors import setup_cors
    from flask_modules.logging import setup_logging

    app = connexion.App(__name__, specification_dir='swagger')

    setup_logging(app.app)
    setup_db(app.app)
    setup_mail(app.app)
    setup_jwt(app.app)
    setup_cors(app.app)
    setup_celery(app.app)

    from flask_modules import SimpleResolver
    from .controller import activities, model
    app.add_api('activities.yaml', validate_responses=True, resolver=SimpleResolver(activities))
    app.add_api('model.yaml', validate_responses=True, resolver=SimpleResolver(model))
    app.add_url_rule('/', 'health', lambda: 'ok')

    return app


app = create_app()
