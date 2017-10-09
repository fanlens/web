#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Models and helpers for activities api """

from typing import Any, Callable, Dict, Union, List

from sqlalchemy import text

from common.db.models.activities import Data, Lang, Source, TagSet, Type
from common.db.models.brain import Prediction
from .user import current_user_dao


def source_to_json(source: Source) -> Dict[str, Union[int, str]]:
    """
    :param source: `Source` to convert
    :return: a dict corresponding to the Swagger specification
    """
    return dict(
        id=source.id,
        type=source.type,
        uri=source.uri,
        slug=source.slug)


def tagset_to_json(tagset: TagSet) -> Dict[str, Union[int, str, List[str]]]:
    """
    :param tagset: `TagSet` to convert
    :return: a dict corresponding to the Swagger specification
    """
    return dict(
        id=tagset.id,
        title=tagset.title,
        tags=[tag.tag for tag in tagset.tags])


class ActivityParser(object):
    """Activity parsing, i.e. converting them into the format expected by the Swagger definition"""
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

    @classmethod
    def _common(cls, data: Data) -> Dict[str, Any]:
        # todo for large amount of rows this is very inefficient
        return dict(text=data.text.text if data.text else "",
                    source=dict(id=data.source.id,
                                type=data.source.type,
                                uri=data.source.uri,
                                slug=data.source.slug),
                    tags=[tag.tag for tag in data.tags],
                    created_time=data.time.time.isoformat() if data.time else '1970-01-01T00:00:00+00:00',
                    language=data.language.language.name if data.language else Lang.un.name,
                    prediction=dict(
                        (prediction.model.tags.filter_by(id=k).one().tag, v)
                        for prediction in data.predictions.filter(
                            Prediction.model_id.in_(
                                cls._best_models_for_user_sql.bindparams(user_id=current_user_dao.user_id)))
                        for k, v in prediction.prediction)
                    if data.predictions else dict())

    @staticmethod
    def _facebook(data: Data) -> Dict[str, Any]:
        return dict(id=data.data['id'],
                    user=data.data.get('from', dict(id=data.data['id'].split('_')[0])))

    @staticmethod
    def _twitter(data: Data) -> Dict[str, Any]:
        return dict(id=data.data['id_str'],
                    user=dict(id=data.data['user']['screen_name'], name=data.data['user']['name']))

    @staticmethod
    def _twitter_dm(data: Data) -> Dict[str, Any]:
        return dict(id=data.data['id'],
                    user=dict(id=data.data['message_create']['sender_id'],
                              name=data.data['message_create']['sender_id']))

    @staticmethod
    def _crunchbase(data: Data) -> Dict[str, Any]:
        raise NotImplementedError("Currently not supported")

    @staticmethod
    def _generic(data: Data) -> Dict[str, Any]:
        return dict(id=str(data.data['comment_id']),
                    user=dict(id=str(data.data['user']['id']),
                              name=data.data['user']['id']))

    def __call__(self, data: Data) -> Dict[str, Any]:
        """
        :param data: the `Data` object to convert
        :return: a dict corresponding to the Swagger specification
        """
        data_type = Type(data.source.type)
        parser_name = '_' + data_type.name
        assert hasattr(self, parser_name)
        parser: Callable[[Data], Dict[str, Any]] = getattr(self, parser_name)

        parsed = self._common(data)
        parsed.update(parser(data))
        return parsed


_ACTIVITY_PARSER = ActivityParser()


def parse(data: Data) -> Dict[str, Any]:
    """ Helper method to invoke the default activity parse, see `ActivityParser.__call__` """
    return _ACTIVITY_PARSER(data)
