#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import g
from sqlalchemy.sql import text

from db import flag_modified

from db.models.facebook import FacebookCommentEntry


class TaggerController(object):
    _random_comment_sql = text("""
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
LIMIT :limit""")

    _sources_sql = text("select distinct(meta::jsonb->>'page') as source from data.facebook_comments")

    @classmethod
    def get_sources(cls) -> list:
        query = g.db_session.execute(cls._sources_sql)
        return sorted([r[0] for r in query])

    @classmethod
    def get_random_comments(cls, count=1, with_entity=False, with_suggestion=False, sources=None):
        # todo: using frac of 1.0 might be pretty slow
        if sources is None:
            sources = [None]
            ignore_source = True
        else:
            ignore_source = False
        query = g.db_session.execute(cls._random_comment_sql,
                                     dict(frac=1.0, limit=count, lang='en', ignore_source=ignore_source,
                                          sources=tuple(sources)))

        if with_entity:
            results = [dict((k, v) for k, v in zip(query.keys(), r)) for r in query]
        else:
            results = [{'id': r[0]} for r in query]

        if with_suggestion:
            for result in results:
                result['suggestion'] = cls.get_suggestions_for_id(result['id'])
            for result in results:
                result['suggestion'] = cls.get_suggestions_for_id(result['id']).get(interval=0.0005)
        return results

    @classmethod
    def get_tags_for(cls, comment_id: str) -> dict:
        row = g.db_session.query(FacebookCommentEntry).get(comment_id)
        if not row:
            return None
        return dict(id=row.id, tags=row.meta['tags'])

    @classmethod
    def patch_tags(cls, comment_id: str, add=set(), remove=set()) -> dict:
        if any([len(tag) > 64 for tag in add.union(remove)]):  # todo proper db validation
            raise ValueError('tags are limited to 64 characters')
        entry = g.db_session.merge(FacebookCommentEntry(id=comment_id))
        entry.meta['tags'] = sorted(list(set(entry.meta.get('tags', [])).union(add).difference(remove)))
        flag_modified(entry, 'meta')
        g.db_session.commit()
        return {'id': entry.id, 'tags': entry.meta['tags']}

    @classmethod
    def get_suggestions_for_id(cls, comment_id: str) -> tuple:
        # todo do some nice mapping
        comment = g.db_session.query(FacebookCommentEntry).get(comment_id)
        if not comment or 'fingerprint' not in comment.meta or 'tokens' not in comment.meta:
            raise ValueError
        else:
            return g.celery.send_task('worker.brain.predict', args=(
            dict(tokens=comment.meta['tokens'], fingerprint=comment.meta['fingerprint']),),
                                      kwargs=dict(model_id='debug_tagger'))
