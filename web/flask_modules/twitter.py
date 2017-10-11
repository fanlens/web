#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Twitter Module"""

import warnings
from typing import Any, Callable, NamedTuple, Optional

from flask import Flask
from tweepy import API, OAuthHandler, binder

from common.config import get_config
from . import FlaskModule, NotInitializedException

_CONFIG = get_config()


class TwitterCredentials(NamedTuple):
    """DTO carrying twitter credentials"""
    consumer_key: str
    consumer_secret: str


class Twitter(FlaskModule):
    """
    Flask module for setting up twitter access.
    Credentials can be provided via the config variables:
        * TWITTER_CONSUMER_KEY
        * TWITTER_CONSUMER_SECRET
    A specialized callback location for the twitter oauth flow can be provided via:
        * TWITTER_CALLBACK, default: '%(host)s/%(version)s/twitter/callback?next=%(next)s'
        host, version, and next can be used as template variables
    """

    def __init__(self, app: Optional[Flask] = None) -> None:
        self._credentials: Optional[TwitterCredentials] = None
        self._callback: Optional[str] = None
        super().__init__(app)

    def init_app(self, app: Flask) -> None:
        if 'TWITTER_CONSUMER_KEY' not in app.config or 'TWITTER_CONSUMER_SECRET' not in app.config:
            warnings.warn("Twitter credentials not provided!")

        app.config.setdefault('TWITTER_CONSUMER_KEY', None)
        app.config.setdefault('TWITTER_CONSUMER_SECRET', None)
        app.config.setdefault('TWITTER_CALLBACK', '%(host)s/%(version)s/twitter/callback?next=%(next)s')
        self._credentials = TwitterCredentials(app.config['TWITTER_CONSUMER_KEY'],
                                               app.config['TWITTER_CONSUMER_KEY'])
        self._callback = app.config['TWITTER_CALLBACK']

    def twitter_auth(self, next_page: str = "/") -> OAuthHandler:
        """
        :param next_page: the page to redirect to after the auth flow
        :return: the twitter oauth handler
        """
        auth = OAuthHandler(self.credentials.consumer_key,
                            self.credentials.consumer_secret,
                            callback=self.callback(next_page))
        auth.secure = True
        return auth

    @property
    def credentials(self) -> TwitterCredentials:
        """
        :return: the credentials for this twitter module
        :raise NotInitializedException: if app has not been initialized
        """
        if self._credentials is None:
            raise NotInitializedException("Twitter FlaskModule not initialized")
        return self._credentials

    def callback(self, next_page: str, host: Optional[str] = None, version: Optional[str] = None) -> str:
        """
        Fill callback template string
        :param next_page: fill next parameter of template
        :param host: override default host
        :param version: override defautl version
        :return: the callback for this twitter module
        :raise NotInitializedException: if app has not been initialized
        """
        if self._callback is None:
            raise NotInitializedException("Twitter FlaskModule not initialized")
        return self._callback % dict(host=host or _CONFIG.get('WEB', 'host'),
                                     version=version or _CONFIG.get('DEFAULT', 'version'),
                                     next=next_page)


twitter = Twitter()


def setup_twitter(app: Flask) -> None:
    """
    Set up the twitter module for the app
    :param app: the `Flask` app
    """
    app.config['TWITTER_CONSUMER_KEY'] = _CONFIG.get('TWITTER', 'consumer_key')
    app.config['TWITTER_CONSUMER_SECRET'] = _CONFIG.get('TWITTER', 'consumer_secret')
    twitter.init_app(app)


class ExtendedTweepyApi(API):
    """Wrapper around Tweepy enabling new experimental endpoints"""

    @property
    def direct_messages_events_list(self) -> Callable[..., Any]:
        """ :reference: https://dev.twitter.com/rest/reference/get/direct_messages/events/list
            :allowed_param: 'cursor', 'count'
        """
        bound_api: Callable[..., Any] = binder.bind_api(api=self,
                                                        require_auth=True,
                                                        path='/direct_messages/events/list.json',
                                                        payload_type='json',
                                                        allowed_param=['count', 'cursor'],
                                                        use_cache=False)
        return bound_api
