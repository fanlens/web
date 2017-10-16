""" Models and helpers for model api """
from typing import Any, Dict, Iterable, NamedTuple, Optional

from common.db.models.brain import Model
from .activities import source_to_json, tagset_to_json
from ...flask_modules import TJson
from ...flask_modules.jwt import is_admin


def model_to_json(model: Model) -> Dict[str, Any]:
    """
    :param model: `Model` to convert
    :return: a dict corresponding to the Swagger specification
    """
    result = dict(
        id=str(model.id),
        trained_ts=model.trained_ts,
        tagset=tagset_to_json(model.tagset),
        sources=[source_to_json(source) for source in model.sources])
    if is_admin():
        result['score'] = model.score
        result['params'] = model.params
    return result


class ModelQueryDto(NamedTuple):
    """DTO for model queries"""
    tagset_id: Optional[int]
    source_ids: Optional[Iterable[int]]


def model_query_dto(body: TJson) -> ModelQueryDto:
    """
    Factory method for model query dtos.
    :param body: json body to load from
    :return: a new model query dto instance
    :raise ValueError: if neither tagset_id nor source_id are provided
    """
    tagset_id = body.get('tagset_id')
    source_ids = body.get('source_ids')

    if tagset_id is None and source_ids is None:
        raise ValueError('No criterion specified')
    return ModelQueryDto(tagset_id=tagset_id, source_ids=source_ids)


class PredictionQueryDto(NamedTuple):
    """DTO for prediction queries"""
    text: str


def prediction_query_dto(body: TJson) -> PredictionQueryDto:
    """
    Factory method for prediction query dtos.
    :param body: json body to load from
    :return: a new prediction query dto instance
    :raise ValueError: if no text is provided or the query neither provides tagset_id nor source_id
    """
    text = body.get('text')
    if not text:
        raise ValueError('No text provided')
    return PredictionQueryDto(text=text)
