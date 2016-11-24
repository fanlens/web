#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_login import current_user
from flask_modules import annotation_composer
from flask_modules.security import csrf
from flask_security import auth_token_required, roles_accepted

defaults = annotation_composer(
    auth_token_required,
    csrf.exempt,
    roles_accepted('admin', 'tagger'))


def check_sources_by_id(sources: set):
    is_sub = sources.issubset(source.id for source in current_user.sources)
    if not is_sub:
        return dict(error='User does not have access to all requested sources'), 403
    return None
