#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, redirect, jsonify, request, render_template
from flask_modules.celery import Scrape
from flask_modules.database import db

forwards = Blueprint('forwards', __name__)
forwards.add_url_rule('/jobs/cgo', 'cgo', lambda: redirect('/cdn/img/jobs/cgo.pdf'))


class Card(db.Model):
    id = db.Integer(primary_key=True)
    url = db.String()


@forwards.route('/@<url_hash>', methods=['GET'])
def shortener(url_hash):
    return hash


def resolve_route(url_hash):
    if card is None:
        return jsonify(error='url not found', reason=str(url_hash)), 404

    if request.headers['Accept'] == 'application/json':
        return jsonify(**card)
    else:
        user_agent = request.headers.get('User-Agent', '').lower()
        if user_agent.startswith('twitterbot') or user_agent.startswith('facebo') or user_agent.startswith('LinkedIn'):
            return render_template('shortener.html', **card)
        else:
            return redirect(card['url'], code=302)


def parse():
    card = Scrape.scrape_meta_for_url(url)
