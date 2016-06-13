#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, jsonify, render_template, Blueprint
from flask_security import current_user
from flask_security.decorators import login_required, roles_accepted, roles_required

from web.routes import request_wants_json
from web.controller.tagger import TaggerController
from web.controller.tagset import TagSetController

tagger = Blueprint('tagger', __name__, template_folder='templates')


@tagger.before_request
@login_required
@roles_accepted('admin', 'tagger')
def enable_global_login_for_bp():
    """forces blueprint wide authentication"""
    pass


@tagger.route('/')
def random_comments():
    if request_wants_json():
        count = int(request.args.get('count', 1))
        sources = request.args.get('sources')
        sources = sources.split(',') if sources else None
        with_entity = request.args.get('with_entity', '').lower() in ("1", "true")
        with_suggestion = request.args.get('with_suggestion', '').lower() in ("1", "true")
        comment_ids = TaggerController.get_random_comments(count=count, with_entity=with_entity,
                                                           with_suggestion=with_suggestion, sources=sources)
        return jsonify({"comments": comment_ids})
    else:
        return render_template('apps/tagger.html')


@tagger.route('/<string:obj_id>')
def get(obj_id: str):
    tags = TaggerController.get_tags_for(obj_id)
    return jsonify(tags)


@tagger.route('/<string:obj_id>', methods=['PATCH'])
def add_tag(obj_id: str):
    patch = request.json
    add = set(patch.get('add', set()))
    remove = set(patch.get('remove', set()))
    amended = TaggerController.patch_tags(obj_id, add, remove)
    return jsonify(amended)


@tagger.route('/<string:obj_id>/suggestions', methods=['GET'])
def suggest(obj_id: str):
    try:
        [suggestion, ] = TaggerController.get_suggestions_for_id(obj_id)
        return jsonify({'id': obj_id, 'suggestion': suggestion})
    except KeyError:
        return jsonify({'error': 'object with id %s not found' % obj_id}), 404


@tagger.route('/_sources')
def sources():
    return jsonify({'sources': TaggerController.get_sources()})

@tagger.route('/_tagsets/')
def user_tagsets():
    include_all = request.args.get('include_all', '').lower() in ("1", "true")
    tag_sets = TagSetController.get_all_tagsets_for_user_id(current_user.id)
    if include_all:
        all_tags = TagSetController.get_all_tags_for_user_id(current_user.id)
        tag_sets.append(dict(id='_all', tags=all_tags, title='All Tags'))
    return jsonify(tagSets=tag_sets)


@tagger.route('/_tags/')
def user_tags():
    return jsonify(tags=TagSetController.get_all_tags_for_user_id(current_user.id))


@tagger.route('/_tagsets/_all')
@roles_required('admin')
def all_tags():
    return jsonify(tags=TagSetController.get_all_tags())