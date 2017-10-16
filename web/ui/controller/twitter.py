"""Implementations for the twitter.yaml Swagger definition. See yaml / Swagger UI for documentation."""
from typing import Optional

from flask import Response, redirect
from flask_security import current_user, login_required
from tweepy.error import TweepError

from common.config import get_config
from common.db import insert_or_ignore
from common.db.models.users import TwitterAuth, User, UserTwitterAuth
from ...flask_modules.database import db
from ...flask_modules.logging import logger
from ...flask_modules.twitter import ExtendedTweepyApi, OAuthHandler, twitter

_VERSION = get_config().get('DEFAULT', 'version')


def _user_twitter_auth(user: User) -> Optional[OAuthHandler]:
    user_twitter_auth: Optional[UserTwitterAuth] = user.twitter.one_or_none()
    if not user_twitter_auth:
        return None
    twitter_auth: TwitterAuth = user_twitter_auth.auth
    auth = twitter.twitter_auth()
    auth.set_access_token(twitter_auth.oauth_token, twitter_auth.oauth_token_secret)
    return auth


def signin_get(next_page: str = "") -> Response:
    """
    Starts the signing flow. The first step is to store the preliminary oauth token in the database. This
    token is not associated with a user yet
    :param next_page: the page to redirect to after the sign in flow
    :return: a redirect to the twitter auth url
    """
    auth = twitter.twitter_auth(next_page)
    auth_url = auth.get_authorization_url(signin_with_twitter=True)
    db.session.add(TwitterAuth(oauth_token=auth.request_token['oauth_token'],
                               oauth_token_secret=auth.request_token['oauth_token_secret']))
    db.session.commit()
    return redirect(auth_url)


def callback_get(next_page: str, oauth_token: str, oauth_verifier: str) -> Response:
    """
    Invoked as second step by the twitter oauth flow.
    Loads the preliminary oauth token from the database
    :param next_page: the page to redirect to after the sign in flow
    :param oauth_token: request token provided by twitter
    :param oauth_verifier: request token verifier provided by twitter
    :return: a redirect to the specified "next_page"
    """
    # load preliminary token
    preliminary_query = db.session.query(TwitterAuth).filter_by(oauth_token=oauth_token)
    preliminary = preliminary_query.one()
    # replace the request token of the oauth handler
    request_token = dict(oauth_token=preliminary.oauth_token, oauth_token_secret=preliminary.oauth_token_secret)
    auth = twitter.twitter_auth()
    auth.request_token = request_token

    # fetch the correct access token and its associated screen name
    access_token, access_token_secret = auth.get_access_token(verifier=oauth_verifier)
    screen_name = auth.get_username()

    # store the token in the database and associated it to the user
    insert_or_ignore(db.session, TwitterAuth(oauth_token=access_token, oauth_token_secret=access_token_secret))
    db.session.query(UserTwitterAuth).filter_by(screen_name=screen_name).update(dict(oauth_token=access_token),
                                                                                synchronize_session=False)
    db.session.commit()
    return redirect(next_page)


@login_required
def test_get() -> Response:
    """ just for testing purposes"""
    auth = _user_twitter_auth(current_user)
    if auth:
        try:
            twitter_api = ExtendedTweepyApi(auth_handler=auth)
            return twitter_api.direct_messages_events_list(count=50)
        except TweepError as err:
            logger.exception(err)
    return redirect(f'/{_VERSION}/twitter/signin?next=/{_VERSION}/twitter/test')
