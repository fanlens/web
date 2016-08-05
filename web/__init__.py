#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""base module for web guis"""

from flask import Flask

from flask_modules.bootstrap import setup_bootstrap
from flask_modules.celery import setup_celery
from flask_modules.database import setup_db
from flask_modules.mail import setup_mail
from flask_modules.security import setup_security


def create_app():
    app = Flask(__name__, static_url_path='/v1/tagger')

    setup_db(app)
    setup_mail(app)
    setup_security(app)
    setup_celery(app)
    setup_bootstrap(app)

    from web.routes.tagger import tagger
    from web.routes.meta import meta
    app.register_blueprint(tagger, url_prefix='/v1/tagger')
    app.register_blueprint(meta, url_prefix='/v1/meta')
    return app


app = create_app()
