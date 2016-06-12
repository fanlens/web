#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, ForeignKey

from db.models.tags import TagSet
from web.modules.database import db
from web.model.user import User


class UserToTagSet(db.Model):
    __tablename__ = "user_tagset"

    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<UserToTagSet(user_id='%s', tagset_id='%s')>" % (self.user_id, self.tagset_id)
