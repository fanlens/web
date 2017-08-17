#!/usr/bin/env python
# -*- coding: utf-8 -*-

from config.db import Config
from tweepy import OAuthHandler, API, binder

_consumer_key = str
_consumer_secret = str


def twitter_auth(next: str = "/"):
    global _consumer_key
    global _consumer_secret
    auth = OAuthHandler(
        _consumer_key,
        _consumer_secret,
        callback='https://localhost/v4/twitter/callback?next=' + next
    );
    auth.secure = True
    return auth


def setup_twitter(app):
    global _consumer_key
    global _consumer_secret
    twitter_config = Config('twitter')
    _consumer_key = twitter_config['consumer_key']
    _consumer_secret = twitter_config['consumer_secret']


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
