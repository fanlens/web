#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db
    from flask_modules.templating import setup_templating
    from .ui_ import ui
    from .landing import landing

    app = Flask(__name__)
    setup_db(app)
    setup_mail(app)
    setup_security(app)
    setup_templating(app)

    @app.route('/', methods=['HEAD'])
    def health():
        return 'ok'

    app.register_blueprint(landing)
    app.register_blueprint(ui, url_prefix='/v3/ui')
    return app


app = create_app()
