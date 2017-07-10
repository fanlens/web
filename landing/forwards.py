#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, jsonify, request, render_template
from flask_security import roles_required, auth_token_required, login_required, current_user
from flask_modules.security import csrf
from flask_modules.celery import Scrape
from flask_modules.database import db

from db.models.scrape import Shortener
from .base62 import encode, decode

forwards = Blueprint('forwards', __name__)
forwards.add_url_rule('/jobs/cgo', 'cgo', lambda: redirect('/cdn/img/jobs/cgo.pdf'))


@forwards.route('/@<url_hash>', methods=['GET'])
def shortener(url_hash):
    shortened_id = decode(url_hash)
    data = db.session.query(Shortener).get(shortened_id)
    if data is None:
        return jsonify(error='url not found', reason=str(url_hash)), 404

    data = dict(data.__dict__)
    data.pop('_sa_instance_state', None)

    if request.headers['Accept'] == 'application/json':
        return jsonify(**data)
    else:
        user_agent = request.headers.get('User-Agent', '').lower()
        if user_agent.startswith('twitterbot') or user_agent.startswith('facebo') or user_agent.startswith('LinkedIn'):
            return render_template('shortener.html', **data)
        else:
            return redirect(data['url'], code=302)


@forwards.route('/@', methods=['POST'])
@auth_token_required
@roles_required('admin')
@csrf.exempt
def create():
    if request.headers['Content-Type'] == 'application/json':
        url = request.json.get('url')
    else:
        url = request.form.get('url')
    if not url:
        return jsonify(error='bad request'), 400
    result = Scrape.scrape_meta_for_url(url)
    inserted_id, tags = result.get()
    return jsonify(hash=encode(inserted_id), tags=tags)


@forwards.route('/@', methods=['GET'])
@login_required
@roles_required('admin')
def create_gui():
    return '''
    <form action="/@?api_key=%(access_token)s" method="post">
        <input name="url"></input>
    </form>
    ''' % dict(access_token=current_user.get_auth_token())
