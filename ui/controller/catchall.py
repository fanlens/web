#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, Blueprint, g
from flask_security import current_user

catchall = Blueprint('index', __name__)


@catchall.route('/', defaults={'path': ''})
@catchall.route('/<path:path>')
def root(path):
    return render_template('ui.html',
                           api_key=(
                               current_user.get_auth_token()
                               if current_user.has_role('tagger')
                               else g.demo_user.get_auth_token()),
                           path=path)
