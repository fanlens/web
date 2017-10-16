""" Models and helpers for user api """
from sqlalchemy.orm import Query

from common.db.models.activities import Data, Source, SourceUser, Tag, TagSet, TagSetUser, TagUser
from common.db.models.brain import Model, ModelUser
from common.db.models.users import User
from ...flask_modules.database import db
from ...flask_modules.jwt import current_user_id


class CurrentUserDao(object):
    """
    Helper DAO that creates DB queries for the properties of the _current user_.
    The properties should be self explanatory.
    """

    # should be self explanatory pylint: disable=missing-docstring
    # false positive "no member query" pylint: disable=no-member

    @property
    def user_id(self) -> int:
        return current_user_id()

    @property
    def self(self) -> User:
        return db.session.query(User).filter_by(id=self.user_id)

    @property
    def source_ids(self) -> Query:
        return db.session.query(SourceUser.source_id).filter_by(user_id=self.user_id)

    @property
    def sources(self) -> Query:
        return db.session.query(Source).filter(Source.id.in_(self.source_ids))

    @property
    def data_ids(self) -> Query:
        return db.session.query(Data.id).filter(Data.source_id.in_(self.source_ids))

    @property
    def data(self) -> Query:
        return db.session.query(Data).filter(Data.source_id.in_(self.source_ids))

    @property
    def tag_ids(self) -> Query:
        return db.session.query(TagUser.tag_id).filter_by(user_id=self.user_id)

    @property
    def tags(self) -> Query:
        return db.session.query(Tag).filter(Tag.id.in_(self.tag_ids))

    @property
    def created_tags(self) -> Query:
        return db.session.query(Tag).filter_by(created_by_user_id=self.user_id)

    @property
    def created_tag_ids(self) -> Query:
        return db.session.query(Tag.id).filter_by(created_by_user_id=self.user_id)

    @property
    def tagset_ids(self) -> Query:
        return db.session.query(TagSetUser.tagset_id).filter_by(user_id=self.user_id)

    @property
    def tagsets(self) -> Query:
        return db.session.query(TagSet).filter(TagSet.id.in_(self.tagset_ids))

    @property
    def model_ids(self) -> Query:
        return db.session.query(ModelUser.model_id).filter_by(user_id=self.user_id)

    @property
    def models(self) -> Query:
        return db.session.query(Model).filter(Model.id.in_(self.model_ids))


current_user_dao = CurrentUserDao()
