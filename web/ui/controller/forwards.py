#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Blueprints for url shortening and other redirects"""
from typing import Dict, Any
from flask import Blueprint, jsonify, redirect, render_template, request
from flask_security import auth_token_required, current_user, login_required, roles_required

from common.db.models.scrape import Shortener
from .base62 import decode, encode
from ...flask_modules import TJsonResponse, TResponse
from ...flask_modules.celery import scrape
from ...flask_modules.database import db
from ...flask_modules.security import csrf

FORWARDS_BP = Blueprint('forwards', __name__)
FORWARDS_BP.add_url_rule('/jobs/cgo', 'cgo', lambda: redirect('/cdn/img/jobs/cgo.pdf'))


@FORWARDS_BP.route('/@<url_hash>', methods=['GET'])
def shortener(url_hash: str) -> TResponse:
    """
    Redirects to the original page or provides the necessary meta information for social platforms.
    :param url_hash: shortened hash
    :return: redirect to original page / provided meta (for bots)
    """
    shortened_id = decode(url_hash)
    tags = db.session.query(Shortener).get(shortened_id)
    if tags is None:
        return jsonify(error='/@%s not found' % str(url_hash)), 404

    tags = dict(tags.__dict__)
    tags.pop('_sa_instance_state', None)

    if request.headers['Accept'] == 'application/json':
        return jsonify(hash=url_hash, short_url='https://fanlens.io/@%s' % url_hash, tags=tags)
    else:
        user_agent = request.headers.get('User-Agent', '').lower()
        if user_agent.startswith('twitterbot') or user_agent.startswith('facebo') or user_agent.startswith('LinkedIn'):
            return render_template('shortener.html', **tags)
        return redirect(tags['url'], code=302)


@FORWARDS_BP.route('/@', methods=['POST'])
@auth_token_required
@roles_required('admin')
@csrf.exempt
def create() -> TJsonResponse:
    """
    Create a new shortener entry for the provided url.
    Url can be sent as form param or as json field.
    :return: the shortened url + meta information
    """
    if request.headers['Content-Type'] == 'application/json':
        url = request.json.get('url')
    else:
        url = request.form.get('url')
    if not url:
        return jsonify(error='bad request'), 400
    result = scrape.scrape_meta_for_url(url)
    inserted_id, tags = result.get()
    url_hash = encode(inserted_id)
    response_body: Dict[str, Any] = jsonify(hash=url_hash, short_url=f'https://fanlens.io/@{url_hash}', tags=tags)
    return response_body


@FORWARDS_BP.route('/@', methods=['GET'])
@login_required
@roles_required('admin')
def create_gui() -> str:
    """
    For interanl use, renders a very simple ui to create shortened links.
    :return: simple shortener ui
    """
    return f'''
    <form action="/@?auth_token={current_user.get_auth_token()}" method="post">
        <input name="url"></input>
    </form>
    '''
