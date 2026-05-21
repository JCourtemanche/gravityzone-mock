"""
TODO: Rename this file to match your API endpoint (e.g. events.py, alerts.py).

Shows the minimal pattern for a route:
  1. Register a Blueprint
  2. Apply the auth decorator
  3. Parse query params
  4. Return generated data

Replace the URL rule and generator calls with your real API structure.
"""
import random
from flask import Blueprint, jsonify, request

# TODO: import the auth decorator that matches your scheme
from auth import require_api_key          # header-based (Cato, SentinelOne)
# from auth import require_basic_auth     # HTTP Basic Auth (ProofPoint)

from generators.example import generate_example_records

# TODO: rename the blueprint and url_prefix
example_bp = Blueprint('example', __name__, url_prefix='/api/v1')


# TODO: replace path and HTTP method with your real endpoint
@example_bp.route('/records', methods=['GET'])
@require_api_key
def get_records():
    # TODO: parse query params relevant to your API
    count = int(request.args.get('limit', 10))
    count = min(max(count, 1), 100)

    records = generate_example_records(count)

    # TODO: wrap in the response envelope your API uses
    return jsonify({
        'data': records,
        'total': len(records),
    }), 200
