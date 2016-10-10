#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_modules import annotation_composer
from flask_modules.security import csrf
from flask_security import auth_token_required, roles_accepted

defaults = annotation_composer(
    auth_token_required,
    csrf.exempt,
    roles_accepted('admin', 'tagger'))