#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db
    from flask_modules.templating import setup_templating
    from flask_modules.logging import setup_logging

    app = Flask(__name__)
    setup_logging(app)
    setup_db(app)
    setup_mail(app)
    setup_security(app)
    setup_templating(app)

    @app.route('/', methods=['HEAD'])
    def health():
        return 'ok'

    from .index import index

    app.register_blueprint(index)
    return app


app = create_app()
