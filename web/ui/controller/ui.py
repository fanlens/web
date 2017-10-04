#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, Blueprint, g, send_file, request, redirect
from flask_security import current_user, login_required

from common.config import get_config
from ...flask_modules.jwt import create_jwt_for_user

_config = get_config()

ui = Blueprint('ui', __name__, url_prefix='/%s/ui' % _config.get('DEFAULT', 'version'))
ui_nonauth = Blueprint('ui_nonauth', __name__)


@ui.route('/static/app.js')
def appjs():
    return send_file('static/app.js')


def hand_off_to_app(path):
    return render_template('ui.html',
                           bot_id=_config.get("BOT", "client_id"),
                           jwt=create_jwt_for_user(current_user
                                                   if current_user.has_role('tagger')
                                                   else g.demo_user),
                           auth_token=(
                               current_user.get_auth_token()
                               if current_user.has_role('tagger')
                               else g.demo_user.get_auth_token()),
                           path=path,
                           version=_config.get('DEFAULT', 'version'))


@ui_nonauth.route('/legal')
@ui_nonauth.route('/team')
@ui_nonauth.route('/enterprise')
def nonauth():
    return hand_off_to_app(request.path)


@ui_nonauth.route('/v1/<path:path>')
@ui_nonauth.route('/v2/<path:path>')
@ui_nonauth.route('/v3/<path:path>')
def redir_old_new(path):
    return redirect('/%s/%s' % (_config.get('DEFAULT', 'version'), path))


@ui.route('/', defaults={'path': ''})
@ui.route('/<path:path>')
@login_required
def root(path):
    return hand_off_to_app(path)
