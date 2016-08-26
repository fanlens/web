#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_security import login_required, current_user


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db
    from flask_modules.templating import setup_templating

    app = Flask(__name__, static_url_path='/user/static/')
    setup_db(app)
    setup_mail(app)
    setup_security(app)
    setup_templating(app)
    return app


app = create_app()


@app.route('/', methods=['HEAD'])
def httpchk():
    return 'ok'


@app.route('/user/token', methods=['GET'])
@login_required
def token():
    return render_template('security/token.html', api_key=current_user.get_auth_token())
