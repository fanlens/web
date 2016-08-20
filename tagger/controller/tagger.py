#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import json

from flask import render_template, redirect
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


@defaults
def comments__random_get(count: int = None,
                         sources: set = None,
                         with_entity: bool = None,
                         with_suggestion: bool = None) -> dict:
    # todo: using frac of 1.0 might be pretty slow
    if sources is None:
        sources = {None}
        ignore_source = True
    else:
        ignore_source = False
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
        raise ValueError('no fingerprint for comment')
    else:
        # todo model id is hard coded
        async_result = celery.send_task('worker.brain.predict', args=(comment.data['message'],),
                                        kwargs=dict(fingerprint=comment.meta['fingerprint'],
                                                    created_time=comment.data['created_time'],
                                                    model_id='32797cd2-4203-11e6-9215-f45c89bc662f'))
        return async_result if async else _resolve_async(async_result)


@defaults
def comments_comment_id_field_id_get(comment_id, field_id, raw=False) -> dict:
    if field_id == 'suggestion':
        field_data = _get_suggestions_for_id(comment_id, '', async=raw is True)  # todo somewhat weird logic
    else:
        field_data = comments_comment_id_get(comment_id).get(field_id, None)

    result = dict(id=comment_id)
    result[field_id] = field_data
    return result


@defaults
def comments_comment_id_get(comment_id, with_suggestion=False) -> dict:
    comment = redis_store.get(comment_id)
    if not comment:
        # todo check source access!
        # todo raise exceptions, 404!
        comment_entry = db.session.query(FacebookCommentEntry).get(comment_id)
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


@defaults
def model_model_id_get(model_id: str) -> dict:
    if model_id not in current_user.models:
        return dict(error='Model not associated to user'), 403
    model = current_user.model[model_id]
    result = dict(id=model.id, trainedTs=model.trained_ts)
    if 'admin' in current_user.roles:
        result['score'] = model.score
    return dict(result)


@defaults
def model__search_post(body: dict, raw=False) -> dict:
    tagset_id = body.get('tagsetId')
    sources = body.get('sources')
    if tagset_id is None and sources is None:
        return None if raw else dict('No criterium specified'), 400
    model_query = db.session.query(Model).filter_by(user_id=current_user.id)
    if tagset_id is not None:
        model_query = model_query.filter_by(tagset_id=tagset_id)
    # todo: add sources support
    #    if sources is not None:
    #        model_query = model_query.filter_by(sources=sources)
    model_query = model_query.order_by(Model.score.desc())
    model = model_query.first()
    if model is None:
        return None if raw else dict('No model found for this query'), 404
    result = dict(id=model.id, trainedTs=model.trained_ts)
    if 'admin' in current_user.roles or raw:
        result['score'] = model.score
        result['params'] = model.params
    return result


@defaults
@roles_required('admin')
def model_post(body: dict, fast=True) -> dict:
    # todo use a mutex in redis to 409
    tagset_id = body['tagsetId']
    sources = body['sources']
    if tagset_id in current_user.tagsets and all(source in current_user.sources for source in sources):
        params = None
        if fast:
            best_model = model__search_post(dict(tagset_id=tagset_id, sources=sources), raw=True)
            params = best_model and best_model['params']
        job_id = celery.send_task('worker.brain.train_model',
                                  args=(current_user.id, tagset_id, tuple(sources)),
                                  kwargs=dict(params=params))
        job_url = '/model/_jobs/' + job_id
        return dict(jobId=job_id, jobUrl=job_url), 303, {'Retry-After': 30, 'Location': job_url}
    else:
        return dict(error='source or tagset not associated with user'), 403


def _check_task(job_id):
    # todo use task status to communicate the stuff
    if task_owner is None:
        return dict(error='job not found'), 404
    if task_owner != current_user.id:
        return dict(error='not job owner'), 403
    return None


@defaults
def model__jobs_job_id_get(job_id) -> dict:
    error = _check_task(job_id)
    if error:
        return error
    result = AsyncResult(job_id)
    if result.ready():
        if result.successful():
            tagset_id, version, model_id = result.get(timeout=2)
            return redirect('/model/%s?version=%s' % (tagset_id, version), code=201)
        elif result.failed():
            return dict(error='model could not be created'), 410
    else:  # still running
        if result.state == 'PENDING':  # most likely doesn't exist
            # todo strictly speaking not 404, the task could be simply not started yet
            return dict(error='no job with id ' + job_id), 404
        else:
            job_url = '/model/_jobs/' + job_id
            return dict(jobId=job_id, jobUrl=job_url), 304, {'Retry-After': 30, 'Location': job_url}


@defaults
def model__jobs_job_id_delete(job_id) -> dict:
    error = _check_task(job_id)
    if error:
        return error
    task = AsyncResult(job_id)
    task.revoke()  # todo: simply revokes the task, does not kill training by default
    return dict(jobId=job_id)
