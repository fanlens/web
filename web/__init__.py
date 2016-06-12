#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""base module for web guis"""

from flask import Flask

from web.modules.bootstrap import setup_bootstrap
from web.modules.celery import setup_celery
from web.modules.database import setup_db
from web.modules.mail import setup_mail
from web.modules.security import setup_security


def create_app():
    app = Flask(__name__)

    setup_db(app)
    setup_mail(app)
    setup_security(app)
    setup_celery(app)
    setup_bootstrap(app)

    from web.routes.index import index
    from web.routes.tagger import tagger
    from web.routes.meta import meta
    from web.routes.tagset import tagset
    app.register_blueprint(index, url_prefix='/')
    app.register_blueprint(tagger, url_prefix='/tagger')
    app.register_blueprint(meta, url_prefix='/meta')
    app.register_blueprint(tagset, url_prefix='/tagset')
    return app

app = create_app()