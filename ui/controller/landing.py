#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from config.db import Config
from flask import Blueprint, flash, redirect, render_template, request
from flask_mail import Message
from flask_modules.mail import mail
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import Email, InputRequired

config = None

landing = Blueprint('landing', __name__)


class ContactForm(FlaskForm):
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    g_recaptcha_response = HiddenField("g-recaptcha-response", id="g-recaptcha-response")


@landing.before_app_first_request
def setup_conf():
    global config
    config = Config()


@landing.route('/pricing', methods=['GET'])
def pricing():
    contact_form = ContactForm()
    return render_template('landing/pricing.html', contact_form=contact_form)


@landing.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@landing.route('/<path:path>')
def index(path):
    contact_form = ContactForm()
    if request.method == 'POST':
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=dict(
            secret=config["recaptcha"]["secret_key"],
            response=contact_form.g_recaptcha_response.data
        ))
        recaptcha = response.json()
        if recaptcha.get('success', False):
            msg = Message(subject='Message From: %s' % contact_form.email.data,
                          body="%(sender)s\n%(message)s" % dict(
                              sender=contact_form.email.data, message=contact_form.message.data),
                          sender=contact_form.email.data,
                          recipients=["info@fanlens.io"])
            mail.send(msg)
            flash('Thank you for contacting us!')
        flash('Spotted invalid traffic')
    return render_template('landing/index.html',
                           contact_form=contact_form,
                           recaptcha_site_key=config["recaptcha"]["site_key"],
                           bot_id=config["eev"]["client_id"])
