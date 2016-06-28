#!/usr/bin/env python
# -*- coding: utf-8 -*-
from db.models.brain import Model

from web.modules.database import db
from web.modules.celery import celery


class ModelController(object):
    @classmethod
    def get_stats(cls, user_id, model_id) -> dict:
        model = db.session.query(Model).filter_by(user_id=user_id, id=model_id).one()
        return dict(id=model.id, score=model.score, trained_ts=model.trained_ts)

    @classmethod
    def train_model(cls, user_id, tagset_id, sources=tuple()):
        task_id = celery.send_task('worker.brain.train_model', args=(user_id, tagset_id, sources))
        return task_id
