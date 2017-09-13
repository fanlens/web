#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing
from sqlalchemy import text

from db.models.activities import Source, TagSetUser, SourceUser
from db.models.brain import Model
from flask_modules.database import db
from flask_modules.celery import Brain
from flask_modules.jwt import is_admin, roles_all, current_user_id
from . import defaults, CurrentUserDao, table_names
from .activities import source_to_json, tagset_to_json

current_user_dao = CurrentUserDao()


def _model_to_result(model: Model):
    result = dict(
        id=str(model.id),
        trained_ts=model.trained_ts,
        tagset=tagset_to_json(model.tagset),
        sources=[source_to_json(source) for source in model.sources])
    if is_admin():
        result['score'] = model.score
        result['params'] = model.params
    return result


@defaults
def root_get() -> dict:
    return dict(models=[_model_to_result(model) for model in current_user_dao.models])


@defaults
def model_id_get(model_id: str) -> tuple:
    model = current_user_dao.models.filter(Model.id == model_id).one_or_none()
    if not model:
        return dict(error='Model not associated to user'), 404
    return _model_to_result(model), 200


@defaults
def search_post(body: dict, internal=False, evaluate=True) -> typing.Union[tuple, dict]:
    tagset_id = body.get('tagset_id')
    source_ids = body.get('source_ids')
    assert not internal or tagset_id or source_ids
    if tagset_id is None and source_ids is None:
        return dict(error='No criterium specified'), 400
    matching = current_user_dao.models
    if tagset_id:
        matching = matching.filter(Model.tagset_id == tagset_id)
    if source_ids:
        matching = matching.filter(Model.sources.any(Source.id.in_(source_ids)))
    model_query = matching.order_by(Model.score.desc(), Model.trained_ts.desc())

    if internal and not evaluate:
        return model_query

    model = model_query.first()
    if model is None:
        return None if internal else (dict(error='No model found for this query'), 404)
    if internal:
        return _model_to_result(model)
    return _model_to_result(model), 200


@defaults
def prediction_post(body: dict, model_id=None) -> dict:
    if model_id:
        model_query = current_user_dao.models.filter(Model.id == model_id).one_or_none()
    else:
        model_query = search_post(body, internal=True, evaluate=False)

    model = model_query.first()
    text = body['text']
    prediction = Brain.predict_text(str(model.id), text).get()
    prediction = dict((model.tags.filter_by(id=k).one().tag, v) for k, v in prediction)
    return dict(text=text, prediction=prediction)


@defaults
@roles_all('admin')  # limited atm
def train_post(body: dict, fast=True) -> tuple:
    tagset_id = body['tagset_id']
    source_ids = body['source_ids']

    tagset_source_check_sql = text("""
    SELECT count(*) = array_length(:source_ids, 1)	
    FROM %(tagset_user_table)s as tagset_user
    JOIN %(source_user_table)s as source_user ON source_user.user_id = tagset_user.user_id
    WHERE tagset_user.user_id = :user_id AND
          tagset_user.tagset_id = :tagset_id AND
          source_user.source_id = ANY (:source_ids)
    """ % table_names(tagset_user_table=TagSetUser, source_user_table=SourceUser))
    valid = db.engine.execute(tagset_source_check_sql,
                              tagset_id=tagset_id,
                              source_ids=source_ids,
                              user_id=current_user_id()).scalar()
    if not valid:
        return dict(error="user does not have access to all specified ressources"), 403

    params = None
    score = None
    model_id = None
    if fast:
        best_model = search_post(dict(tagset_id=tagset_id, source_ids=source_ids), internal=True) or dict()
        model_id = best_model.get('id')
        params = best_model.get('params')
        score = best_model.get('score')
    job = Brain.train_model(current_user_dao.id, tagset_id, tuple(source_ids), n_estimators=10, _params=params,
                            _score=score)
    if fast and model_id is not None:
        redir_url = '/v4/model/' + model_id
    else:
        redir_url = '/v4/search'
    return dict(job=job.id, url=redir_url), 202
