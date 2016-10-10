#!/usr/bin/env python
# -*- coding: utf-8 -*-
from celery.result import AsyncResult
from db.models.brain import Model
from flask import redirect
from flask_modules.celery import celery
from flask_modules.database import db
from flask_security import current_user
from flask_security.decorators import roles_required

from . import defaults


def _internal_job_id(job_id):
    return '#task-' + job_id


def _model_to_result(model: Model):
    result = dict(modelId=model.id, trainedTs=model.trained_ts)
    if 'admin' in [role.name for role in current_user.roles]:
        result['score'] = model.score
        result['params'] = model.params
    return result


@defaults
def model_id_get(model_id: str) -> dict:
    try:
        model_idx = [model.id for model in current_user.models].index(model_id)
    except ValueError as err:
        return dict(error='Model not associated to user'), 403
    model = current_user.models[model_idx]
    return _model_to_result(model)


@defaults
def search_post(body: dict, internal=False) -> dict:
    tagset_id = body.get('tagsetId')
    sources = body.get('sources')
    if tagset_id is None and sources is None:
        return None if internal else (dict(error='No criterium specified'), 400)
    model_query = db.session.query(Model).filter_by(user_id=current_user.id)
    if tagset_id is not None:
        model_query = model_query.filter_by(tagset_id=tagset_id)
    # todo: add sources support
    #    if sources is not None:
    #        model_query = model_query.filter_by(sources=sources)
    model_query = model_query.order_by(Model.score.desc())
    model = model_query.first()
    if model is None:
        return None if internal else (dict(error='No model found for this query'), 404)
    return _model_to_result(model)


@defaults
@roles_required('admin')
def train_post(body: dict, fast=True) -> dict:
    tagset_id = body['tagsetId']
    if tagset_id not in [tagset.id for tagset in current_user.tagsets]:
        return dict(error='Tagset not associated with user'), 403

    sources = set(body['sources'])
    error = _check_sources(sources)
    if error:
        return error

    params = None
    if fast:
        best_model = model__search_post(dict(tagset_id=tagset_id, sources=sources), internal=True)
        params = best_model and best_model['params']
    job = celery.send_task('worker.brain.train_model',
                           args=(current_user.id, tagset_id, tuple(sources)),
                           kwargs=dict(params=params))
    job_url = '/model/_jobs/' + job.id
    return dict(jobId=job.id, jobUrl=job_url), 303, {'Retry-After': 30, 'Location': job_url}


def _check_task(job: AsyncResult):
    job_info = job.info
    if job_info.get('user_id', None) != current_user.id:
        return dict(error='not job owner'), 403
    return None


@defaults
def jobs_job_id_get(job_id) -> dict:
    job = celery.AsyncResult(job_id)
    error = _check_task(job)
    if error:
        return error
    if job.ready():
        if job.successful():
            tagset_id, version, model_id = job.get(timeout=2)
            return redirect('/model/%s?version=%s' % (tagset_id, version), code=201)
        elif job.failed():
            return dict(error='model could not be created'), 410
    else:  # still running
        if job.state == 'PENDING':  # most likely doesn't exist
            # todo strictly speaking not 404, the task could be simply not started yet
            return dict(error='no job with id ' + job_id), 404
        else:
            job_url = '/model/_jobs/' + job_id
            return dict(jobId=job_id, jobUrl=job_url), 302, {'Retry-After': 30, 'Location': job_url}


@defaults
def jobs_job_id_delete(job_id) -> dict:
    job = celery.AsyncResult(job_id)
    error = _check_task(job)
    if error:
        return error
    job.revoke()  # todo: simply revokes the task, does not kill training by default
    return dict(jobId=job_id)


@defaults
def suggestion_post(body: dict) -> dict:
    try:
        text = body['text']
        task = celery.send_task('worker.brain.predict', args=(text,),
                                kwargs=dict(model_id='32797cd2-4203-11e6-9215-f45c89bc662f'))
        suggestion = dict((k, v) for [v, k] in task.get())
        return dict(text=text, suggestion=suggestion)
    except KeyError:
        return dict(error='no text field in request'), 400
    except Exception as err:
        return dict(error=str(err.args)), 400
