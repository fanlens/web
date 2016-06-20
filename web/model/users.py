#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_security import RoleMixin, UserMixin

from db.models.users import Role, User

from web.modules.database import db


class WebRole(db.Model, Role, RoleMixin):
    pass


class WebUser(db.Model, UserMixin, User):
    pass
