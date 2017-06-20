#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from config.db import Config
from flask import session
from flask_security import current_user
from flask_security.decorators import roles_accepted, auth_token_required, login_required

eev_config = None
DIRECTLINE_BASE_PATH = 'https://directline.botframework.com/v3/directline'
TOKEN_API = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
GRANT_TYPE = "grant_type=client_credentials&client_id=%(client_id)s&client_secret=%(client_secret)s&scope=https%%3A%%2F%%2Fapi.botframework.com%%2F.default"
STATE_BASE_PATH = "https://state.botframework.com/v3"


def _get_eev_config():
    global eev_config
    if not eev_config:
        eev_config = Config('eev')
    return eev_config


def _fetch_new():
    # {
    #    "conversationId": "abc123",
    #    "token": "RCurR_XV9ZA.cwA.BKA.iaJrC8xpy8qbOF5xnR2vtCX7CZj0LdjAPGfiCpg4Fv0y8qbOF5xPGfiCpg4Fv0y8qqbOF5x8qbOF5xn",
    #    "expires_in": 1800
    # }
    eev_config = _get_eev_config()
    resp = requests.post(DIRECTLINE_BASE_PATH + "/tokens/generate",
                         headers=dict(Authorization="Bearer %s" % eev_config['secret']))

    if resp.status_code != 200:
        return dict(error="could not connect to eev: " + resp.text), 500
    else:
        session['eev'] = resp.json()
        return session['eev']


def _refresh():
    assert 'eev' in session
    resp = requests.post(DIRECTLINE_BASE_PATH + "/tokens/refresh",
                         headers=dict(Authorization="Bearer %s" % session['eev']['token']))
    if resp.status_code != 200:
        return _fetch_new()
    else:
        session['eev'] = resp.json()
        return session['eev']


@auth_token_required
@roles_accepted('admin', 'tagger')
def token_post() -> str:
    if 'eev' in session:
        return _refresh()
    else:
        return _fetch_new()


def _set_session_data(channel_id, user_id, auth_token, name) -> bool:
    eev_config = _get_eev_config()
    data_obj = {"data": {"auth_token": auth_token, "name": name}, "etag": "*"}
    token_req = requests.post(TOKEN_API,
                              data=GRANT_TYPE % dict(client_id=eev_config['client_id'],
                                                     client_secret=eev_config['client_secret']))

    access_token = token_req.json().get('access_token', '')

    # todo: one should use the serviceUrl property of the original botframework message, addendum: seems broken
    resp = requests.post(STATE_BASE_PATH + "/botstate/%s/users/%s" % (channel_id, user_id),
                         json=data_obj,
                         headers=dict(Authorization="Bearer %s" % access_token))

    return resp.status_code == 200


@login_required
@roles_accepted('admin', 'tagger')
def login_channel_id_user_id_get(channel_id: str, user_id: str) -> tuple:
    token = current_user.get_auth_token() if current_user.has_role('tagger') else g.demo_user.get_auth_token()
    success = _set_session_data(channel_id, user_id, token, current_user.email)
    return ('ok', 200) if success else ('failed', 403)
