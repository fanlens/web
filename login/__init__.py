#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db

    app = Flask(__name__)
    setup_db(app)
    setup_mail(app)
    setup_security(app)
    return app


app = create_app()


@app.route('/', methods=['HEAD'])
def httpchk():
    return 'ok'
