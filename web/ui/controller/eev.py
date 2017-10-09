#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementations for the ui.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring
import requests
from flask import g
from flask_security import current_user, login_required, roles_accepted

from common.config import get_config
from ...flask_modules import simple_response, ok_response, TJsonResponse
from ...flask_modules.jwt import create_jwt_for_user

_CONFIG = get_config()

_TOKEN_API = "https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token"
_GRANT_TYPE: bytes = '&'.join(['grant_type=client_credentials',
                               f"client_id={_CONFIG.get('BOT', 'client_id')}",
                               f"client_secret={_CONFIG.get('BOT', 'client_secret')}",
                               'scope=https%%3A%%2F%%2Fapi.botframework.com%%2F.default']).encode('utf-8')
_STATE_BASE_PATH = "https://state.botframework.com/v3"


def _set_session_data(channel_id: str, user_id: str, jwt: str, name: str) -> bool:
    """Store the session data into channel meta info for the user"""
    data_obj = {"data": {"jwt": jwt, "name": name}, "etag": "*"}
    token_req = requests.post(_TOKEN_API, data=_GRANT_TYPE)

    access_token = token_req.json().get('access_token', '')

    # todo: one should use the serviceUrl property of the original botframework message, addendum: seems broken
    resp = requests.post(_STATE_BASE_PATH + "/botstate/%s/users/%s" % (channel_id, user_id),
                         json=data_obj,
                         headers=dict(Authorization="Bearer %s" % access_token))

    return resp.status_code == 200


@login_required
@roles_accepted('admin', 'tagger')
def login_channel_id_user_id_get(channel_id: str, user_id: str) -> TJsonResponse:
    user = current_user if current_user.id == int(user_id) and current_user.has_role('tagger') else g.demo_user
    token = create_jwt_for_user(user)
    success = _set_session_data(channel_id, user_id, token, current_user.email)
    return ok_response() if success else simple_response('failed', 403)
