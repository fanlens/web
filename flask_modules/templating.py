#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

def setup_templating(app):
    blueprint = Blueprint(
        'templating',
        __name__,
        template_folder='templates')

    app.register_blueprint(blueprint)
    return app
