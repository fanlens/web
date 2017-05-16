#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db.models.activities import Source
from db.models.brain import Model, Job
from flask import redirect
from flask_modules.celery import celery, Brain
from flask_modules.database import db
from flask_security import current_user
from flask_security.decorators import roles_required

from . import defaults, check_sources_by_id
from .activities import source_to_json, tagset_to_json


def _model_to_result(model: Model):
    result = dict(
        id=model.id,
        trained_ts=model.trained_ts,
        tagset=tagset_to_json(model.tagset),
        sources=[source_to_json(source) for source in model.sources])
    if 'admin' in [role.name for role in current_user.roles]:
        result['score'] = model.score
        result['params'] = model.params
    return result


@defaults
def root_get() -> dict:
    return dict(models=[_model_to_result(model) for model in current_user.models])


@defaults
def model_id_get(model_id: str) -> dict:
    model = current_user.models.filter_by(id=model_id).one_or_none()
    if not model:
        return dict(error='Model not associated to user'), 404
    return _model_to_result(model)


@defaults
def search_post(body: dict, internal=False) -> dict:
    tagset_id = body.get('tagset_id')
    source_ids = body.get('source_ids')
    if tagset_id is None and source_ids is None:
        return None if internal else (dict(error='No criterium specified'), 400)
    matching = current_user.models
    if tagset_id:
        matching = matching.filter_by(tagset_id=tagset_id)
    if source_ids:
        matching = matching.filter(Model.sources.any(Source.id.in_(source_ids)))
    model_query = matching.order_by(Model.score.desc(), Model.trained_ts.desc())

    model = model_query.first()
    if model is None:
        return None if internal else (dict(error='No model found for this query'), 404)
    return _model_to_result(model)


@defaults
@roles_required('admin')
def train_post(body: dict, fast=True) -> tuple:
    jobs = current_user.jobs.all()
    if jobs:
        job_url = '/v3/model/jobs/' + str(jobs[0].id)
        return dict(job=str(jobs[0].id), url=job_url), 409

    tagset_id = body['tagset_id']
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    if not tagset:
        return dict(error='Tagset not associated with user'), 404

    source_ids = set(body['source_ids'])
    error = check_sources_by_id(source_ids)
    if error:
        return error

    params = None
    if fast:
        best_model = search_post(dict(tagset_id=tagset_id, source_ids=source_ids), internal=True)
        params = best_model and best_model['params']
    job = Brain.train_model(tagset_id, tuple(source_ids), n_estimators=200, params=params)
    current_user.jobs.append(Job(id=job.id, user_id=current_user.id))
    db.session.commit()
    job_url = '/v3/model/jobs/' + job.id
    return dict(job=job.id, url=job_url), 202


@defaults
def jobs_get() -> dict:
    return dict(jobs=[dict(job=job.id, url='/v3/jobs/%s' % job.id) for job in current_user.jobs])


@defaults
def jobs_job_id_get(job_id) -> dict:
    job = current_user.jobs.filter_by(id=job_id).one_or_none()
    if not job:
        return dict(error='no job for user with ' + job_id), 404

    result = celery.AsyncResult(job_id)
    if result.ready():
        if result.successful():
            model_id = result.get(timeout=2)
            return redirect('/v3/model/%s' % model_id, code=201)
        elif result.failed():
            return dict(error='model could not be created'), 410
    else:  # still running
        if result.state == 'PENDING':  # most likely doesn't exist
            # todo strictly speaking not 404, the task could be simply not started yet
            return dict(error='no job for user with ' + job_id), 404
        else:
            job_url = '/v3/jobs/' + job_id
            return dict(job=job_id, url=job_url), 304, {'Retry-After': 30, 'Location': job_url}


@defaults
def jobs_job_id_delete(job_id, revoke: bool = True) -> dict:
    job = current_user.jobs.filter_by(id=job_id).one_or_none()
    if not job:
        return dict(error='no job for user with ' + job_id), 404

    if revoke:
        result = celery.AsyncResult(job_id)
        result.revoke()  # todo: simply revokes the task, does not kill training by default
    current_user.jobs.filter_by(id=job_id).delete()
    db.session.commit()
    return dict(job=job_id)


@defaults
def model_id_prediction_post(model_id, body: dict) -> dict:
    model = current_user.models.filter_by(id=model_id).one_or_none()
    if not model:
        return dict(error='model not associated with user'), 404
    text = body['text']
    prediction = Brain.predict_text(model_id, text).get()
    prediction = dict((model.tags.filter_by(id=k).one().tag, v) for k, v in prediction)
    return dict(text=text, prediction=prediction)
