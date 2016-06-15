#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, Blueprint, redirect, url_for

index = Blueprint('index', __name__)


@index.route('/')
def root():
    return redirect(url_for('tagger.random_comments'), code=302)
#    """main index.html"""
#    return render_template('landing/index.html')
