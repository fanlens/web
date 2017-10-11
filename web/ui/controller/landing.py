#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Blueprints for the landing page."""
import requests
from flask import Blueprint, Response, flash, render_template, request
from flask_mail import Message
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField
from wtforms.validators import Email, InputRequired

from common.config import get_config
from ...flask_modules.mail import mail

_CONFIG = get_config()

LANDING_BP = Blueprint('landing', __name__)


class ContactForm(FlaskForm):
    """A recaptcha protected contact form for the landing page."""
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    g_recaptcha_response = HiddenField("g-recaptcha-response", id="g-recaptcha-response")


@LANDING_BP.route('/pricing', methods=['GET'])
def pricing() -> Response:
    """Render the pricing page"""
    contact_form = ContactForm()
    return render_template('landing/pricing.html', contact_form=contact_form)


@LANDING_BP.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@LANDING_BP.route('/<path:path>')
def index(path: str) -> Response:
    """
    Main route for landing page. Performs a catch all for unmapped paths.
    GET: render the landing page.
    POST: expects the contact form data and sends a mail accordingly before rendering the landing page.
    """
    contact_form = ContactForm()
    if request.method == 'POST':
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=dict(
            secret=_CONFIG.get("RECAPTCHA", "secret_key"),
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
                           recaptcha_site_key=_CONFIG.get("RECAPTCHA", "site_key"),
                           bot_id=_CONFIG.get("BOT", "client_id"),
                           sub_path=path)
