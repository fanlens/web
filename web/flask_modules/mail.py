#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mailing module"""

from flask import Flask
from flask_mail import Mail

from common.config import get_config

mail = Mail()


def setup_mail(app: Flask) -> None:
    """
    Set up mailing for the app
    :param app: the `Flask` app
    """
    config = get_config()
    app.config['MAIL_SERVER'] = config.get('MAIL', 'host')
    app.config['MAIL_PORT'] = config.get('MAIL', 'port')
    app.config['MAIL_USERNAME'] = config.get('MAIL', 'username')
    app.config['MAIL_PASSWORD'] = config.get('MAIL', 'password')
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    mail.init_app(app)
