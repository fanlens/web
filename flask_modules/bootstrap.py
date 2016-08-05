#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap, StaticCDN, WebCDN

bootstrap = Bootstrap()


def setup_bootstrap(app):
    bootstrap.init_app(app)
    app.extensions['bootstrap']['cdns']['bootstrap'] = StaticCDN()
    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN('/v1/tagger/js/')
