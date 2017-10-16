"""Controllers implementing the Swagger specification"""

from flask_jwt_simple import jwt_required

from ...flask_modules import annotation_composer
from ...flask_modules.jwt import roles_any

defaults = annotation_composer(
    jwt_required,
    roles_any('admin', 'tagger'),
)
