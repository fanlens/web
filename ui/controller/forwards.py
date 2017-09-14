#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base62 import encode, decode
from db.models.scrape import Shortener
from flask import Blueprint, redirect, jsonify, request, render_template
from flask_modules.celery import Scrape
from flask_modules.database import db
from flask_modules.security import csrf
from flask_security import roles_required, auth_token_required, login_required, current_user

forwards = Blueprint('forwards', __name__)
forwards.add_url_rule('/jobs/cgo', 'cgo', lambda: redirect('/cdn/img/jobs/cgo.pdf'))


@forwards.route('/@<url_hash>', methods=['GET'])
def shortener(url_hash):
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
        else:
            return redirect(tags['url'], code=302)


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
    hash = encode(inserted_id)
    return jsonify(hash=hash, short_url='https://fanlens.io/@%s' % hash, tags=tags)


@forwards.route('/@', methods=['GET'])
@login_required
@roles_required('admin')
def create_gui():
    return '''
    <form action="/@?auth_token=%(access_token)s" method="post">
        <input name="url"></input>
    </form>
    ''' % dict(access_token=current_user.get_auth_token())
