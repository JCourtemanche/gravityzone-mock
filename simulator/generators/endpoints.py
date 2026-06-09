import random
from .base import generate_guid, USERS

_ENDPOINTS = None

_OS_MAP = {
    'Windows 10 Pro': 'Windows 10 Pro',
    'Windows 11 Pro': 'Windows 11 Pro',
    'macOS 13 Ventura': 'macOS 13.6 Ventura',
    'macOS 14 Sonoma': 'macOS 14.2 Sonoma',
    'iOS 17': 'iOS 17.0',
    'Ubuntu 22.04': 'Ubuntu 22.04.3 LTS',
}

_MACHINE_TYPES = {
    'Windows 10 Pro': 1, 'Windows 11 Pro': 1,
    'macOS 13 Ventura': 1, 'macOS 14 Sonoma': 1,
    'iOS 17': 1, 'Ubuntu 22.04': 1,
}


def _make_endpoint(user, idx):
    os_name = user.get('os_name', 'Windows 10 Pro')
    hostname = user['hostname']
    group_id = generate_guid()
    product_version = random.choice(['7.9.10.1234', '7.8.5.1109', '7.9.8.1200'])

    # Documented fields for getEndpointsList (per official API spec)
    endpoint = {
        'id': generate_guid(),
        'name': hostname,
        'label': '',
        'fqdn': f"{hostname}.businesscorp.local",
        'groupId': group_id,
        'isManaged': True,
        'operatingSystem': _OS_MAP.get(os_name, os_name),
        'ip': user['internal_ip'],
        'macs': [f"AA:BB:{(idx * 17 + 33) % 256:02X}:{(idx * 31 + 11) % 256:02X}:{(idx * 7 + 55) % 256:02X}:{(idx * 13 + 77) % 256:02X}"],
        'ssid': '',
        'productOutdated': idx % 8 == 0,
        'lastSuccessfulScan': {
            'name': 'System scan',
            'date': f'2026-06-0{max(1, 9 - idx)}T06:00:00+00:00',
        },
        # Internal fields (not returned in getEndpointsList, used for getManagedEndpointDetails)
        '_state': 1 if idx % 5 != 0 else 2,
        '_groupId': group_id,
        '_groupName': 'Managed Endpoints',
        '_productVersion': product_version,
        '_machineType': _MACHINE_TYPES.get(os_name, 1),
        '_lastSeen': f'2026-06-09T{10 + idx % 12:02d}:00:00',  # no TZ offset (per API spec)
        '_agent_lastUpdate': f'2026-06-09T{8 + idx % 4:02d}:30:00',  # no TZ offset
        '_productOutdated': idx % 8 == 0,
        '_productVersion': product_version,
        '_companyId': 'gz-company-001',
    }
    return endpoint


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
