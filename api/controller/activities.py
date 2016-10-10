#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from celery import group
from flask import redirect
from flask_modules.celery import celery
from flask_modules.database import db
from flask_modules.redis import redis_store
from flask_security import current_user
from sqlalchemy.sql import func

from . import defaults
from db import insert_or_ignore, insert_or_update
from db.models.activities import Data, Source, Tag, Tagging, Type, TagSet, Lang

generic_parser = lambda data: dict(
    message=data.text.text or "{in progress}",
    source=dict(id=data.source.id,
                type=data.source.type.value,
                uri=data.source.uri,
                slug=data.source.slug),
    tags=[tag.tag for tag in data.tags],
    created_time=data.time.time.isoformat(),
    meta=dict(
        fingerprint=data.fingerprint.fingerprint,
        language=data.language.language.name
    )
)
parsers = {
    Type.facebook: lambda data: dict(
        id=data.data['id'],
        user=data.data.get('from'),
        **generic_parser(data)
    ),
    Type.twitter: lambda data: dict(
        id=data.data['id_str'],
        user=dict(id=data.data['user']['screen_name'], name=data.data['user']['name']),
        **generic_parser(data)
    ),
    Type.crunchbase: lambda _: None,
    Type.generic: lambda _: None,
}


def _check_result(result: bool):
    if not result:
        return dict(error='User does not have access to all requested sources'), 403
    return None


def _check_sources_by_id(sources: set):
    is_sub = sources.issubset(source.id for source in current_user.sources)
    return _check_result(is_sub)


def _get_suggestions(activity: dict, model_id: str) -> dict:
    # todo model id is hard coded
    if not activity['extra']['fingerprint']:
        return dict()
    async_result = celery.send_task('worker.brain.predict', args=(activity['message'],),
                                    kwargs=dict(fingerprint=activity['meta']['fingerprint'],
                                                created_time=activity['created_time'],
                                                model_id='32797cd2-4203-11e6-9215-f45c89bc662f'))
    return dict((k, v) for [v, k] in async_result.get())


def _get_by_id(source_id: int, activity_id: str) -> Data:
    return db.session.query(Data).filter(
        Data.source_id.in_({src.id for src in current_user.sources}) &
        (Data.source_id == source_id) &
        (Data.object_id == activity_id)).one_or_none()


def _to_key(source_id: int, activity_id: str):
    return "%d:%s" % (source_id, activity_id)


@defaults
def source_ids_get(source_ids: list = None,
                   count: int = None,
                   max_id: str = None,
                   random: bool = False,
                   with_suggestion: bool = None) -> dict:
    error = _check_sources_by_id(set(source_ids))
    if error:
        return error

    data_query = db.session.query(Data)
    if random:
        data_query = data_query.filter(
            Data.id.in_(db.select([func.activity.random_rows(count, 0.6, '{en}', source_ids)])))
    else:
        data_query = data_query.filter(Data.language.has(language='en')).order_by(Data.object_id)

    if max_id:
        data_query = data_query.filter(Data.object_id < max_id)
    data_query = data_query.limit(count).all()

    data = dict((data.id, parsers[data.source.type](data)) for data in data_query)
    # if with_suggestion:
    #     suggestions = group([celery.signature('worker.brain.predict',
    #                                           args=(activity['message'],),
    #                                           kwargs=dict(fingerprint=activity['fingerprint'],
    #                                                       created_time=activity['created_time'],
    #                                                       model_id='32797cd2-4203-11e6-9215-f45c89bc662f',
    #                                                       key_by=activity['id']))
    #                          for activity in data.values()
    #                          if activity['fingerprint'] is not None]).apply_async()
    #     for suggestion in suggestions.get():
    #         data[suggestion['key']]['suggestion'] = dict((k, v) for [v, k] in suggestion['prediction'])
    data = data.values()
    for datum in data:
        redis_store.setex(_to_key(datum['source']['id'], datum['id']), 30, json.dumps(datum).encode('utf-8'))
        del datum['meta']

    return dict(activities=list(data))


@defaults
def source_id_activity_id_field_id_get(source_id: int, activity_id: str, field_id: str, no_cache=False) -> dict:
    activity = source_id_activity_id_get(source_id, activity_id, with_suggestion=field_id == 'suggestion',
                                         no_cache=no_cache)
    if isinstance(activity, tuple):  # error
        return activity
    result = dict(id=activity_id)
    result[field_id] = activity.get(field_id, None)
    return result


