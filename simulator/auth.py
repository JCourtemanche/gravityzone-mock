"""
Authentication helpers.

Keep only the decorator that matches your integration's auth scheme,
delete the other one.
"""
from functools import wraps
from flask import request, jsonify
from config import Config


# ---------------------------------------------------------------------------
# Option A — API key in a custom header (x-api-key, x-auth-token, …)
# ---------------------------------------------------------------------------
def require_api_key(f):
    """Validate a header-based API key. Adjust the header name as needed."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != Config.AUTH_API_KEY:
            return jsonify({'errors': [{'message': 'Invalid API key'}]}), 403
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Option B — HTTP Basic Auth
# ---------------------------------------------------------------------------
def require_basic_auth(f):
    """Validate HTTP Basic Auth credentials."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != Config.AUTH_USERNAME or auth.password != Config.AUTH_PASSWORD:
            return jsonify({'error': 'Authentication required'}), 401, {
                'WWW-Authenticate': 'Basic realm="Simulator"'
            }
        return f(*args, **kwargs)
    return decorated
