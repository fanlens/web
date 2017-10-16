#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Implementations for the activities.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring,too-many-arguments
from typing import Optional, Tuple, Union, cast

from sqlalchemy import text
from sqlalchemy.orm import Query

from common.db import insert_or_ignore
from common.db.models.activities import Data, Language, Source, SourceUser, Tag, TagSetUser, TagTagSet, TagUser, \
    Tagging, Time
from . import defaults
from ..model import table_names
from ..model.activities import parse
from ..model.user import current_user_dao
from ...flask_modules import TJson, TJsonResponse, deleted_response, updated_response
from ...flask_modules.database import db


def _activity_id_query(source_id: int, activity_id: str) -> Query:
    return current_user_dao.data_ids.filter((Source.id == source_id) & (Data.object_id == activity_id))


def _activity_query(source_id: int, activity_id: str) -> Query:
    return current_user_dao.data.filter((Source.id == source_id) & (Data.object_id == activity_id))


@defaults
def root_get(count: int,
             max_id: Optional[str] = None,
             since: Optional[str] = None,
             until: Optional[str] = None,
             source_ids: Optional[list] = None,
             tagset_ids: Optional[list] = None,
             tags: Optional[list] = None,
             languages: Optional[list] = None,
             random: Optional[bool] = False) -> TJsonResponse:
    data_query = (db.session.query(Data)
                  .filter(Data.source_id.in_(current_user_dao.source_ids)))

    if since or until or not random:
        data_query = data_query.join(Time, Time.data_id == Data.id)

    if source_ids:
        data_query = data_query.filter(Data.source_id.in_(source_ids))

    if max_id:
        data_query = data_query.filter(Data.object_id < max_id)

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
                            (TagSetUser.user_id == current_user_dao.user_id))
                      .filter(TagTagSet.tagset_id.in_(tuple(tagset_ids))))
    if tags:
        data_query = (data_query
                      .join(Tagging, Tagging.data_id == Data.id)
                      .join(Tag, Tag.id == Tagging.tag_id)
                      .join(TagUser,
                            (TagUser.tag_id == Tag.id) &
                            (TagUser.user_id == current_user_dao.user_id))
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

    data = [parse(data) for data in data_query]
    return dict(activities=list(data))


@defaults
def source_id_activity_id_get(source_id: int, activity_id: str, _internal: bool = False) -> Union[TJsonResponse, Data]:
    data = _activity_query(source_id, activity_id).one_or_none()
    if not data:
        return dict(error='No activity found for user and %d -> %s' % (source_id, activity_id)), 404
    if _internal:
        return data
    return parse(data)


@defaults
def source_id_activity_id_put(source_id: int,
                              activity_id: str,
                              activity_import: TJson,
                              commit: bool = True) -> TJsonResponse:
    if ('source_id' in activity_import and source_id != activity_import['source_id']) \
            or ('id' in activity_import and activity_id != activity_import['id']):
        db.session.rollback()
        return dict(error="source_id does not match activity"), 400

    if source_id not in current_user_dao.source_ids.all():
        db.session.rollback()
        return dict(error="user not associated to source"), 403

    insert_or_ignore(db.session,
                     Data(source_id=source_id,
                          object_id=activity_id,
                          data=activity_import['data']))
    if commit:
        db.session.commit()
    return updated_response()


@defaults
def source_id_activity_id_delete(source_id: int, activity_id: str, commit: bool = True) -> TJsonResponse:
    db.session.query(Data).filter(Data.id.in_(_activity_id_query(source_id, activity_id))).delete(
        synchronize_session=False)
    if commit:
        db.session.commit()
    return deleted_response()


@defaults
def source_id_activity_id_tags_patch(source_id: int,  # pylint: disable=invalid-name
                                     activity_id: str,
                                     body: dict) -> TJsonResponse:
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
                          user_id=current_user_dao.user_id,
                          add=add or tuple([None]),
                          remove=remove or tuple([None]))

    data: Data = source_id_activity_id_get(source_id, activity_id, _internal=True)
    if isinstance(data, tuple):  # error
        return cast(Tuple[TJson, int], data)
    return {'id': activity_id, 'tags': [tag.tag for tag in data.tags]}
