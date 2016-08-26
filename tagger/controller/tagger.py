#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json

from flask import render_template, redirect, Response
from flask_security import current_user
from flask_security.decorators import auth_token_required, roles_accepted, roles_required, login_required

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text, func

from celery.result import AsyncResult

from db import insert_or_ignore
from db.models.facebook import FacebookCommentEntry
from db.models.tags import UserToTagToComment
from db.models.brain import Model

from flask_modules import annotation_composer
from flask_modules.security import csrf
from flask_modules.database import db
from flask_modules.redis import redis_store
from flask_modules.celery import celery

defaults = annotation_composer(
    auth_token_required,
    csrf.exempt,
    roles_accepted('admin', 'tagger'))


@login_required
@roles_accepted('admin', 'tagger')
def root_get() -> str:
    return render_template('tagger.html', api_key=current_user.get_auth_token())


def _check_sources(sources: set):
    is_sub = sources.issubset(set(source.slug for source in current_user.sources))
    if not is_sub:
        return dict(error='User does not have access to all requested sources'), 403
    return None


@defaults
def comments__random_get(count: int = None,
                         sources: set = None,
                         with_entity: bool = None,
                         with_suggestion: bool = None) -> dict:
    if not sources:
        sources = set(source.slug for source in current_user.sources)
        ignore_source = True
    else:
        sources = set(sources)
        ignore_source = False
        error = _check_sources(sources)
        if error:
            return error

    # todo: using frac of 1.0 might be pretty slow
    query = db.session.execute(
        text("""
            SELECT
              id,
              meta :: JSONB ->> 'page'                         AS page,
              data :: JSONB ->> 'message'                      AS message,
              data :: JSONB -> 'from'                          AS user,
              COALESCE(meta :: JSONB -> 'tags', '[]' :: JSONB) AS tags
            FROM data.facebook_comments
            WHERE meta :: JSONB ->> 'lang' = :lang AND
                  meta :: JSONB -> 'fingerprint' IS NOT NULL AND
                  (:ignore_source OR meta :: JSONB ->> 'page' IN :sources) AND
                  id IN (
                    SELECT id
                    FROM data.facebook_comments
                      TABLESAMPLE SYSTEM (:frac)
                    WHERE CHAR_LENGTH(data :: JSONB ->> 'message') > 64)
            LIMIT :limit"""),
        dict(frac=1.0, limit=count, lang='en', ignore_source=ignore_source,
             sources=tuple(sources)))

    if with_entity:
        comments = [dict((k, v) for k, v in zip(query.keys(), r)) for r in query]
        for comment in comments:
            comment.update(comments_comment_id_field_id_get(comment['id'], 'tags', raw=True))
    else:
        comments = [{'id': r[0]} for r in query]

    if with_suggestion:
        for comment in comments:
            comment.update(comments_comment_id_field_id_get(comment['id'], 'suggestion', raw=True))
        for comment in comments:
            comment['suggestion'] = _resolve_async(comment['suggestion']) or []
    return dict(comments=comments)


def _resolve_async(async_result: AsyncResult):
    # switch to better backend
    try:
        return dict((k, v) for [v, k] in async_result.get())
    except Exception as err:
        logging.exception('error getting asynchronous result')
        return None


def _get_suggestions_for_id(comment_id: str, model_id: str, async=False) -> AsyncResult:
    comment = db.session.query(FacebookCommentEntry).get(comment_id)
    if not comment or 'fingerprint' not in comment.meta:
        return dict(error='no fingerprint for comment'), 503
    else:
        error = _check_sources({comment.meta['page']})
        if error:
            return error
        # todo model id is hard coded
        async_result = celery.send_task('worker.brain.predict', args=(comment.data['message'],),
                                        kwargs=dict(fingerprint=comment.meta['fingerprint'],
                                                    created_time=comment.data['created_time'],
                                                    model_id='32797cd2-4203-11e6-9215-f45c89bc662f'))
        return async_result if async else _resolve_async(async_result)


@defaults
def comments_comment_id_field_id_get(comment_id, field_id, raw=False) -> dict:
    if field_id == 'suggestion':
        # todo somewhat weird logic
        field_data = dict(suggestion=_get_suggestions_for_id(comment_id, '', async=raw is True))
    else:
        field_data = comments_comment_id_get(comment_id)

    if isinstance(field_data, tuple):
        # yeah yeah... for now it's ok
        raise Exception('wtf')
        return field_data

    result = dict(id=comment_id)
    result[field_id] = field_data.get(field_id, None)
    return result


