#!/usr/bin/env python
# -*- coding: utf-8 -*-
import typing
from contextlib import suppress

from flask import redirect
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from db import insert_or_ignore
from db.models.activities import (Data, Source, SourceUser, Language, Tag, TagUser, TagSet, TagSetUser, TagTagSet,
                                  Tagging, Time, Type)
from db.models.brain import Prediction
from flask_modules.database import db
from . import defaults, current_user_dao, table_names

_best_models_for_user_sql = text('''
SELECT id FROM (
SELECT DISTINCT ON (tagset_id, sources)
    model.id, model.score, model.trained_ts, model.tagset_id, jsonb_agg(DISTINCT src_mdl.source_id ORDER BY src_mdl.source_id) AS sources
FROM activity.model AS model
JOIN activity.source_model AS src_mdl ON src_mdl.model_id = model.id
JOIN activity.model_user AS model_user ON model_user.model_id = model.id
WHERE model_user.user_id = :user_id 
GROUP BY model.tagset_id, model.id, model.score, model.trained_ts
ORDER BY model.tagset_id, sources, score DESC, model.trained_ts DESC) AS best_models''')


def _activity_id_query(source_id, activity_id):
    return current_user_dao.data_ids.filter((Source.id == source_id) & (Data.object_id == activity_id))


def _activity_query(source_id, activity_id):
    return current_user_dao.data.filter((Source.id == source_id) & (Data.object_id == activity_id))


def source_to_json(source: Source):
    return dict(
        id=source.id,
        type=source.type,
        uri=source.uri,
        slug=source.slug)


def tagset_to_json(tagset: TagSet):
    return dict(
        id=tagset.id,
        title=tagset.title,
        tags=[tag.tag for tag in tagset.tags])


def generic_parser(data: Data) -> dict:
    # todo for large amount of rows this is very inefficient
    return dict(
        text=data.text.text if data.text else "",
        source=dict(id=data.source.id,
                    type=data.source.type,
                    uri=data.source.uri,
                    slug=data.source.slug),
        tags=[tag.tag for tag in data.tags],
        created_time=data.time.time.isoformat() if data.time else '1970-01-01T00:00:00+00:00',
        language=data.language.language.name if data.language else 'un',
        prediction=dict(
            (prediction.model.tags.filter_by(id=k).one().tag, v)
            for prediction in data.predictions.filter(
                Prediction.model_id.in_(_best_models_for_user_sql.bindparams(user_id=current_user_dao.id)))
            for k, v in prediction.prediction)
        if data.predictions else dict())


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
    Type.twitter_dm: lambda data: dict(
        id=data.data['id'],
        user=dict(id=data.data['message_create']['sender_id'], name=data.data['message_create']['sender_id']),
        **generic_parser(data)
    ),
    Type.crunchbase: lambda _: None,
    Type.generic: lambda data: dict(
        id=str(data.data['comment_id']),
        user=dict(id=str(data.data['user']['id']), name=data.data['user']['id']),
        **generic_parser(data)
    ),
}


def parser(data: Data) -> dict:
    return _parsers[Type(data.source.type)](data)


