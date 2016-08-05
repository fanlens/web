#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.models.tags import Tag

from flask_modules.database import db


class TagSetController(object):
    @classmethod
    def get_all_tags(cls):
        return [tag for tag, in db.session.query(Tag.tag)]
