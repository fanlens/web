#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import requests

from flask import session
from flask_security.decorators import roles_accepted, auth_token_required
from config.db import Config

BASE_PATH = 'https://directline.botframework.com'
eev_config = None


def _fetch_new():
    resp = requests.post(BASE_PATH + "/api/tokens/conversation",
                         headers=dict(Authorization="BotConnector %s" % eev_config['secret']))
    if resp.status_code != 200:
        logging.error("couldn't create token")
        return dict(error="could not connect to eev"), 500
    else:
        session['eev_token'] = resp.text[1:-1]
        return dict(token=session['eev_token'])


def _renew():
    assert 'eev_token' in session
    resp = requests.post(BASE_PATH + "/api/tokens/renew",
                         headers=dict(Authorization="BotConnector %s" % session['eev_token']))
    if resp.status_code != 200:
        logging.error("couldn't renew token")
        return _fetch_new()
    else:
        session['eev_token'] = resp.text[1:-1]
        return dict(token=session['eev_token'])


@auth_token_required
@roles_accepted('admin', 'tagger')
def token_get(renew: bool = True) -> str:
    global eev_config
    eev_config = Config('eev')
    if 'eev_token' in session and renew:
        return _renew()
    else:
        return _fetch_new()
