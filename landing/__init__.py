#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.db import Config
from flask import Flask, render_template, flash, request, redirect
from flask_mail import Message
from flask_modules.mail import mail
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email

config = None


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db

    app = Flask(__name__)
    setup_db(app)
    setup_mail(app)
    setup_security(app)

    from .forwards import forwards
    app.register_blueprint(forwards)

    return app


app = create_app()


class ContactForm(FlaskForm):
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    submit = SubmitField("Send")


@app.before_first_request
def setup_conf():
    global config
    config = Config('eev')


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
    return render_template('landing/index.html', contact_form=contact_form, bot_id=config["client_id"])


@app.route('/pricing', methods=['GET'])
def pricing():
    contact_form = ContactForm()
    return render_template('landing/pricing.html', contact_form=contact_form)


@app.route('/<path:path>')
def root(path):
    return redirect('/v3/ui/' + path)
