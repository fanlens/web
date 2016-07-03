#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Blueprint, request, flash, session, g, redirect, url_for
from flask_mail import Message

from config.env import Environment

from web.model.contact import ContactForm
from web.modules.mail import mail

from web.controller.tagger import TaggerController

index = Blueprint('index', __name__)

web_env = Environment('WEB')


@index.route('/', methods=['GET', 'POST'])
def root():
    """main index.html"""
    if web_env.get('disable_landing', '0').lower() in ('1', 'true'):
        return redirect(url_for('tagger.random_comments'))

    contact_form = ContactForm()
    if request.method == 'POST':
        if session.get('already_sent', False):
            flash('Already got your message, thanks!')
        elif contact_form.validate():
            flash('Thank you for contacting us!')
            msg = Message(subject='Message From: %s' % contact_form.email.data,
                          body="%(sender)s\n%(message)s" % dict(
                              sender=contact_form.email.data, message=contact_form.message.data),
                          sender=contact_form.email.data,
                          recipients=["info.fanlens@gmail.com"])
            mail.send(msg)
            session['already_sent'] = True

    random_comment, = TaggerController.get_random_comments(g.demo_user.id, count=1, with_entity=True,
                                                           with_suggestion=True,
                                                           sources={'ladygaga'})
    return render_template('landing/index.html', contact_form=contact_form, demo=random_comment)