@defaults
def root_get(count: int = None,
             max_id: str = None,
             since: str = None,
             until: str = None,
             source_ids: list = None,
             tagset_ids: list = None,
             tags: list = None,
             languages: list = None,
             random: bool = False) -> typing.Union[dict, tuple]:
    data_query = (db.session.query(Data)
                  .filter(Data.source_id.in_(current_user_dao.source_ids)))

    if since or until or not random:
        data_query = data_query.join(Time, Time.data_id == Data.id)

    if source_ids:
        data_query = data_query.filter(Data.source_id.in_(source_ids))

    if max_id:
        data_query = data_query.filter(Data.object_id < max_id)

    if since or until:
        if since:
            data_query = data_query.filter(Time.time >= since)
        if until:
            data_query = data_query.filter(Time.time <= until)

    if tagset_ids:
        data_query = (data_query
                      .join(Tagging, Tagging.data_id == Data.id)
                      .join(TagTagSet, TagTagSet.tag_id == Tagging.tag_id)
                      .join(TagSetUser,
                            (TagSetUser.tagset_id == TagTagSet.tagset_id) &
                            (TagSetUser.user_id == current_user_dao.id))
                      .filter(TagTagSet.tagset_id.in_(tuple(tagset_ids))))
    if tags:
        data_query = (data_query
                      .join(Tagging, Tagging.data_id == Data.id)
                      .join(Tag, Tag.id == Tagging.tag_id)
                      .join(TagUser,
                            (TagUser.tag_id == Tag.id) &
                            (TagUser.user_id == current_user_dao.id))
                      .filter(Tag.tag.in_(tags)))

        if random:
            data_query = data_query.order_by(
                db.func.random())  # inefficient but ok for now, see also random_rows stored procedure
        else:
            data_query = data_query.order_by(Time.time.desc())

    if languages:
        data_query = (data_query
                      .join(Language, Language.data_id == Data.id)
                      .filter(Language.language.in_(languages)))

    data_query = data_query.limit(count)

    data = [parser(data) for data in data_query]
    return dict(activities=list(data))


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
def source_id_activity_id_get(source_id: int, activity_id: str, _internal=False) -> typing.Union[dict, tuple, Data]:
    data = _activity_query(source_id, activity_id).one_or_none()
    if not data:
        return dict(error='No activity found for user and %d -> %s' % (source_id, activity_id)), 404
    if _internal:
        return data
    return parser(data)


@defaults
def source_id_activity_id_tags_patch(source_id: int, activity_id: str, body: dict) -> typing.Union[dict, tuple]:
    remove = tuple(set(body.get('remove', [])))
    add = tuple(set(body.get('add', [])))

    if add or remove:
        sql = text("""
            BEGIN;
            
            INSERT INTO %(tagging_table)s (tag_id, data_id, tagging_ts)
            SELECT tag.id as tag_id, data.id as data_id, now() as tagging_ts
            FROM %(tag_table)s as tag
            INNER JOIN %(data_table)s as data ON data.object_id = :object_id   -- correct data id
            INNER JOIN %(source_user_table)s as source_user ON data.source_id = source_user.source_id AND source_user.user_id = :user_id  -- data belongs to user
            INNER JOIN %(tag_user_table)s as tag_user ON tag.id = tag_user.tag_id AND tag_user.user_id = :user_id  -- tag belongs to user
            WHERE tag.tag in :add
            ON CONFLICT DO NOTHING;
            
            DELETE FROM %(tagging_table)s as tagging
            USING %(tag_user_table)s as tag_user,
                  %(tag_table)s as tag, 
                  %(data_table)s as data,  
                  %(source_user_table)s as source_user
            WHERE tag.tag in :remove AND
                  tag.id = tag_user.tag_id AND tag_user.user_id = :user_id AND  -- tag belongs to user
                  data.object_id = :object_id AND  -- correct data id
                  data.source_id = source_user.source_id AND source_user.user_id = :user_id AND  -- data belongs to user
                  tagging.tag_id = tag.id AND 
                  tagging.data_id = data.id;
            
            COMMIT;
            """ % table_names(tagging_table=Tagging,
                              tag_table=Tag,
                              tag_user_table=TagUser,
                              data_table=Data,
                              source_user_table=SourceUser))
        db.engine.execute(sql,
                          object_id=activity_id,
                          user_id=current_user_dao.id,
                          add=add or tuple([None]),
                          remove=remove or tuple([None]))

    data = source_id_activity_id_get(source_id, activity_id, _internal=True)  # type: Data
    if isinstance(data, tuple):  # error
        return data
    return {'id': activity_id, 'tags': [tag.tag for tag in data.tags]}


@defaults
def source_id_activity_id_put(source_id: int,
                              activity_id: str,
                              activity_import: dict,
                              commit=True) -> typing.Union[dict, tuple]:
    if ('source_id' in activity_import and source_id != activity_import['source_id']) or (
                    'id' in activity_import and activity_id != activity_import['id']):
        db.session.rollback()
        return dict(error="source_id does not match activity"), 400

    if source_id not in current_user_dao.source_ids.all():
        db.session.rollback()
        return dict(error="user not associated to source"), 403

    insert_or_ignore(db.session,
                     Data(source_id=source_id,
                          object_id=activity_id,
                          data=activity_import['data']))
    commit and db.session.commit()


