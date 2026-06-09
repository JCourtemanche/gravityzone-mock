from functools import wraps
from flask import request, jsonify


def require_basic_auth(f):
    """Validate HTTP Basic Auth.

    GravityZone encodes the API key as Basic auth (username=api_key, password="").
    The mock accepts any non-empty username without validating its value so that
    XSIAM can use whatever credentials are configured in the integration.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username:
            return jsonify({
                'jsonrpc': '2.0',
                'error': {'code': -32001, 'message': 'Authentication required'},
                'id': None,
            }), 401, {'WWW-Authenticate': 'Basic realm="GravityZone"'}
        return f(*args, **kwargs)
    return decorated
