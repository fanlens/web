#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import request
from connexion.operation import Operation
from connexion.resolver import Resolver, Resolution


def request_wants_json():
    best = request.accept_mimetypes \
        .best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
           request.accept_mimetypes[best] > \
           request.accept_mimetypes['text/html']


class SimpleResolver(Resolver):
    def __init__(self, module):
        self._module = module

    def resolve(self, operation: Operation):
        parts = []
        if operation.path == '/':
            parts.append('root')
        else:
            for part in operation.path.split('/'):
                if part:
                    parts.append(part)
        parts.append(operation.method)
        func_name = '_'.join(parts).replace('{', '').replace('}', '')
        func = getattr(self._module, func_name)

        return Resolution(func, func_name)


def annotation_composer(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f

    return deco
