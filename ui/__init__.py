#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from flask import Flask, render_template, flash, request, jsonify, g, send_from_directory
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email
from flask_mail import Message
from flask_security import current_user, login_required, roles_accepted

from flask_modules import request_wants_json
from flask_modules.mail import mail


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db
    from flask_modules.templating import setup_templating

    app = Flask(__name__)
    setup_db(app)
    setup_mail(app)
    setup_security(app)
    setup_templating(app)
    return app


app = create_app()


class ContactForm(Form):
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    submit = SubmitField("Send")


@app.route('/static/<path:filename>', methods=['GET'])
def send_files(filename):
    return send_from_directory('static', filename)


@app.route('/ui', methods=['GET'])
@login_required
@roles_accepted('admin', 'tagger')
def ui() -> str:
    return render_template('tagger/tagger.html', api_key=current_user.get_auth_token())


@app.route('/', methods=['HEAD'])
def health():
    return 'ok'


@app.route('/', methods=['GET', 'POST'])
def index():
    contact_form = ContactForm()
    if request.method == 'POST':
        #        if session.get('already_sent', False):
        #            flash('Already got your message, thanks!')
        #        elif contact_form.validate():
        #            flash('Thank you for contacting us!')
        #            msg = Message(subject='Message From: %s' % contact_form.email.data,
        #                          body="%(sender)s\n%(message)s" % dict(
        #                              sender=contact_form.email.data, message=contact_form.message.data),
        #                          sender=contact_form.email.data,
        #                          recipients=["info@fanlens.io"])
        #            mail.send(msg)
        #            session['already_sent'] = True
        msg = Message(subject='Message From: %s' % contact_form.email.data,
                      body="%(sender)s\n%(message)s" % dict(
                          sender=contact_form.email.data, message=contact_form.message.data),
                      sender=contact_form.email.data,
                      recipients=["info@fanlens.io"])
        mail.send(msg)
        flash('Thank you for contacting us!')
    return render_template('landing/index.html', contact_form=contact_form)


@app.route('/pricing', methods=['GET'])
def pricing():
    contact_form = ContactForm()
    return render_template('landing/pricing.html', contact_form=contact_form)


@app.route('/demo', methods=['GET'])
def demo():
    if request_wants_json():
        return jsonify(dict())
        # return jsonify(requests.get('https://lb/v3/activities/1/_random',
        #                             params=dict(
        #                                 count=1,
        #                                 sources='adele',
        #                                 with_entity=True,
        #                                 with_suggestion=True,
        #                                 api_key=g.demo_user.get_auth_token()),
        #                             verify=False).json())
    else:
        return render_template('landing/demo.html')
