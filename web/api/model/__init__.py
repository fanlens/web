#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The model Module provides domain specific helpers and data models in addition to the ones provided in the main
common.db.models package
"""

from typing import Dict

from common.db import Base


def table_names(**placeholder: Base) -> Dict[str, str]:
    """
    :param placeholder: the placeholder for the string interpolation
    :return: a dictionary mapping the full table names (value) to their placeholder (key)
    """
    return dict((name, table.__table__.fullname) for name, table in placeholder.items())
