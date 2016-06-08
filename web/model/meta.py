#!/usr/bin/env python
# -*- coding: utf-8 -*-

import typing
import enum


class MetaFields(enum.Enum):
    LANG = 'lang'
    TAGS = 'tags'
    TOKENS = 'tokens'
    FINGERPRINT = 'fingerprint'
    PAGE = 'page'


Defaults = {
    MetaFields.PAGE: '',
    MetaFields.LANG: 'un',
    MetaFields.TAGS: [],
    MetaFields.TOKENS: [],
    MetaFields.FINGERPRINT: [],
}

Types = {
    MetaFields.PAGE: typing.AnyStr,
    MetaFields.LANG: typing.AnyStr,
    MetaFields.TAGS: typing.Iterable,
    MetaFields.TOKENS: typing.Iterable,
    MetaFields.FINGERPRINT: typing.Iterable,
}

Included = [
    MetaFields.PAGE,
    MetaFields.LANG,
    MetaFields.TAGS,
]
