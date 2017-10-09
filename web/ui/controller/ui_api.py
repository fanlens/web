#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementations for the ui.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring
from typing import Dict, DefaultDict, List

from flask import current_app
from flask_mail import Message
from flask_security import auth_token_required, roles_required
from sqlalchemy.exc import IntegrityError

from common.db.models.users import Enquiry
from ...flask_modules import TJsonResponse, annotation_composer, simple_response, updated_response
from ...flask_modules.database import db
from ...flask_modules.mail import mail
from ...flask_modules.security import csrf

default = annotation_composer(csrf.exempt)  # pylint: disable=invalid-name

strict = annotation_composer(  # pylint: disable=invalid-name
    auth_token_required,
    roles_required('admin'),
    csrf.exempt)


@default
def enquiries_tag_email_put(tag: str, email: str) -> TJsonResponse:
    try:
        db.session.add(Enquiry(email=email, tag=tag.strip().lower()))
        db.session.commit()
    except IntegrityError:
        current_app.logger.warning('duplicate email %s entered in category %s' % (email, tag))
    return updated_response()


@strict
def enquiries_get() -> TJsonResponse:
    enquiries_by_tag = DefaultDict[str, List[Dict[str, str]]](list)
    for enquiry in db.session.query(Enquiry):
        enquiries_by_tag[enquiry.tag].append(
            dict(email=enquiry.email,
                 timestamp=enquiry.timestamp))
    return enquiries_by_tag


@default
def email_post(email: Dict[str, str]) -> TJsonResponse:
    msg = Message(subject=email.get('subject', 'Message From: %s' % email['from']),
                  body="%(sender)s\n%(message)s" % dict(
                      sender=email['from'], message=email['message']),
                  sender=email['from'],
                  recipients=['info@fanlens.io'])
    mail.send(msg)
    return simple_response('ok', 202)
