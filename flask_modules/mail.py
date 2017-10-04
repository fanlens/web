#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import get_config
from flask_mail import Mail

mail = Mail()


def setup_mail(app):
    config = get_config()
    app.config['MAIL_SERVER'] = config.get('MAIL', 'host')
    app.config['MAIL_PORT'] = config.get('MAIL', 'port')
    app.config['MAIL_USERNAME'] = config.get('MAIL', 'username')
    app.config['MAIL_PASSWORD'] = config.get('MAIL', 'password')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail.init_app(app)
