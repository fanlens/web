"""Implementations for the activities.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring,too-many-arguments
from typing import Union

from flask import Response, redirect
from sqlalchemy import text

from common.db.models.activities import Tag, TagSet, TagSetUser, TagTagSet, TagUser
from . import defaults
from .tags import tags_tag_put
from ..model import table_names
from ..model.activities import tagset_to_json
from ..model.user import current_user_dao
from ...flask_modules import TJson, TJsonResponse, deleted_response, updated_response
from ...flask_modules.database import db


@defaults
def tagsets_get() -> TJsonResponse:
    tagsets = [tagset_to_json(tagset) for tagset in current_user_dao.tagsets]
    return dict(tagSets=tagsets)


@defaults
def tagsets_post(tagset: TJson) -> Union[TJsonResponse, Response]:
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
                                    user_id=current_user_dao.user_id,
                                    tags=tagset['tags'],
                                    title=tagset['title']))
    if not result:
        return dict(error='no tagset created'), 200

    return redirect('/tagset/%d' % result[0][0], code=201)


@defaults
def tagsets_tagset_id_get(tagset_id: int) -> TJsonResponse:
    tagset = current_user_dao.tagsets.filter(TagSet.id == tagset_id).one_or_none()
    if not tagset:
        return dict(error="tagset does not exist"), 404
    return dict(id=tagset.id,
                title=tagset.title,
                tags=[tag.tag for tag in tagset.tags])


@defaults
def tagsets_tagset_id_patch(tagset_id: int, tagset: dict) -> TJsonResponse:
    user_tagset = current_user_dao.tagsets.filter_by(id=tagset_id).one_or_none()
    if user_tagset is None:
        return dict(error="tagset does not exist"), 404
    if 'id' in tagset:
        return dict(error="tagset id cannot be changed!"), 400
    if 'title' in tagset:
        user_tagset.title = tagset['title']
    if 'tags' in tagset:
        tags = set(tagset['tags'])
        for tag in tags:  # make sure all tags are in DB
            tags_tag_put(tag, commit=False)
        user_tagset.tags.update(
            db.session.query(Tag).filter(Tag.user.any(id=current_user_dao.user_id)).filter(Tag.tag.in_(tags)))
    db.session.commit()

    return dict(id=user_tagset.id,
                title=user_tagset.title,
                tags=[tag.tag for tag in user_tagset.tags]), 200


@defaults
def tagsets_tagset_id_delete(tagset_id: int) -> TJsonResponse:
    current_user_dao.tagsets.filter(TagSet.id == tagset_id).delete(synchronize_session=False)
    db.session.commit()
    return deleted_response()


@defaults
def tagsets_tagset_id_tag_put(tagset_id: int, tag: str) -> TJsonResponse:
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
                                    user_id=current_user_dao.user_id,
                                    tagset_id=tagset_id,
                                    tag=tag))
    if len(result) != 1:
        return dict(error="could not add tag to tagset"), 400
    return updated_response()


@defaults
def tagsets_tagset_id_tag_delete(tagset_id: int, tag: str) -> TJsonResponse:
    db.session.query(TagTagSet).filter(
        TagTagSet.tagset_id.in_(current_user_dao.tagset_ids) &
        (TagTagSet.tagset_id == tagset_id) &
        (TagTagSet.tag.has(tag=tag))).delete(synchronize_session=False)
    db.session.commit()
    return deleted_response()
