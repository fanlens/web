#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""package used for the ai components of the fanlens project"""

from setuptools import setup, find_packages

setup(
    name="fanlens-web",
    version="4.0.0",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'fanlens-common',

        'Flask',
        'flask-security',
        'flask-cors',
        'flask-sqlalchemy',
        'psycopg2',
        'Flask-Redis',
        'redis',
        'Flask-Cache',
        'connexion',
        'celery[redis]',
        'msgpack-python',
        'requests',
        'Tweepy',
    ],
)
