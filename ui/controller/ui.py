#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import render_template, Blueprint, g, send_file, request, redirect
from flask_security import current_user, login_required
from config.db import Config

ui = Blueprint('ui', __name__, url_prefix='/v4/ui')
ui_nonauth = Blueprint('ui_nonauth', __name__)

config = None


@ui.before_app_first_request
def setup_conf():
    global config
    config = Config('eev')


@ui.route('/static/app.js')
def appjs():
    return send_file('static/app.js')


def hand_off_to_app(path):
    return render_template('ui.html',
                           bot_id=config["client_id"],
                           api_key=(
                               current_user.get_auth_token()
                               if current_user.has_role('tagger')
                               else g.demo_user.get_auth_token()),
                           path=path)


@ui_nonauth.route('/legal')
@ui_nonauth.route('/team')
@ui_nonauth.route('/enterprise')
def nonauth():
    return hand_off_to_app(request.path)


@ui_nonauth.route('/v3/<path:path>')
def redir_old_new(path):
    return redirect('/v4/' + path)


@ui.route('/', defaults={'path': ''})
@ui.route('/<path:path>')
@login_required
def root(path):
    return hand_off_to_app(path)
