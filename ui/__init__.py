#!/usr/bin/env python
# -*- coding: utf-8 -*-


def create_app():
    import connexion

    from flask_modules.mail import setup_mail
    from flask_modules.security import setup_security
    from flask_modules.database import setup_db
    from flask_modules.logging import setup_logging

    app = connexion.App(__name__, specification_dir='swagger')

    setup_logging(app.app)
    setup_db(app.app)
    setup_mail(app.app)
    setup_security(app.app)

    from flask_modules import SimpleResolver
    from .controller.catchall import catchall
    from .controller.forwards import forwards
    from .controller import ui

    app.app.register_blueprint(forwards)
    app.app.register_blueprint(catchall)
    app.add_api('ui.yaml', validate_responses=True, resolver=SimpleResolver(ui))
    app.add_url_rule('/', 'health', lambda: 'ok')
    return app


app = create_app()
