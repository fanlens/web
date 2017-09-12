#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_jwt_simple import jwt_required
from flask_modules import annotation_composer
from flask_modules.jwt import roles_any, current_user_id
from flask_modules.database import db
from sqlalchemy.orm import Query
from db.models.activities import Source, SourceUser, Data, Tag, TagUser, TagSet, TagSetUser
from db.models.brain import ModelUser, Model
from db.models.users import User

defaults = annotation_composer(
    jwt_required,
    roles_any('admin', 'tagger'),
)


class CurrentUserDao(object):
    @property
    def id(self) -> int:
        return current_user_id()

    @property
    def self(self) -> User:
        return db.session.query(User).filter_by(id=self.id)

    @property
    def source_ids(self) -> Query:
        return db.session.query(SourceUser.source_id).filter_by(user_id=self.id)

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
        return db.session.query(TagUser.tag_id).filter_by(user_id=self.id)

    @property
    def tags(self) -> Query:
        return db.session.query(Tag).filter(Tag.id.in_(self.tag_ids))

    @property
    def created_tags(self) -> Query:
        return db.session.query(Tag).filter_by(created_by_user_id=self.id)

    @property
    def created_tag_ids(self) -> Query:
        return db.session.query(Tag.id).filter_by(created_by_user_id=self.id)

    @property
    def tagset_ids(self) -> Query:
        return db.session.query(TagSetUser.tagset_id).filter_by(user_id=self.id)

    @property
    def tagsets(self) -> Query:
        return db.session.query(TagSet).filter(TagSet.id.in_(self.tagset_ids))

    @property
    def model_ids(self) -> Query:
        return db.session.query(ModelUser.model_id).filter_by(user_id=self.id)

    @property
    def models(self) -> Query:
        return db.session.query(Model).filter(Model.id.in_(self.model_ids))


current_user_dao = CurrentUserDao()


def table_names(**kwargs) -> dict:
    return dict((name, table.__table__.fullname) for name, table in kwargs.items())