@defaults
def source_id_activity_id_get(source_id: int, activity_id: str, no_cache=False, with_suggestion=False) -> dict:
    cached = redis_store.get(_to_key(source_id, activity_id))
    if not cached or no_cache:
        data = _get_by_id(source_id, activity_id)
        if data is None:
            return dict(error='No activity for this id found'), 404

        activity = parsers[data.source.type](data)
        if with_suggestion:
            activity['suggestion'] = _get_suggestions(activity, '')
        elif cached:
            cached = json.loads(cached.decode('utf-8'))
            # protect from cache deletion
            activity['suggestion'] = cached.get('suggestion')
    else:
        activity = json.loads(cached.decode('utf-8'))
        if with_suggestion and activity.get('suggestion') is None:
            activity['suggestion'] = _get_suggestions(activity, '')
    redis_store.setex(_to_key(source_id, activity_id), 30, json.dumps(activity).encode('utf-8'))
    del cached  # only use activity from here on out

    error = _check_sources_by_id({activity['source']['id']})
    if error:
        return error
    del activity['meta']
    return activity


@defaults
def source_id_activity_id_tags_patch(source_id: int, activity_id: str, body: dict) -> dict:
    remove = set(body.get('remove', []))
    add = set(body.get('add', []))
    data = _get_by_id(source_id, activity_id)
    if data is None:
        return dict(error='No activity for this id found'), 404

    for add_tag in add.union(remove):  # make sure all tags are in DB
        tags_tag_put(add_tag, commit=False)
    db.session.commit()

    add and data.tags.update(db.session.query(Tag).filter(Tag.tag.in_(add)).filter_by(user_id=current_user.id))
    remove and data.tags.difference_update(
        db.session.query(Tag).filter(Tag.tag.in_(remove)).filter_by(user_id=current_user.id))
    db.session.commit()
    return source_id_activity_id_field_id_get(source_id, activity_id, 'tags', no_cache=True)


@defaults
def source_id_activity_id_put(source_id: int, activity_id: str, activity_import: dict, commit=True) -> dict:
    if ('source_id' in activity_import and source_id != activity_import['source_id'] or
                    'id' in activity_import and activity_id != activity_import['id']):
        db.session.rollback()
        return dict(error="source_id does not match activity"), 400

    err = _check_sources_by_id({source_id})
    if err:
        db.session.rollback()
        return err

    insert_or_update(db.session,
                     Data(source_id=source_id,
                          object_id=activity_id,
                          data=activity_import['data']),
                     'source_id, object_id')
    commit and db.session.commit()


@defaults
def source_id_activity_id_delete(source_id: int, activity_id: str, commit=True) -> dict:
    err = _check_sources_by_id({source_id})
    if err:
        db.session.rollback()
        return err
    db.session.query(Data).filter_by(source_id=source_id, object_id=activity_id).delete()
    commit and db.session.commit()
    redis_store.delete(_to_key(source_id, activity_id))


@defaults
def root_post(import_activities: dict) -> dict:
    ids = set()
    for activity in import_activities['activities']:
        if 'id' not in activity:
            activity['id'] = hash(activity['data'])
        if 'source_id' not in activity:
            db.session.rollback()
            return dict(error='no source_id found for ' + activity['id']), 400
        ids.add((activity['source_id'], activity['id']))
        err = source_id_activity_id_put(activity['source_id'], activity['id'], activity, False)
        if err:
            db.session.rollback()
            return err
    db.session.commit()
    return dict(activities=[dict(id=activity_id, source_id=source_id) for activity_id, source_id in ids]), 201


@defaults
def sources_get() -> dict:
    return dict(sources=[dict(id=source.id,
                              type=source.type.value,
                              uri=source.uri,
                              slug=source.slug)
                         for source in current_user.sources.all()])


@defaults
def sources_post(source: dict):
    if 'id' in source:
        return dict(error='id not allowed, will be assigned'), 400

    source_entry = Source(type=source['type'],
                          uri=source['uri'],
                          slug=source['slug'])
    current_user.sources.append(source_entry)
    db.session.commit()
    return redirect('/sources/%d' % source_entry.id, code=201)


@defaults
def sources_source_id_get(source_id: int) -> dict:
    source = current_user.sources.filter_by(id=source_id).one_or_none()
    return dict(id=source.id,
                type=source.type.value,
                uri=source.uri,
                slug=source.slug) if source else dict(error="source does not exist"), 404


