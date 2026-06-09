import random
from .base import generate_guid, USERS

_ENDPOINTS = None


def _make_endpoint(user, idx):
    return {
        'id': generate_guid(),
        'name': user['hostname'],
        'ip': user['internal_ip'],
        'macs': [f"AA:BB:{(idx * 17 + 33) % 256:02X}:{(idx * 31 + 11) % 256:02X}:{(idx * 7 + 55) % 256:02X}:{(idx * 13 + 77) % 256:02X}"],
        'operatingSystemVersion': user['os_name'],
        'state': 1 if idx % 5 != 0 else 2,  # 80% online, 20% offline
        'fqdn': f"{user['hostname']}.businesscorp.local",
        'companyId': 'gz-company-001',
        'isManaged': True,
        'productVersion': '7.9.10.1234',
        'managedByMSP': False,
        'lastSeen': '2026-06-09T12:00:00+00:00',
    }


def get_endpoints():
    global _ENDPOINTS
    if _ENDPOINTS is None:
        sample = random.sample(USERS, min(8, len(USERS)))
        _ENDPOINTS = [_make_endpoint(u, i) for i, u in enumerate(sample)]
    return _ENDPOINTS


def get_endpoint_by_id(endpoint_id):
    for ep in get_endpoints():
        if ep['id'] == endpoint_id:
            return ep
    return None
