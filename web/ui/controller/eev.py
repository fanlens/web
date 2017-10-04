#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from flask_security import login_required, roles_accepted, current_user

from common.config import get_config
from ...flask_modules.jwt import create_jwt_for_user

config = get_config()

TOKEN_API = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
GRANT_TYPE = (
    "grant_type=client_credentials&client_id=%(client_id)s&client_secret=%(client_secret)s&scope=https%%3A%%2F%%2Fapi.botframework.com%%2F.default"
    % dict(client_id=config.get('BOT', 'client_id'),
           client_secret=config.get('BOT', 'client_secret')))
STATE_BASE_PATH = "https://state.botframework.com/v3"


def _set_session_data(channel_id, user_id, jwt, name) -> bool:
    data_obj = {"data": {"jwt": jwt, "name": name}, "etag": "*"}
    token_req = requests.post(TOKEN_API, data=GRANT_TYPE)

    access_token = token_req.json().get('access_token', '')

    # todo: one should use the serviceUrl property of the original botframework message, addendum: seems broken
    resp = requests.post(STATE_BASE_PATH + "/botstate/%s/users/%s" % (channel_id, user_id),
                         json=data_obj,
                         headers=dict(Authorization="Bearer %s" % access_token))

    return resp.status_code == 200


@login_required
@roles_accepted('admin', 'tagger')
def login_channel_id_user_id_get(channel_id: str, user_id: str) -> tuple:
    user = current_user if current_user.id == int(user_id) and current_user.has_role('tagger') else g.demo_user
    token = create_jwt_for_user(user)
    success = _set_session_data(channel_id, user_id, token, current_user.email)
    return ('ok', 200) if success else ('failed', 403)
