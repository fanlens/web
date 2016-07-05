#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request, jsonify, render_template, Blueprint, redirect, url_for
from flask_security import current_user
from flask_security.decorators import login_required, roles_accepted, roles_required

from web.modules.security import csrf

from web.modules.celery import celery

from web.routes import request_wants_json
from web.controller.tagger import TaggerController
from web.controller.tagset import TagSetController
from web.controller.model import ModelController

tagger = Blueprint('tagger', __name__, template_folder='templates')

csrf.exempt(tagger)


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
        comment_ids = TaggerController.get_random_comments(current_user.id, count=count, with_entity=with_entity,
                                                           with_suggestion=with_suggestion, sources=sources)
        return jsonify({"comments": comment_ids})
    else:
        return render_template('apps/tagger.html')


@tagger.route('/comments/<string:obj_id>')
def get(obj_id: str):
    tags = TaggerController.get_tags_for(obj_id, current_user.id)
    return jsonify(tags)


@tagger.route('/comments/<string:obj_id>', methods=['PATCH'])
def add_tag(obj_id: str):
    patch = request.json
    add = set(patch.get('add', set()))
    remove = set(patch.get('remove', set()))
    try:
        amended = TaggerController.patch_tags(obj_id, current_user.id, add, remove)
        return jsonify(amended)
    except ValueError as err:
        return jsonify(error=err.args), 400


@tagger.route('/sources/')
def sources():
    return jsonify({'sources': [source.slug or source.external_id for source in
                                current_user.sources]})  # todo switch to internal id?!


@tagger.route('/tagsets/')
def user_tagsets():
    include_all = request.args.get('include_all', '').lower() in ("1", "true")
    tagsets = dict((str(tagset.id), dict(id=tagset.id, title=tagset.title, tags=[tag.tag for tag in tagset.tags]))
                   for tagset in current_user.tagsets)
    if include_all:
        all_tags = set()
        for tagset in tagsets.values():
            all_tags = all_tags.union(tagset['tags'])
        tagsets['_all'] = dict(id='_all', tags=list(all_tags), title='All Tags')
    return jsonify(tagSets=tagsets)


@tagger.route('/tags/')
def user_tags():
    return jsonify(tags=list(set([tag.tag for tagset in current_user.tagsets for tag in tagset.tags])))


@tagger.route('/tags/_counts')
def user_tags_counts():
    return jsonify(tags=TaggerController.get_tag_counts_for_user_id(current_user.id))


@tagger.route('/tags/_all')
@roles_required('admin')
def all_tags():
    return jsonify(tags=TagSetController.get_all_tags())


@tagger.route('/comments/<string:obj_id>/suggestion', methods=['GET'])
def suggest(obj_id: str):
    try:
        [suggestion, ] = TaggerController.get_suggestions_for_id(obj_id)
        return jsonify(id=obj_id, suggestion=suggestion)
    except KeyError:
        return jsonify(error='object with id %s not found' % obj_id), 404


@tagger.route('/suggestion', methods=['POST'])
def suggest_new():
    try:
        text = request.json['text']
        suggestion = TaggerController.get_suggestions_for_text(text)
        return jsonify(text=text, suggestion=suggestion)
    except KeyError:
        return jsonify(error='no text field in request'), 400
    except Exception as err:
        return jsonify(error=str(err.args)), 400


@tagger.route('/train', methods=['POST'])
@roles_required('admin')
def train():
    try:
        tagset = request.json['tagset']
        sources = request.json.get('sources', tuple())
        task_id = ModelController.train_model(current_user.id, tagset, sources)
        return jsonify(status='job added to queue'), 303, {'Retry-After': 30,
                                                           'Location': url_for('tagger.training_status',
                                                                               status_id=task_id)}
    except KeyError:
        return jsonify(error='please provide the tagset and sources in your request'), 400


@tagger.route('/train/<string:status_id>', methods=['GET'])
@roles_required('admin')
def training_status(status_id: str):
    result = celery.AsyncResult(status_id)
    if result.ready():
        if result.successful():
            model_id = result.get(timeout=2)
            return redirect(url_for('tagger.model_stats', model_id=model_id), code=201)
        elif result.failed():
            return jsonify(error='model could not be created'), 410
    else:  # still running
        if result.state == 'PENDING':  # most likely doesn't exist
            # todo strictly speaking not 404, the task could be simply not started yet
            return jsonify(error='no job with id ' + status_id), 404
        else:
            # lot of debate what to return, 503 is semantically not really true since the server itself is still running
            # but 503 has better support for polling/Retry-After, other candidates 200, 304
            return jsonify(status='still running...'), 503, {'Retry-After': 30,
                                                             'Location': url_for('tagger.training_status',
                                                                                 status_id=status_id)}


@tagger.route('/model/<string:model_id>', methods=['GET'])
@roles_required('admin')
def model_stats(model_id: str):
    stats = ModelController.get_stats(current_user.id, model_id)
    return jsonify(stats=stats)
