#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Email


class ContactForm(Form):
    email = StringField("Email", [InputRequired("Please enter your email address."),
                                  Email("A valid email address is required.")])
    company = StringField("Company")
    message = TextAreaField("Message", [InputRequired("Please add a message.")])
    submit = SubmitField("Send")