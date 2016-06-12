#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from db.models.tags import Tag, TagToTagSet, TagSet
from web.modules.database import db
from web.model.tagset import UserToTagSet


class TagSetController(object):
    @classmethod
    def get_all_tags(cls):
        return [tag for tag, in db.session.query(Tag.tag)]

    @classmethod
    def get_all_tags_for_user_id(cls, user_id):
        return [tag for (_, tag) in UserToTagSet.query.join(TagSet, TagToTagSet, Tag).add_columns(Tag.tag).filter(
            UserToTagSet.user_id == user_id)]

    @classmethod
    def get_all_tagsets_for_user_id(cls, user_id):
        tagsets = defaultdict(lambda: defaultdict(list))
        for _, tag, tagset_id, tagset_title in (UserToTagSet.query
                                                        .join(TagSet, TagToTagSet, Tag)
                                                        .add_columns(Tag.tag, TagSet.id, TagSet.title)
                                                        .filter(UserToTagSet.user_id == user_id)):
            tagsets[tagset_id]['title'] = tagset_title
            tagsets[tagset_id]['id'] = tagset_id
            tagsets[tagset_id]['tags'].append(tag)
        return list(tagsets.values())