@defaults
def comments_comment_id_get(comment_id, with_suggestion=False) -> dict:
    comment = redis_store.get(comment_id)
    if not comment:
        comment_entry = db.session.query(FacebookCommentEntry).get(comment_id)
        if comment_entry is None:
            return dict(error='No comment for this id found'), 404
        user_to_tag_to_comments = db.session.query(UserToTagToComment).filter_by(user_id=current_user.id,
                                                                                 comment_id=comment_id)
        comment = dict(
            id=comment_entry.id,
            message=comment_entry.data['message'],
            page=comment_entry.meta['page'],
            tags=[user_to_tag_to_comment.tag for user_to_tag_to_comment in user_to_tag_to_comments],
            user=comment_entry.data['from'])
    else:
        comment = json.loads(str(comment))
    if with_suggestion:
        comment['suggestion'] = _get_suggestions_for_id(comment_id, '', async=False)
    redis_store.setex(comment_id, 30, json.dumps(comment))

    # check after to prevent ddosing the db
    error = _check_sources({comment['page']})
    if error:
        raise Exception(error)
        return error
    return comment


@defaults
def comments_comment_id_tags_patch(comment_id, body: dict, with_entity=False) -> dict:
    remove = body.get('remove', set())
    add = body.get('add', set())
    for remove_tag in remove:
        db.session.query(UserToTagToComment).filter_by(user_id=current_user.id, tag=remove_tag,
                                                       comment_id=comment_id).delete()
    for add_tag in add:
        try:
            insert_or_ignore(db.session, UserToTagToComment(user_id=current_user.id, tag=add_tag,
                                                            comment_id=comment_id))
        except IntegrityError:
            db.session.rollback()
            raise ValueError('tag not allowed')
    db.session.commit()
    return comments_comment_id_get(comment_id) if with_entity else comments_comment_id_field_id_get(comment_id, 'tags')


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


@defaults
def sources_get() -> dict:
    return dict(sources=[source.slug or source.external_id
                         for source in current_user.sources])  # todo switch to internal id?!


@defaults
def tags_get() -> dict:
    return dict(tags=list(set([tag.tag for tagset in current_user.tagsets for tag in tagset.tags])))


@defaults
def tags__counts_get() -> dict:
    return dict(tags=dict((k, v) for k, v in db.session.query(UserToTagToComment.tag)
                          .filter_by(user_id=current_user.id)
                          .add_column(func.count())
                          .group_by(UserToTagToComment.tag).all()))


@defaults
def tagsets_get(include_all=False) -> dict:
    tagsets = dict((str(tagset.id), dict(id=tagset.id, title=tagset.title, tags=[tag.tag for tag in tagset.tags]))
                   for tagset in current_user.tagsets)
    if include_all:
        all_tags = set()
        for tagset in tagsets.values():
            all_tags = all_tags.union(tagset['tags'])
        tagsets['_all'] = dict(id='_all', tags=list(all_tags), title='All Tags')
    return dict(tagSets=tagsets)


def _internal_job_id(job_id):
    return '#task-' + job_id


def _model_to_result(model: Model):
    result = dict(modelId=model.id, trainedTs=model.trained_ts)
    if 'admin' in [role.name for role in current_user.roles]:
        result['score'] = model.score
        result['params'] = model.params
    return result


@defaults
def model_model_id_get(model_id: str) -> dict:
    try:
        model_idx = [model.id for model in current_user.models].index(model_id)
    except ValueError as err:
        return dict(error='Model not associated to user'), 403
    model = current_user.models[model_idx]
    return _model_to_result(model)


@defaults
def model__search_post(body: dict, raw=False) -> dict:
    tagset_id = body.get('tagsetId')
    sources = body.get('sources')
    if tagset_id is None and sources is None:
        return None if raw else (dict(error='No criterium specified'), 400)
    model_query = db.session.query(Model).filter_by(user_id=current_user.id)
    if tagset_id is not None:
        model_query = model_query.filter_by(tagset_id=tagset_id)
    # todo: add sources support
    #    if sources is not None:
    #        model_query = model_query.filter_by(sources=sources)
    model_query = model_query.order_by(Model.score.desc())
    model = model_query.first()
    if model is None:
        return None if raw else (dict(error='No model found for this query'), 404)
    return _model_to_result(model)


@defaults
@roles_required('admin')
def model_post(body: dict, fast=True) -> dict:
    tagset_id = body['tagsetId']
    if tagset_id not in [tagset.id for tagset in current_user.tagsets]:
        return dict(error='Tagset not associated with user'), 403

    sources = set(body['sources'])
    error = _check_sources(sources)
    if error:
        return error

    params = None
    if fast:
        best_model = model__search_post(dict(tagset_id=tagset_id, sources=sources), raw=True)
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
def model__jobs_job_id_get(job_id) -> dict:
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
def model__jobs_job_id_delete(job_id) -> dict:
    job = celery.AsyncResult(job_id)
    error = _check_task(job)
    if error:
        return error
    job.revoke()  # todo: simply revokes the task, does not kill training by default
    return dict(jobId=job_id)
