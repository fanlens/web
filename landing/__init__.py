#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, flash, request, session, jsonify, g
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email
from flask_mail import Message

from flask_modules.mail import mail

from web.controller.tagger import TaggerController


def create_app():
    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db

    app = Flask(__name__)
    setup_db(app)
    setup_mail(app)
    setup_security(app)
    return app


app = create_app()


class ContactForm(Form):
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    submit = SubmitField("Send")


@app.route('/', methods=['GET', 'POST'])
def index():
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
                          recipients=["info@fanlens.io"])
            mail.send(msg)
            session['already_sent'] = True

    return render_template('index.html', contact_form=contact_form)


@app.route('/demo', methods=['GET'])
def demo():
    random_comment, = TaggerController.get_random_comments(g.demo_user.id, count=1, with_entity=True,
                                                          with_suggestion=True, sources={'adele'})
    return jsonify(random_comment)
