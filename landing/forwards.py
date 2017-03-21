#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, redirect

forwards = Blueprint('forwards', __name__)
forwards.add_url_rule('/jobs/cgo', 'cgo', lambda: redirect('/cdn/img/jobs/cgo.pdf'))

