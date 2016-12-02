#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing

from api.controller import check_sources_by_id
from db import insert_or_ignore, insert_or_update
from db.models.activities import Data, Source, Tag, Type, TagSet
from flask import redirect
from flask_modules.database import db
from flask_security import current_user
from sqlalchemy.sql import func

from . import defaults


def generic_parser(data: Data) -> dict:
    return dict(
        text=data.text.text if data.text else "",
        source=dict(id=data.source.id,
                    type=data.source.type.value,
                    uri=data.source.uri,
                    slug=data.source.slug),
        tags=[tag.tag for tag in data.tags],
        created_time=data.time.time.isoformat() if data.time else '1970-01-01T00:00:00+00:00',
        language=data.language.language.name if data.language else 'un',
        prediction=dict((data.prediction.model.tags.filter_by(id=k).one().tag, v) for k, v in
                        data.prediction.prediction) if data.prediction else dict())


_parsers = {
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


def parser(data: Data) -> dict:
    return _parsers[data.source.type](data)


@defaults
def source_ids_get(source_ids: list = None, count: int = None, max_id: str = None, random: bool = False) -> \
        typing.Union[dict, tuple]:
    error = check_sources_by_id(set(source_ids))
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

    data = [parser(data) for data in data_query]
    return dict(activities=list(data))


@defaults
def source_id_activity_id_get(source_id: int, activity_id: str, _internal=False) -> typing.Union[dict, tuple, Data]:
    data = current_user.data.filter_by(source_id=source_id, object_id=activity_id).one_or_none()
    if not data:
        return dict(error='No activity found for user and %d -> %s' % (source_id, activity_id)), 404
    return parser(data) if not _internal else data


@defaults
def source_id_activity_id_field_id_get(source_id: int, activity_id: str, field_id: str) -> typing.Union[dict, tuple]:
    activity = source_id_activity_id_get(source_id, activity_id)
    if isinstance(activity, tuple):  # error
        return activity
    return {'id': activity_id, field_id: activity.get(field_id, None)}


@defaults
def source_id_activity_id_tags_patch(source_id: int, activity_id: str, body: dict) -> typing.Union[dict, tuple]:
    remove = set(body.get('remove', []))
    add = set(body.get('add', []))
    data = source_id_activity_id_get(source_id, activity_id, _internal=True)
    if data is None:
        return dict(error='No activity for this id found'), 404
    elif isinstance(data, tuple):  # error
        return data

    for add_tag in add.union(remove):  # make sure all tags are in DB
        tags_tag_put(add_tag, commit=False)
    db.session.commit()

    add and data.tags.update(db.session.query(Tag).filter(Tag.tag.in_(add)).filter_by(user_id=current_user.id))
    remove and data.tags.difference_update(
        db.session.query(Tag).filter(Tag.tag.in_(remove)).filter_by(user_id=current_user.id))
    db.session.commit()
    return source_id_activity_id_field_id_get(source_id, activity_id, 'tags')


@defaults
def source_id_activity_id_put(source_id: int,
                              activity_id: str,
                              activity_import: dict,
                              commit=True) -> typing.Union[dict, tuple]:
    if ('source_id' in activity_import and source_id != activity_import['source_id']) or (
                    'id' in activity_import and activity_id != activity_import['id']):
        db.session.rollback()
        return dict(error="source_id does not match activity"), 400

    err = check_sources_by_id({source_id})
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
def source_id_activity_id_delete(source_id: int, activity_id: str, commit=True) -> typing.Union[dict, tuple]:
    # directly deleting from current_user relationship has a glitch :(
    err = check_sources_by_id({source_id})
    if err:
        return err
    db.session.query(Data).filter_by(source_id=source_id, object_id=activity_id).delete()
    commit and db.session.commit()


@defaults
def root_post(import_activities: dict) -> typing.Union[dict, tuple]:
    ids = set()
    for activity in import_activities['activities']:
        if 'id' not in activity:
            activity['id'] = hash(activity['data'])
        if 'source_id' not in activity:
            return dict(error='no source_id found for ' + activity['id']), 400
        ids.add((activity['source_id'], activity['id']))
        err = source_id_activity_id_put(activity['source_id'], activity['id'], activity, False)
        if err:
            db.session.rollback()
            return err
    db.session.commit()
    return dict(activities=[dict(id=activity_id, source_id=source_id) for source_id, activity_id in ids]), 201


@defaults
def sources_get() -> dict:
    return dict(sources=[dict(id=source.id,
                              type=source.type.value,
                              uri=source.uri,
                              slug=source.slug)
                         for source in current_user.sources.all()])


@defaults
def sources_post(source: dict) -> typing.Union[dict, tuple]:
    if 'id' in source:
        return dict(error='id not allowed, will be assigned'), 400

    source_entry = Source(type=source['type'],
                          uri=source['uri'],
                          slug=source['slug'])
    current_user.sources.append(source_entry)
    db.session.commit()
    return redirect('/sources/%d' % source_entry.id, code=201)


@defaults
def sources_source_id_get(source_id: int) -> typing.Union[dict, tuple]:
    source = current_user.sources.filter_by(id=source_id).one_or_none()
    return dict(id=source.id,
                type=source.type.value,
                uri=source.uri,
                slug=source.slug) if source else dict(error="source does not exist"), 404


@defaults
def sources_source_id_patch(source_id: int, source: dict) -> typing.Union[dict, tuple]:
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
def source_ids_tags_get(source_ids: list, with_count: bool = True) -> typing.Union[dict, tuple]:
    error = check_sources_by_id(set(source_ids))
    if error:
        return error
    current_user.sources.filter(Source.id.in_(source_ids))
    tags = dict()
    tags['counts'] = dict((t, c) for t, c in
                          ((tag.tag, tag.data.filter(Data.source_id.in_(source_ids)).count()) for tag in
                           current_user.tags)
                          if c > 0)
    tags['tags'] = list(tags['counts'].keys())
    if not with_count:
        del (tags['counts'])
    return tags


@defaults
def tags_tag_get(tag: str, with_count: bool = False) -> typing.Union[dict, tuple]:
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
def tagsets_tagset_id_get(tagset_id: int) -> typing.Union[dict, tuple]:
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    return dict(id=tagset.id,
                title=tagset.title,
                tags=[tag.tag for tag in tagset.tags]) if tagset else dict(error="tagset does not exist"), 404


@defaults
def tagsets_tagset_id_patch(tagset_id: int, tagset: dict) -> typing.Union[dict, tuple]:
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
def tagsets_tagset_id_tag_delete(tagset_id: int, tag: str) -> typing.Union[dict, tuple]:
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    if tagset is None:
        return dict(error="tagset does not exist"), 404
    tagset.tags.discard(db.session.query(Tag).filter_by(user_id=current_user.id, tag=tag).one_or_none())
    db.session.commit()


@defaults
def tagsets_tagset_id_tag_put(tagset_id: int, tag: str) -> typing.Union[dict, tuple]:
    tagset = current_user.tagsets.filter_by(id=tagset_id).one_or_none()
    if tagset is None:
        return dict(error="tagset does not exist"), 404
    tags_tag_put(tag, commit=False)
    tagset.tags.update(db.session.query(Tag).filter_by(user_id=current_user.id, tag=tag))
    db.session.commit()
