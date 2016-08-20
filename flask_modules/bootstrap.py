#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap, WebCDN

bootstrap = Bootstrap()


def setup_bootstrap(app):
    bootstrap.init_app(app)
    app.extensions['bootstrap']['cdns']['bootstrap'] = WebCDN('/assets/')
    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN('/assets/js/')
