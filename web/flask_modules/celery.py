#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""`Celery` background tasks module and Proxies"""
from abc import ABC, abstractmethod
from typing import Any, Callable, cast

from celery import Celery
from celery.result import AsyncResult
from flask import Flask

from common.config import get_config
from . import FlaskModule


class FlaskCelery(FlaskModule, Celery):
    """
    Flask module for `Celery` interaction.
    The following config params are the minimum required. See official `Celery` documentation for more options.
        * CELERY_ALWAYS_EAGER
        * CELERY_TASK_SERIALIZER
        * CELERY_RESULT_SERIALIZER
        * CELERY_ACCEPT_CONTENT
        * CELERY_IGNORE_RESULT
        * CELERY_TRACK_STARTED
    """

    def init_app(self: 'FlaskCelery', app: Flask) -> None:
        app.config.setdefault('CELERY_ALWAYS_EAGER', False)  # important so it doesn't get executed locally!
        app.config.setdefault('CELERY_TASK_SERIALIZER', 'msgpack')
        app.config.setdefault('CELERY_RESULT_SERIALIZER', 'msgpack')
        app.config.setdefault('CELERY_ACCEPT_CONTENT', ['msgpack'])
        app.config.setdefault('CELERY_IGNORE_RESULT', False)
        app.config.setdefault('CELERY_TRACK_STARTED', True)

        config = get_config()
        Celery.__init__(cast(Celery, self), app.import_name,
                        backend=config.get('CELERY', 'backend'),
                        broker=config.get('CELERY', 'broker'))
        self.conf.update(app.config)
        self._monkey_patch(app)

    def _monkey_patch(self: Celery, app: Flask) -> None:
        """wrap task calls with app context, see also: http://flask.pocoo.org/docs/0.12/patterns/celery/"""
        # it's called monkey patch for a reason pylint: disable=invalid-name,missing-docstring

        task_base = self.Task

        class ContextTask(task_base):  # type: ignore
            abstract = True

            def __call__(self, *args, **kwargs):  # type: ignore
                with app.app_context():
                    return task_base.__call__(self, *args, **kwargs)

        self.Task = ContextTask


celery = FlaskCelery()


def setup_celery(app: Flask) -> None:
    """
    Add `Celery` cababilities to app
    :param app: the `Flask` app
    """
    celery.init_app(app)


class Proxy(ABC):
    """
    Proxy classes allow loose coupling and not having an explicit dependency on the fanlens-brain package
    They are light wrappers that send a task to the `Celery` queue by name
    """

    @property
    @abstractmethod
    def module_name(self) -> str:
        """:return: the name of the tasks module"""
        raise NotImplementedError("Must be overriden")

    def __getattr__(self, fun_name: str) -> Callable[..., AsyncResult]:
        def dispatch(*args: Any, **kwargs: Any) -> AsyncResult:
            """
            Wrapper that sends a task to `Celery` to be executed
            :param args: additional arguments to send along
            :param args: additional keyword arguments to send along
            """
            return celery.send_task(f"{self.tasks_module}.{fun_name}", args=args, kwargs=kwargs)

        return dispatch


class Brain(Proxy):
    """Proxy class for `brain_tasks`"""

    @property
    def module_name(self) -> str:
        return 'worker.brain_tasks'

    __slots__ = ('train_model', 'predict_text')


class Scrape(Proxy):
    """Proxy class for `scrape_tasks`"""

    @property
    def module_name(self) -> str:
        return 'worker.scrape_tasks'

    __slots__ = ('scrape_meta_for_url',)


brain = Brain()
scrape = Scrape()
