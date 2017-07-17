#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config.db import Config
from flask import Blueprint, flash, redirect, render_template, request
from flask_mail import Message
from flask_modules.mail import mail
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Email, InputRequired

config = None

landing = Blueprint('landing', __name__)


class ContactForm(FlaskForm):
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    submit = SubmitField("Send")


@landing.before_app_first_request
def setup_conf():
    global config
    config = Config('eev')


@landing.route('/pricing', methods=['GET'])
def pricing():
    contact_form = ContactForm()
    return render_template('landing/pricing.html', contact_form=contact_form)


@landing.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@landing.route('/<path:path>')
def index(path):
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
