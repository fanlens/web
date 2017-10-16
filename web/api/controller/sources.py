#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementations for the activities.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring,too-many-arguments
from typing import Union

from flask import Response, redirect
from sqlalchemy import text

from common.db.models.activities import Source, SourceUser
from . import defaults
from ..model import table_names
from ..model.activities import source_to_json
from ..model.user import current_user_dao
from ...flask_modules import TJsonResponse, deleted_response
from ...flask_modules.database import db


@defaults
def sources_get() -> TJsonResponse:
    return dict(sources=[source_to_json(source) for source in current_user_dao.sources.all()])


@defaults
def sources_post(source: dict) -> Union[TJsonResponse, Response]:
    if 'id' in source:
        return dict(error='id not allowed, will be assigned'), 400

    source_add_query = text("""
    WITH inserted_source_id as (
        INSERT INTO %(source_table)s (type, uri, slug)
        VALUES (:type, :uri, :slug)
        ON CONFLICT DO NOTHING
        RETURNING id
    )
    INSERT INTO %(source_user_table)s (source_id, user_id)
    SELECT id as source_id, :user_id as user_id
    FROM inserted_source_id
    ON CONFLICT DO NOTHING
    RETURNING source_id;
    """ % table_names(source_table=Source,
                      source_user_table=SourceUser))
    source_id, = db.engine.execute(source_add_query.execution_options(autocommit=True),
                                   type=source['type'],
                                   uri=source['type'],
                                   slug=source['slug'],
                                   user_id=current_user_dao.user_id).first()
    return redirect('/sources/%d' % source_id, code=201)


@defaults
def sources_source_id_get(source_id: int) -> TJsonResponse:
    source = current_user_dao.sources.filter_by(id=source_id).one_or_none()
    if source:
        return dict(id=source.id,
                    type=source.type,
                    uri=source.uri,
                    slug=source.slug), 200
    return dict(error="source does not exist"), 404


@defaults
def sources_source_id_patch(source_id: int, source: dict) -> TJsonResponse:
    user_source = current_user_dao.sources.filter_by(id=source_id).one_or_none()
    if user_source is None:
        return dict(error="source does not exist"), 404
    if 'id' in source:
        return dict(error="source id cannot be changed!"), 400
    if 'type' in source:
        return dict(error="type cannot be changed!"), 400
    if 'uri' in source:
        user_source.uri = source['uri']
    if 'slug' in source:
        user_source.slug = source['slug']
    db.session.commit()
    return source_to_json(user_source)


@defaults
def sources_source_id_delete(source_id: int) -> TJsonResponse:
    db.session.query(Source).filter((Source.id == source_id) & Source.id.in_(current_user_dao.source_ids)).delete(
        synchronize_session=False)
    db.session.commit()
    return deleted_response()
