#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementations for the activities.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring,too-many-arguments
from . import defaults
from .activity import source_id_activity_id_put
from ...flask_modules import TJsonResponse
from ...flask_modules.database import db


@defaults
def root_post(import_activities: dict) -> TJsonResponse:
    ids = set()
    for activity in import_activities['activities']:
        if 'id' not in activity:
            activity['id'] = hash(activity['data'])
        if 'source_id' not in activity:
            return dict(error='no source_id found for ' + activity['id']), 404
        ids.add((activity['source_id'], activity['id']))
        err: TJsonResponse = source_id_activity_id_put(activity['source_id'], activity['id'], activity, False)
        if err:
            db.session.rollback()
            return err
    db.session.commit()
    return dict(activities=[dict(id=activity_id, source_id=source_id) for source_id, activity_id in ids]), 201
