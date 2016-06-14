#!/usr/bin/env python
# -*- coding: utf-8 -*-

import typing

from sqlalchemy import text

from db import flag_modified
from db.models.facebook import FacebookCommentEntry
from web.modules.database import db
from web.model.meta import MetaFields, Defaults, Types, Included


class MetaController(object):
    _list_stats = text("""
        SELECT
          unrolled.field AS field,
          count(*)       AS c
        FROM (
               SELECT jsonb_array_elements_text(meta :: JSONB -> :field) AS field
               FROM data.facebook_comments
               WHERE :ignore_page OR meta :: JSONB ->> 'page' in :page
             ) AS unrolled
        GROUP BY field
        ORDER BY c DESC
        """)
    _scalar_stats = text("""
        SELECT
          meta :: JSONB ->> :field AS field,
          count(*)                 AS c
        FROM data.facebook_comments
        WHERE :ignore_page OR meta :: JSONB ->> 'page' in :page
        GROUP BY field
        ORDER BY c DESC
        """)

    @classmethod
    def get_all(cls, obj_id: str):
        result = {}
        for field in MetaFields:
            result[field.value] = cls.get(obj_id, field)
        return result

    @classmethod
    def set_all(cls, obj_id: str, values: dict):
        for field in MetaFields:
            if field.value in values:
                cls.set(obj_id, field, values[field.value], commit=False)
        db.session.commit()

    @classmethod
    def get(cls, obj_id: str, key: MetaFields) -> typing.Any:
        comment = db.session.query(FacebookCommentEntry).get(obj_id)
        if comment:
            return comment.meta.get(key.value, Defaults[key])
        else:
            return None

    @classmethod
    def set(cls, obj_id: str, key: MetaFields, value: typing.Any, commit=True) -> typing.Any:
        entry = FacebookCommentEntry(id=obj_id)
        entry = db.session.merge(entry)
        entry.meta[key.value] = value
        flag_modified(entry, 'meta')
        if commit:
            db.session.commit()

    @classmethod
    def get_all_stats(cls, source_id: str = None):
        result = {}
        for field in MetaFields:
            if field in Included:
                result[field.value] = cls.get_stats(field, source_id)
        return result

    @classmethod
    def get_stats(cls, key: MetaFields,
                  pages: typing.Union[typing.AnyStr, typing.Set[typing.AnyStr]] = None) -> typing.Any:
        ignore_pages = pages is None or len(pages) == 0
        if ignore_pages:
            pages = {None}
        if not isinstance(pages, set):
            pages = {pages}
        if Types[key] == typing.AnyStr:
            sql = cls._scalar_stats
        elif Types[key] == typing.Iterable:
            sql = cls._list_stats
        stats = db.session.execute(sql, dict(field=key.value, ignore_page=ignore_pages, page=tuple(pages)))
        return dict((k, v) for k, v in stats if k is not None)
