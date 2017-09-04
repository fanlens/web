#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import redirect, request
from flask_modules.database import db
from flask_security import login_required, current_user
from db import insert_or_ignore
from db.models.users import TwitterAuth, UserTwitterAuth, User
from flask_modules.twitter import twitter_auth, ExtendedTweepyApi


def user_twitter_auth(user: User):
    twauth = user.twitter.one().auth
    auth = twitter_auth()
    auth.set_access_token(twauth.oauth_token, twauth.oauth_token_secret)
    return auth


def current_user_twitter_auth():
    return user_twitter_auth(current_user)


def signin_get(next: str = ""):
    auth = twitter_auth(next)
    auth_url = auth.get_authorization_url(signin_with_twitter=True)
    db.session.add(TwitterAuth(oauth_token=auth.request_token['oauth_token'],
                               oauth_token_secret=auth.request_token['oauth_token_secret']))
    db.session.commit()
    return redirect(auth_url)


def callback_get(next: str, oauth_token: str, oauth_verifier: str):
    stored_query = db.session.query(TwitterAuth).filter_by(oauth_token=oauth_token)
    stored = stored_query.one()
    request_token = dict(oauth_token=stored.oauth_token, oauth_token_secret=stored.oauth_token_secret)

    auth = twitter_auth()
    auth.request_token = request_token
    access_token, access_token_secret = auth.get_access_token(verifier=oauth_verifier)
    screen_name = auth.get_username()

    insert_or_ignore(db.session, TwitterAuth(oauth_token=access_token, oauth_token_secret=access_token_secret))
    db.session.query(UserTwitterAuth).filter_by(screen_name=screen_name).update(dict(oauth_token=access_token),
                                                                                synchronize_session=False)
    db.session.commit()
    return redirect(next)


from tweepy.error import TweepError
import logging


@login_required
def test_get():
    try:
        auth = current_user_twitter_auth()
        twitter = ExtendedTweepyApi(auth_handler=auth)
        return twitter.direct_messages_events_list(count=50)
    except (TweepError, Exception) as err:
        logging.exception(err)
        return redirect('/v4/twitter/signin?next=/v4/twitter/test')
