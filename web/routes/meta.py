#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, jsonify, Blueprint, g
from flask_security.decorators import roles_required, roles_accepted, login_required

from web.controller.meta import MetaController
from web.model.meta import MetaFields

meta = Blueprint('meta', __name__, template_folder='templates')


# todo this is somewhat obsolete, refactor tagger.py and meta.py a bit

@meta.before_request
@login_required
@roles_required('admin')
def enable_global_login_for_bp():
    """forces blueprint wide authentication"""
    pass


@meta.route('/_stats/', methods=['GET'])
def stats_all_sources():
    values = MetaController.get_all_stats()
    return jsonify(values), 404 if values is None else 200


@meta.route('/_stats/<string:source_id>', methods=['GET'])
def stats_for_source(source_id: str):
    if ',' in source_id:
        source_id = tuple(source_id.split(','))
    values = MetaController.get_all_stats(source_id)
    return jsonify(values), 404 if values is None else 200


@meta.route('/_stats/<string:source_id>/<string:field>', methods=['GET'])
def field_stats(source_id: str, field: str):
    if ',' in source_id:
        source_id = set(source_id.split(','))
    try:
        field = MetaFields(field)
        value = MetaController.get_stats(field, pages=source_id)
        return jsonify({field.value: value}), 404 if value is None else 200
    except ValueError:
        return jsonify(error='field %s not supported' % field.value), 404


@meta.route('/<string:obj_id>', methods=['GET'])
def get_meta(obj_id: str):
    values = MetaController.get_all(obj_id)
    return jsonify(values), 404 if values is None else 200


# todo proper validation with db constraints
@meta.route('/<string:obj_id>', methods=['PATCH'])
@roles_required('admin')
def patch(obj_id: str):
    if not request.json:
        return jsonify(error='bad request'), 400
    MetaController.set_all(obj_id, request.json)
    values = MetaController.get_all(obj_id)
    return jsonify(values), 404 if values is None else 200


@meta.route('/<string:obj_id>/<string:field>', methods=['GET'])
def get(obj_id: str, field: str):
    try:
        field = MetaFields(field)
        value = MetaController.get(obj_id, field)
        return jsonify({field.value: value}), 404 if value is None else 200
    except ValueError:
        return jsonify(error='field %s not supported' % field.value), 404


# todo proper validation with db constraints
@meta.route('/<string:obj_id>/<string:field>', methods=['PUT'])
@roles_required('admin')
def put(obj_id: str, field: str):
    if not request.json:
        return jsonify(error='bad request'), 400
    value = request.json.get(field)
    try:
        field = MetaFields(field)
        MetaController.set(obj_id, field, value)
        return jsonify({field.value: value})
    except KeyError:
        return jsonify(error='field %s not supported' % field.value), 404
