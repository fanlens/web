#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from db.models.tags import Tag, TagToTagSet, TagSet, UserToTagSet

from web.modules.database import db


class TagSetController(object):
    @classmethod
    def get_all_tags(cls):
        return [tag for tag, in db.session.query(Tag.tag)]
