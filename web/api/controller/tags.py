"""Implementations for the activities.yaml Swagger definition. See yaml / Swagger UI for documentation."""
# see swagger pylint: disable=missing-docstring,too-many-arguments
from contextlib import suppress

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from common.db.models.activities import Data, Tag, TagUser, Tagging
from . import defaults
from ..model import table_names
from ..model.user import current_user_dao
from ...flask_modules import TJson, TJsonResponse, deleted_response
from ...flask_modules.database import db
from ...flask_modules.logging import logger


@defaults
def tags_get(with_count: bool = False) -> TJsonResponse:
    if with_count:
        tags: TJson = dict()
        with_count_sql = text("""
        SELECT tag.tag, count(*)
        FROM %(tag_table)s as tag
        JOIN %(tag_user_table)s as tag_user ON tag_user.tag_id = tag.id AND tag_user.user_id = :user_id
        LEFT OUTER JOIN %(tagging_table)s as tagging ON tagging.tag_id = tag.id
        GROUP BY tag.tag  -- tag is unique per user
        """ % table_names(data_table=Data,
                          tagging_table=Tagging,
                          tag_table=Tag,
                          tag_user_table=TagUser))
        tags['count'] = dict((tag, tag_count)
                             for tag, tag_count in db.engine.execute(with_count_sql, user_id=current_user_dao.user_id))
        tags['tags'] = list(tags['count'].keys())
    else:
        tags = dict(tags=[tag.tag for tag in current_user_dao.tags])

    return tags


@defaults
def tags_tag_get(tag: str, with_count: bool = False) -> TJsonResponse:
    the_tag = current_user_dao.tags.filter(Tag.tag == tag).one_or_none()
    if the_tag is None:
        return dict(error="Tag not found"), 404

    result = dict(tag=the_tag.tag)
    if with_count:
        result['count'] = the_tag.data.count()
    return result


@defaults
def tags_tag_put(tag: str, commit: bool = True) -> TJsonResponse:
    tag_obj = Tag(tag=tag, created_by_user_id=current_user_dao.user_id)
    with suppress(IntegrityError):
        db.session.add(tag_obj)
        # todo: performance - one unnecessary roundtrip. ignore until relevant
        current_user_dao.self.one().tags.append(tag_obj)
        if commit:
            db.session.commit()
    return dict(tag=tag_obj.tag), 201


@defaults
def tags_tag_delete(tag: str) -> TJsonResponse:
    current_user_dao.created_tags.filter(Tag.tag == tag).delete()
    db.session.commit()
    return deleted_response()
