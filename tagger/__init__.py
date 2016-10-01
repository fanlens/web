#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""base module for web guis"""

import connexion

from flask import send_from_directory, Blueprint

from flask_modules import SimpleResolver
from flask_modules.celery import setup_celery
from flask_modules.database import setup_db
from flask_modules.redis import setup_redis
from flask_modules.mail import setup_mail
from flask_modules.security import setup_security
from flask_modules.templating import setup_templating


def create_app():
    app = connexion.App(__name__, specification_dir='swagger')

    setup_db(app.app)
    setup_redis(app.app)
    setup_mail(app.app)
    setup_security(app.app)
    setup_celery(app.app)
    setup_templating(app.app)

    @app.app.route('/', methods=['HEAD'])
    def httpchk():
        return 'ok'

    @app.route('/v2/tagger/static/<path:filename>')
    def send_files(filename):
        return send_from_directory('static', filename)

    from tagger.controller import tagger, eev
    app.add_api('tagger.yaml', validate_responses=True, resolver=SimpleResolver(tagger))
    app.add_api('eev.yaml', validate_responses=True, resolver=SimpleResolver(eev))

    return app


app = create_app()
