#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementations for the activities.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring

from contextlib import suppress
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound

from common.config import get_config
from common.db.models.activities import Source, SourceUser, TagSetUser
from common.db.models.brain import Model
from . import defaults
from ..model import table_names
from ..model.model import ModelQueryDto, model_query_dto, model_to_json, prediction_query_dto
from ..model.user import current_user_dao
from ...flask_modules import TJson, TJsonResponse, bad_arg
from ...flask_modules.celery import brain
from ...flask_modules.database import db
from ...flask_modules.jwt import current_user_id, roles_all

_CONFIG = get_config()


@defaults
def root_get() -> TJsonResponse:
    return dict(models=[model_to_json(model) for model in current_user_dao.models])


@defaults
def model_id_get(model_id: str) -> TJsonResponse:
    model = current_user_dao.models.filter(Model.id == model_id).one_or_none()
    if not model:
        return dict(error='Model not associated to user'), 404
    return model_to_json(model), 200


def _best_model_query_by_id(model_id: str) -> Query:
    return current_user_dao.models.filter(Model.id == model_id).limit(1)


def _best_model_query_by_dto(query: ModelQueryDto) -> Query:
    matching = current_user_dao.models
    if query.tagset_id:
        matching = matching.filter(Model.tagset_id == query.tagset_id)
    if query.source_ids:
        matching = matching.filter(Model.sources.any(Source.id.in_(query.source_ids)))
    return matching.order_by(Model.score.desc(), Model.trained_ts.desc()).limit(1)


@defaults
def search_post(body: TJson) -> TJsonResponse:
    try:
        dto = model_query_dto(body)
    except ValueError as err:
        return bad_arg(err)

    model_query = _best_model_query_by_dto(query=dto)

    try:
        model = model_query.one()
        return model_to_json(model)
    except NoResultFound:
        return dict(error='No model found for this query'), 404


@defaults
def prediction_post(body: TJson, model_id: Optional[str] = None) -> TJsonResponse:
    dto = prediction_query_dto(body)

    try:
        if model_id:
            model_query = _best_model_query_by_id(model_id)
        else:
            model_query = _best_model_query_by_dto(model_query_dto(body))
        model: Model = model_query.one()
        prediction = brain.predict_text(model['id'], dto.text).get()
        prediction = dict((model.tags.filter_by(id=k).one().tag, v) for k, v in prediction)
        return dict(text=dto.text, prediction=prediction)
    except NoResultFound:
        return dict(error='No model found for this query'), 404
    except ValueError as err:
        return bad_arg(err)


@defaults
@roles_all('admin')  # limited atm
def train_post(body: TJson, fast: bool = True) -> TJsonResponse:
    try:
        dto = model_query_dto(body)
    except ValueError as err:
        return bad_arg(err)

    tagset_source_check_sql = text("""
    SELECT count(*) = array_length(:source_ids, 1)	
    FROM %(tagset_user_table)s as tagset_user
    JOIN %(source_user_table)s as source_user ON source_user.user_id = tagset_user.user_id
    WHERE tagset_user.user_id = :user_id AND
          tagset_user.tagset_id = :tagset_id AND
          source_user.source_id = ANY (:source_ids)
    """ % table_names(tagset_user_table=TagSetUser, source_user_table=SourceUser))
    valid = db.engine.execute(tagset_source_check_sql,
                              tagset_id=dto.tagset_id,
                              source_ids=dto.source_ids,
                              user_id=current_user_id()).scalar()
    if not valid:
        return dict(error="user does not have access to all specified ressources"), 403

    params = None
    score = None
    model_id = None
    if fast:
        model_query = _best_model_query_by_dto(dto)
        with suppress(NoResultFound):  # if nothing found, ignore the fast params
            best_model = model_query.one()
            model_id = best_model.id
            params = best_model.params
            score = best_model.score

    job = brain.train_model(current_user_dao.user_id,
                            dto.tagset_id,
                            tuple(dto.source_ids or []),
                            n_estimators=10,
                            _params=params,
                            _score=score)
    if fast and model_id is not None:
        redir_url = '/%s/model/%s' % (_CONFIG.get('DEFAULT', 'version'), str(model_id))
    else:
        redir_url = '/%s/search' % _CONFIG.get('DEFAULT', 'version')
    return dict(job=job.id, url=redir_url), 202
