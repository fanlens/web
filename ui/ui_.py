#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""do not remove the trailing underscore, needed to make importable in __main__"""

from flask import render_template, Blueprint
from flask_login import login_required, current_user
from flask_security import roles_accepted

ui = Blueprint('ui', __name__)


@ui.route('/', methods=['GET'])
@login_required
@roles_accepted('admin', 'tagger')
def root() -> str:
    return render_template('tagger/tagger.html', api_key=current_user.get_auth_token())
