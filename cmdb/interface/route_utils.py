# DATAGERRY - OpenSource Enterprise CMDB
# Copyright (C) 2019 NETHINKS GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import base64
import functools
import json
from functools import wraps
from typing import ClassVar

from authlib.jose.errors import ExpiredTokenError
from werkzeug._compat import to_unicode
from werkzeug.http import wsgi_to_bytes

from cmdb.security.auth import AuthModule, AuthenticationProvider
from cmdb.security.token.generator import TokenGenerator
from cmdb.user_management import User
from cmdb.user_management.user_manager import UserManagerGetError, UserManager
from cmdb.utils.system_reader import SystemSettingsReader
from cmdb.utils.wraps import LOGGER

try:
    from cmdb.utils.error import CMDBError
except ImportError:
    CMDBError = Exception

from flask import Blueprint, request, abort, current_app

from cmdb.security.token.validator import TokenValidator, ValidationError
from cmdb.utils import json_encoding

DEFAULT_MIME_TYPE = 'application/json'


class RootBlueprint(Blueprint):
    """Wrapper class for Blueprints with nested elements"""

    def __init__(self, *args, **kwargs):
        super(RootBlueprint, self).__init__(*args, **kwargs)
        self.nested_blueprints = []

    def register_nested_blueprint(self, nested_blueprint):
        """Add a 'sub' blueprint to root element
        Args:
            nested_blueprint (NestedBlueprint): Blueprint for sub routes
        """
        self.nested_blueprints.append(nested_blueprint)


class NestedBlueprint:
    """Default Blueprint class but with parent prefix route
    """

    def __init__(self, blueprint, url_prefix):
        self.blueprint = blueprint
        self.prefix = '/' + url_prefix
        super(NestedBlueprint, self).__init__()

    def route(self, rule, **options):
        rule = self.prefix + rule
        return self.blueprint.route(rule, **options)


def make_response(instance, status_code=200, indent=2):
    """
    make json http response with indent settings and auto encoding
    Args:
        instance: instance of a cmdbDao instance or instance of the subclass
        status_code: optional status code
        indent: indent of json response
    Returns:
        http valid response
    """
    from flask import make_response as flask_response

    # encode the dict data from the object to json data
    resp = flask_response(json.dumps(instance, default=json_encoding.default, indent=indent), status_code)
    # add header information
    resp.mimetype = DEFAULT_MIME_TYPE
    return resp


def login_required(f):
    """wraps function for routes which requires an authentication
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        """checks if user is logged in and valid
        """
        try:
            token = parse_authorization_header(request.headers['Authorization'])
        except Exception as err:
            return abort(401)
        if token:
            return f(*args, **kwargs)
        else:
            return abort(401)

    return decorated


def insert_request_user(func):
    """helper function which auto injects the user from the token request
    requires: login_required
    """

    @functools.wraps(func)
    def get_request_user(*args, **kwargs):
        from flask import request, current_app
        with current_app.app_context():
            user_manager = current_app.user_manager

        token = parse_authorization_header(request.headers['Authorization'])
        try:
            decrypted_token = TokenValidator().decode_token(token)
        except ValidationError as err:
            return abort(401)
        try:
            user_id = decrypted_token['DATAGERRY']['value']['user']['public_id']
        except ValueError:
            return abort(401)
        user = user_manager.get_user(user_id)
        kwargs.update({'request_user': user})
        return func(*args, **kwargs)

    return get_request_user


def right_required(required_right: str, excepted: dict = None):
    """wraps function for routes which requires a special user right
    requires: insert_request_user
    """

    with current_app.app_context():
        user_manager: UserManager = current_app.user_manager

    def _page_right(func):
        @functools.wraps(func)
        def _decorate(*args, **kwargs):
            try:
                current_user: User = kwargs['request_user']
            except KeyError:
                return abort(400, 'No request user was provided')

            if excepted:
                for exe_key, exe_value in excepted.items():

                    LOGGER.debug(f'Excepted parameter: {exe_key} | {exe_value}')
                    # Check if parameter exits
                    try:
                        route_parameter = kwargs[exe_value]
                        LOGGER.debug(f'Parameter exits {route_parameter}')
                    except KeyError:
                        continue
                    # Check if user attr exists
                    if not hasattr(current_user, exe_key):
                        continue

                    # Check if parameter test passed
                    if current_user.__dict__.get(exe_key) == route_parameter:
                        LOGGER.debug(f'Exception parameter passed test at {exe_key} | {exe_value}!')
                        return func(*args, **kwargs)

            try:
                has_right = user_manager.group_has_right(current_user.get_group(), required_right)
            except UserManagerGetError:
                return abort(404, 'Group or right not exists')
            if not has_right:
                return abort(403, 'Request user does not have the right for this action')
            return func(*args, **kwargs)

        return _decorate

    return _page_right


def parse_authorization_header(header):
    """
    Parses the HTTP Auth Header to a JWT Token
    Args:
        header: Authorization header of the HTTP Request
    Examples:
        request.headers['Authorization'] or something same
    Returns:
        Valid JWT token
    """
    if not header:
        return None
    value = wsgi_to_bytes(header)
    try:
        auth_type, auth_info = value.split(None, 1)
        auth_type = auth_type.lower()
    except ValueError:
        # Fallback for old versions
        auth_type = b"bearer"
        auth_info = value

    if auth_type == b"basic":
        try:
            username, password = base64.b64decode(auth_info).split(b":", 1)

            with current_app.app_context():
                username = to_unicode(username, "utf-8")
                password = to_unicode(password, "utf-8")

                user_manager: UserManager = current_app.user_manager
                auth_module = AuthModule(SystemSettingsReader(current_app.database_manager))

                try:
                    user_instance = auth_module.login(user_manager, username, password)
                except Exception as e:
                    return None
                if user_instance:
                    tg = TokenGenerator(current_app.database_manager)
                    return tg.generate_token(payload={'user': {
                        'public_id': user_instance.get_public_id()
                    }})
                else:
                    return None
        except Exception:
            return None

    if auth_type == b"bearer":
        try:
            tv = TokenValidator()
            decoded_token = tv.decode_token(auth_info)
            tv.validate_token(decoded_token)
            return auth_info
        except Exception:
            return None
    return None