@defaults
def source_id_activity_id_delete(source_id: int, activity_id: str, commit=True):
    db.session.query(Data).filter(Data.id.in_(_activity_id_query(source_id, activity_id))).delete(
        synchronize_session=False)
    commit and db.session.commit()


@defaults
def sources_get() -> dict:
    return dict(sources=[source_to_json(source) for source in current_user_dao.sources.all()])


@defaults
def sources_post(source: dict) -> tuple:
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
                                   user_id=current_user_dao.id).first()
    return redirect('/sources/%d' % source_id, code=201)


@defaults
def sources_source_id_get(source_id: int) -> typing.Union[dict, tuple]:
    source = current_user_dao.sources.filter_by(id=source_id).one_or_none()
    return (dict(id=source.id,
                 type=source.type,
                 uri=source.uri,
                 slug=source.slug), 200) if source else \
        (dict(error="source does not exist"), 404)


@defaults
def sources_source_id_patch(source_id: int, source: dict) -> typing.Union[dict, tuple]:
    user_source = current_user_dao.sources.filter_by(id=source_id).one_or_none()
    if user_source is None:
        return dict(error="source does not exist"), 404
    if 'id' in source:
        return dict(error="source id cannot be changed!"), 403
    if 'type' in source:
        return dict(error="type cannot be changed!"), 403
    if 'uri' in source:
        user_source.uri = source['uri']
    if 'slug' in source:
        user_source.slug = source['slug']
    db.session.commit()


@defaults
def sources_source_id_delete(source_id: int) -> dict:
    db.session.query(Source).filter((Source.id == source_id) & Source.id.in_(current_user_dao.source_ids)).delete(
        synchronize_session=False)
    db.session.commit()


@defaults
def tags_get(with_count: bool = False) -> dict:
    if with_count:
        tags = {}
        with_count_sql = text("""
        SELECT tag.tag, count(*)
        FROM %(data_table)s as data
        JOIN %(tagging_table)s as tagging ON tagging.data_id = data.id
        JOIN %(tag_table)s  as tag ON tagging.tag_id = tag.id
        JOIN %(tag_user_table)s as tag_user ON tag_user.tag_id = tag.id AND tag_user.user_id = :user_id
        GROUP BY tag.tag  -- tag is unique per user
        """ % table_names(data_table=Data,
                          tagging_table=Tagging,
                          tag_table=Tag,
                          tag_user_table=TagUser))
        tags['counts'] = dict(
            (tag, tag_count) for tag, tag_count in db.engine.execute(with_count_sql, user_id=current_user_dao.id))
        tags['tags'] = list(tags['counts'].keys())
    else:
        tags = dict(tags=[tag.tag for tag in current_user_dao.tags])
    return tags


@defaults
def tags_tag_get(tag: str, with_count: bool = False) -> typing.Union[dict, tuple]:
    the_tag = current_user_dao.tags.filter(Tag.tag == tag).one_or_none()
    if the_tag is None:
        return dict(error="Tag not found"), 404

    result = dict(tag=the_tag.tag)
    if with_count:
        result['count'] = the_tag.data.count()
    return result


@defaults
def tags_tag_put(tag: str, commit=True) -> tuple:
    tag = Tag(tag=tag, created_by_user_id=current_user_dao.id)
    with suppress(IntegrityError):
        db.session.add(tag)
        # todo: performance - one unnecessary roundtrip. ignore until relevant
        current_user_dao.self.one().tags.append(tag)
        commit and db.session.commit()
    return dict(tag=tag.tag), 201


@defaults
def tags_tag_delete(tag: str):
    current_user_dao.created_tags.filter(Tag.tag == tag).delete()
    db.session.commit()


@defaults
def tagsets_get() -> dict:
    tagsets = [tagset_to_json(tagset) for tagset in current_user_dao.tagsets]
    return dict(tagSets=tagsets)


