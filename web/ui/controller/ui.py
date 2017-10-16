"""Blueprint for user interface (the single page app) entry points"""
from flask import Blueprint, Response, g, redirect, render_template, request, send_file
from flask_security import current_user, login_required

from common.config import get_config
from ...flask_modules.jwt import create_jwt_for_user

_CONFIG = get_config()

UI_BP = Blueprint('ui', __name__, url_prefix='/%s/ui' % _CONFIG.get('DEFAULT', 'version'))
UI_NONAUTH_BP = Blueprint('ui_nonauth', __name__)


@UI_BP.route('/static/app.js')
def appjs() -> Response:
    """:return: the single page javascript app"""
    return send_file('static/app.js')


def _hand_off_to_app(path: str) -> Response:
    return render_template('ui.html',
                           bot_id=_CONFIG.get("BOT", "client_id"),
                           jwt=create_jwt_for_user(current_user
                                                   if current_user.has_role('tagger')
                                                   else g.demo_user),
                           auth_token=(
                               current_user.get_auth_token()
                               if current_user.has_role('tagger')
                               else g.demo_user.get_auth_token()),
                           path=path,
                           version=_CONFIG.get('DEFAULT', 'version'))


@UI_NONAUTH_BP.route('/legal')
@UI_NONAUTH_BP.route('/team')
@UI_NONAUTH_BP.route('/enterprise')
def nonauth() -> Response:
    """Other (landing) pages implemented by the single page app."""
    return _hand_off_to_app(request.path)


@UI_NONAUTH_BP.route('/v1/<path:path>')
@UI_NONAUTH_BP.route('/v2/<path:path>')
@UI_NONAUTH_BP.route('/v3/<path:path>')
def redir_old_new(path: str) -> Response:
    """Redirects call to old versions to the new version"""
    return redirect('/%s/%s' % (_CONFIG.get('DEFAULT', 'version'), path))


@UI_BP.route('/', defaults={'path': ''})
@UI_BP.route('/<path:path>')
@login_required
def root(path: str) -> Response:
    """Catch all for ui paths. Hands the path off to the single page app."""
    return _hand_off_to_app(path)
