#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from flask_security import current_user
from flask_security.decorators import login_required, roles_accepted, roles_required

from web.controller.tagset import TagSetController

tagset = Blueprint('tagset', __name__)


@tagset.before_request
@login_required
@roles_accepted('admin', 'tagger')
def enable_global_login_for_bp():
    """forces blueprint wide authentication"""
    pass


@tagset.route('/sets/')
@login_required
def all_user():
    return jsonify(TagSetController.get_all_tagsets_for_user_id(current_user.id))


@tagset.route('/tags/')
@roles_required('admin')
def user_tags():
    return jsonify(TagSetController.get_all_tags_for_user_id(current_user.id))


@tagset.route('/all/tags/')
@roles_required('admin')
def all_tags():
    return jsonify(TagSetController.get_all_tags())