@defaults
def sources_source_id_patch(source_id: int, source: dict) -> dict:
    user_source = current_user.sources.filter_by(id=source_id).one_or_none()
    if user_source is None:
        return dict(error="source does not exist"), 404
    if 'id' in source:
        return dict(error="source id cannot be changed!"), 403
    if 'type' in source:
        return dict(error="type cannot be changed!"), 403
    if 'uri' in source:
        user_source.uri = source['uri']
    if 'slug' in source:
        user_source.uri = source['slug']
    db.session.commit()


@defaults
def sources_source_id_delete(source_id: int) -> dict:
    current_user.sources.filter_by(id=source_id).delete()
    db.session.commit()


@defaults
def tags_get(with_count: bool = False) -> dict:
    tags = dict(tags=[tag.tag for tag in current_user.tags])
    if with_count:
        tags['counts'] = dict((tag.tag, tag.data.count()) for tag in current_user.tags)
    return tags


@defaults
def tags_tag_get(tag: str, with_count: bool = False) -> dict:
    the_tag = db.session.query(Tag).filter_by(user_id=current_user.id, tag=tag).one_or_none()
    if the_tag is None:
        return dict(error="Tag not found"), 404

    result = dict(tag=the_tag.tag)
    if with_count:
        result['count'] = the_tag.data.count()
    return result


@defaults
def tags_tag_put(tag: str, commit=True) -> dict:
    insert_or_ignore(db.session, Tag(user_id=current_user.id, tag=tag), flush=True)
    commit and db.session.commit()


@defaults
def tags_tag_delete(tag: str) -> dict:
    db.session.query(Tag).filter_by(user_id=current_user.id, tag=tag).delete()
    db.session.commit()


@defaults
def tagsets_get() -> dict:
    tagsets = [dict(id=tagset.id, title=tagset.title, tags=[tag.tag for tag in tagset.tags])
               for tagset in current_user.tagsets]
    return dict(tagSets=tagsets)


@defaults
def tagsets_post(tagset: dict):
    tags = set(tagset['tags'])
    for tag in tags:  # make sure all tags are in DB
        tags_tag_put(tag, commit=False)
    tagset = TagSet(title=tagset['title'], user_id=current_user.id)
    tagset.tags.update(db.session.query(Tag).filter_by(user_id=current_user.id).filter(Tag.tag.in_(tags)))
    current_user.tagsets.append(tagset)
    db.session.commit()
    return redirect('/tagset/%d' % tagset.id, code=201)


@defaults
def tagsets_tagset_id_get(tagset_id: int) -> dict:
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    return dict(id=tagset.id,
                title=tagset.title,
                tags=[tag.tag for tag in tagset.tags]) if tagset else dict(error="tagset does not exist"), 404


@defaults
def tagsets_tagset_id_patch(tagset_id: int, tagset: dict) -> dict:
    user_tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    if user_tagset is None:
        return dict(error="tagset does not exist"), 404
    if 'id' in tagset:
        return dict(error="tagset id cannot be changed!"), 403
    if 'title' in tagset:
        user_tagset.title = tagset['title']
    if 'tags' in tagset:
        tags = set(tagset['tags'])
        for tag in tags:  # make sure all tags are in DB
            tags_tag_put(tag, commit=False)
        user_tagset.tags.update(db.session.query(Tag).filter_by(user_id=current_user.id).filter(Tag.tag.in_(tags)))
    db.session.commit()


@defaults
def tagsets_tagset_id_delete(tagset_id: int) -> dict:
    current_user.tagsets.filter_by(id=tagset_id).delete()
    db.session.commit()


@defaults
def tagsets_tagset_id_tag_delete(tagset_id: int, tag: str) -> dict:
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    if tagset is None:
        return dict(error="tagset does not exist"), 404
    tagset.tags.discard(db.session.query(Tag).filter_by(user_id=current_user.id, tag=tag).one_or_none())
    db.session.commit()


@defaults
def tagsets_tagset_id_tag_put(tagset_id: int, tag: str) -> dict:
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    if tagset is None:
        return dict(error="tagset does not exist"), 404
    tags_tag_put(tag, commit=False)
    tagset.tags.update(db.session.query(Tag).filter_by(user_id=current_user.id, tag=tag))
    db.session.commit()
