#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, ForeignKey

from db.models.facebook import FacebookCommentEntry
from db.models.tags import TagSet, Tag
from web.modules.database import db
from web.model.user import User


class UserToTagSet(db.Model):
    __tablename__ = "user_tagset"

    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    tagset_id = Column(Integer, ForeignKey(TagSet.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<UserToTagSet(user_id='%s', tagset_id='%s')>" % (self.user_id, self.tagset_id)


class UserToTagToComment(db.Model):
    __tablename__ = "user_tag_comment"
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'), primary_key=True)
    tag = Column(String, ForeignKey(Tag.tag, ondelete='CASCADE'), primary_key=True)
    comment_id = Column(String, ForeignKey(FacebookCommentEntry.id, ondelete='CASCADE'), primary_key=True)

    def __repr__(self):
        return "<UserToTagToComment(user_id='%s', tag='%s', comment_id='%s')>" % (
            self.user_id, self.tag, self.comment_id)
