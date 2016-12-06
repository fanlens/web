#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

from flask import session
from flask_security.decorators import roles_accepted, auth_token_required
from config.db import Config

BASE_PATH = 'https://directline.botframework.com/v3/directline'
eev_config = None


def _fetch_new():
    # {
    #    "conversationId": "abc123",
    #    "token": "RCurR_XV9ZA.cwA.BKA.iaJrC8xpy8qbOF5xnR2vtCX7CZj0LdjAPGfiCpg4Fv0y8qbOF5xPGfiCpg4Fv0y8qqbOF5x8qbOF5xn",
    #    "expires_in": 1800
    # }
    resp = requests.post(BASE_PATH + "/tokens/generate",
                         headers=dict(Authorization="Bearer %s" % eev_config['secret']))

    if resp.status_code != 200:
        return dict(error="could not connect to eev: " + resp.text), 500
    else:
        session['eev'] = resp.json()
        return session['eev']


def _refresh():
    assert 'eev' in session
    resp = requests.post(BASE_PATH + "/tokens/refresh",
                         headers=dict(Authorization="Bearer %s" % session['eev_token']))
    if resp.status_code != 200:
        return _fetch_new()
    else:
        session['eev'] = resp.json()
        return session['eev']


@auth_token_required
@roles_accepted('admin', 'tagger')
def token_post() -> str:
    global eev_config
    eev_config = Config('eev')
    if 'eev' in session:
        return _refresh()
    else:
        return _fetch_new()
