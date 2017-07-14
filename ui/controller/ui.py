#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict

from db.models.users import Enquiry
from flask import current_app
from flask_mail import Message
from flask_modules import annotation_composer
from flask_modules.database import db
from flask_modules.mail import mail
from flask_modules.security import csrf
from flask_security import auth_token_required, roles_required
from sqlalchemy.exc import IntegrityError

default = annotation_composer(csrf.exempt)

strict = annotation_composer(
    auth_token_required,
    roles_required('admin'),
    csrf.exempt)


@default
def enquiries_tag_email_put(tag: str, email: str) -> str:
    try:
        db.session.add(Enquiry(email=email, tag=tag.strip().lower()))
        db.session.commit()
    except IntegrityError:
        current_app.logger.warning('duplicate email %s entered in category %s' % (email, tag))


@strict
def enquiries_get(filter_done: bool = False):
    enquiries_by_tag = defaultdict(list)
    for enquiry in db.session.query(Enquiry):
        enquiries_by_tag[enquiry.tag].append(
            dict(email=enquiry.email,
                 timestamp=enquiry.timestamp))
    return enquiries_by_tag


@default
def email_post(email: dict):
    msg = Message(subject=email.get('subject', 'Message From: %s' % email['from']),
                  body="%(sender)s\n%(message)s" % dict(
                      sender=email['from'], message=email['message']),
                  sender=email['from'],
                  recipients=['info@fanlens.io'])
    mail.send(msg)
    return 'sent', 202
