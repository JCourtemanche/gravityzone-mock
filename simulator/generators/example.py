"""
TODO: Rename this file to match your data type (e.g. events.py, alerts.py).

This is a minimal example showing how to build a generator that uses
the shared Business Corp personas. Replace the example fields with the
actual fields required by your API.
"""
import random
from .base import generate_guid, generate_iso8601_date, random_user, random_malicious_ip


def generate_example_record():
    """
    TODO: Replace with your actual record structure.

    Each field below shows the pattern:
      - persona fields  → come from random_user()
      - threat fields   → come from shared lists (random_malicious_ip(), etc.)
      - identity fields → use generate_guid(), generate_iso8601_date(), etc.
    """
    user = random_user()

    return {
        # Identity
        'id': generate_guid(),
        'timestamp': generate_iso8601_date(),

        # Persona fields — always from shared data
        'userName': user['name'],
        'userEmail': user['email'],
        'srcIp': user['internal_ip'],
        'hostname': user['hostname'],
        'os': user['os_name'],

        # TODO: add threat / event-specific fields
        'destIp': random_malicious_ip(),
        'action': random.choice(['block', 'allow', 'detect']),
    }


def generate_example_records(count=10):
    return [generate_example_record() for _ in range(count)]
