#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Blueprint

index = Blueprint('index', __name__)


@index.route('/')
def root():
    """main index.html"""
    return render_template('landing/index.html')