@defaults
def tagsets_post(tagset: dict):
    insert_tagset_sql = text("""
    -- create tagset and associate to user
    WITH inserted_tagset_id as (
        INSERT INTO %(tagset_table)s (title, created_by_user_id)
        VALUES (:title, :user_id)
        RETURNING id, created_by_user_id
    ),
    tagset_user_association as (
        INSERT INTO %(tagset_user_table)s (tagset_id, user_id)
        SELECT id as tagset_id, created_by_user_id as user_id
        FROM inserted_tagset_id
        ON CONFLICT DO NOTHING
        RETURNING tagset_id
    )
    -- add tags to tagset
    INSERT INTO %(tag_tagset_table)s (tagset_id, tag_id)
    SELECT tagset_user_association.tagset_id as tagset_id, tag.id as tag_id
    FROM tagset_user_association, %(tag_table)s as tag 
    JOIN %(tag_user_table)s as tag_user ON tag_user.tag_id = tag.id AND tag_user.user_id = :user_id
    WHERE tag.tag = ANY (:tags)
    ON CONFLICT DO NOTHING
    RETURNING tagset_id;
    """ % table_names(tag_table=Tag,
                      tag_user_table=TagUser,
                      tagset_table=TagSet,
                      tagset_user_table=TagSetUser,
                      tag_tagset_table=TagTagSet))
    result = list(db.engine.execute(insert_tagset_sql.execution_options(autocommit=True),
                                    user_id=current_user_dao.id,
                                    tags=tagset['tags'],
                                    title=tagset['title']))
    if result:
        return redirect('/tagset/%d' % result[0][0], code=201)
    else:
        return dict(error='no tagset created'), 200


@defaults
def tagsets_tagset_id_get(tagset_id: int) -> typing.Union[dict, tuple]:
    tagset = current_user_dao.tagsets.filter(TagSet.id == tagset_id).one_or_none()
    if not tagset:
        return dict(error="tagset does not exist"), 404
    return dict(id=tagset.id,
                title=tagset.title,
                tags=[tag.tag for tag in tagset.tags])


@defaults
def tagsets_tagset_id_patch(tagset_id: int, tagset: dict) -> typing.Union[dict, tuple]:
    user_tagset = current_user_dao.tagsets.filter_by(id=tagset_id).one_or_none()
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
        user_tagset.tags.update(
            db.session.query(Tag).filter(Tag.user.any(id=current_user_dao.id)).filter(Tag.tag.in_(tags)))
    db.session.commit()
    if user_tagset:
        return dict(id=user_tagset.id,
                    title=user_tagset.title,
                    tags=[tag.tag for tag in user_tagset.tags]), 200
    else:
        return dict(error="tagset does not exist"), 404


@defaults
def tagsets_tagset_id_delete(tagset_id: int) -> dict:
    current_user_dao.tagsets.filter(TagSet.id == tagset_id).delete(synchronize_session=False)
    db.session.commit()


@defaults
def tagsets_tagset_id_tag_delete(tagset_id: int, tag: str) -> typing.Union[dict, tuple]:
    db.session.query(TagTagSet).filter(
        TagTagSet.tagset_id.in_(current_user_dao.tagset_ids) &
        (TagTagSet.tagset_id == tagset_id) &
        (TagTagSet.tag.has(tag=tag))).delete(synchronize_session=False)
    db.session.commit()


@defaults
def tagsets_tagset_id_tag_put(tagset_id: int, tag: str) -> typing.Union[dict, tuple]:
    add_tag_to_tagset_sql = text("""
    INSERT INTO %(tag_tagset_table)s (tag_id, tagset_id)
    SELECT tag.id as tag_id, :tagset_id as tagset_id
    FROM %(tag_table)s as tag
    JOIN %(tag_user_table)s as tag_user ON tag.id = tag_user.tag_id AND tag_user.user_id = :user_id
    WHERE tag.tag = :tag
    ON CONFLICT DO NOTHING
    RETURNING id;
    """ % table_names(tag_tagset_table=TagTagSet, tag_table=Tag, tag_user_table=TagUser))
    result = list(db.engine.execute(add_tag_to_tagset_sql.execution_options(autocommit=True),
                                    user_id=current_user_dao.id,
                                    tagset_id=tagset_id,
                                    tag=tag))
    if len(result) != 1:
        return dict(error="could not add tag to tagset"), 400
