#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask

# todo switch to nginx for file serving!
app = Flask(__name__, static_url_path='/assets')


@app.route('/', methods=['GET'])
def httpchk():
    return 'ok'
