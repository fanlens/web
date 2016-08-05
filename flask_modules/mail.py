#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.db import Config
from flask_mail import Mail

mail = Mail()


def setup_mail(app):
    web_config = Config('web')
    # todo turn off "allow less secure apps!"
    app.config['MAIL_SERVER'] = web_config['mail']['server']
    app.config['MAIL_PORT'] = web_config['mail']['port']
    app.config['MAIL_USERNAME'] = web_config['mail']['username']
    app.config['MAIL_PASSWORD'] = web_config['mail']['password']
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail.init_app(app)
