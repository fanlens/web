#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config import get_config
from tweepy import OAuthHandler, API, binder

_config = get_config()
_consumer_key = str
_consumer_secret = str


def setup_twitter(app):
    global _consumer_key
    global _consumer_secret
    _consumer_key = _config.get('TWITTER', 'consumer_key')
    _consumer_secret = _config.get('TWITTER', 'consumer_secret')


def twitter_auth(next: str = "/"):
    global _consumer_key
    global _consumer_secret
    auth = OAuthHandler(
        _consumer_key,
        _consumer_secret,
        callback='%s/%s/twitter/callback?next=%s' % (
            _config.get('WEB', 'host'),
            _config.get('DEFAULT', 'version'),
            next)
    )
    auth.secure = True
    return auth


class ExtendedTweepyApi(API):
    @property
    def direct_messages_events_list(self):
        """ :reference: https://dev.twitter.com/rest/reference/get/direct_messages/events/list
            :allowed_param: 'cursor', 'count'
        """
        return binder.bind_api(
            api=self,
            require_auth=True,
            path='/direct_messages/events/list.json',
            payload_type='json',
            allowed_param=['count', 'cursor'],
            use_cache=False
        )
