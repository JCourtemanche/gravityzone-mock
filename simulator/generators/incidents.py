import random
from datetime import datetime, timedelta
from .base import generate_guid, generate_sha256, USERS, MALICIOUS_FILES
from .endpoints import get_endpoints

_INCIDENTS = None

_ATTACK_TYPES = [
    'Fileless attack', 'Ransomware', 'Trojan', 'Exploit',
    'Network attack', 'Phishing', 'Data exfiltration', 'Lateral movement',
    'Credential theft', 'Privilege escalation',
]

_STATUS_INT_MAP = {
    'open': 1, 'in_progress': 2, 'closed': 3, 'false_positive': 4,
}
_INT_STATUS_MAP = {v: k for k, v in _STATUS_INT_MAP.items()}

_PROCESSES = ['cmd.exe', 'powershell.exe', 'wscript.exe', 'mshta.exe', 'rundll32.exe', 'regsvr32.exe']


def _make_incident(endpoint, idx):
    hours_ago = random.randint(1, 720)
    created = datetime(2026, 6, 9, 12, 0, 0) - timedelta(hours=hours_ago)
    last_updated = created + timedelta(minutes=random.randint(1, 120))

    incident_type = 'extendedIncident' if idx % 5 == 0 else 'incident'
    status_str = random.choices(
        ['open', 'in_progress', 'closed', 'false_positive'],
        weights=[50, 25, 20, 5],
    )[0]

    severity = random.randint(0, 100)
    if severity >= 80:
        priority = 'high'
    elif severity >= 50:
        priority = 'medium'
    elif severity >= 20:
        priority = 'low'
    else:
        priority = 'unknown'

    mal_file = random.choice(MALICIOUS_FILES)
    analyst = random.choice(USERS)

    details = {
        'computerId': endpoint['id'],
        'computerName': endpoint['name'],
        'computerFqdn': endpoint.get('fqdn', f"{endpoint['name']}.businesscorp.local"),
        'computerIp': endpoint['ip'],
        'alerts': [
            {
                'alertId': generate_guid(),
                'type': random.choice(_ATTACK_TYPES),
                'severity': severity,
                'filePath': f"C:\\Windows\\Temp\\{mal_file['name']}",
                'fileHash': mal_file['hash'],
                'processName': random.choice(_PROCESSES),
                'detectedAt': created.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
            }
        ],
    }
    if incident_type == 'extendedIncident':
        details['affectedEndpoints'] = [
            {'computerId': endpoint['id'], 'computerName': endpoint['name']}
        ]

    return {
        'incidentId': generate_guid(),
        'incidentNumber': 5000 + idx,
        'incidentType': incident_type,
        'severityScore': severity,
        'status': status_str,
        'statusInt': _STATUS_INT_MAP[status_str],
        'mainAction': random.choices(
            ['blocked', 'reported', 'partially_blocked'],
            weights=[60, 25, 15],
        )[0],
        'priority': priority,
        'created': created.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        'lastUpdated': last_updated.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        'lastProcessed': last_updated.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
        'incidentLink': f"https://cloud.gravityzone.bitdefender.com/incidents/{generate_guid()}",
        'attackTypes': random.sample(_ATTACK_TYPES, random.randint(1, 3)),
        'company': {'id': 'gz-company-001', 'name': 'Business Corp'},
        'assignee': {
            'userId': generate_guid(),
            'userName': analyst['email'],
            'companyId': 'gz-company-001',
            'companyName': 'Business Corp',
        },
        'details': details,
        'notes': [],
    }


def get_incidents():
    global _INCIDENTS
    if _INCIDENTS is None:
        endpoints = get_endpoints()
        _INCIDENTS = [
            _make_incident(random.choice(endpoints), i)
            for i in range(25)
        ]
    return _INCIDENTS


def get_incident_by_id(incident_id):
    for inc in get_incidents():
        if inc['incidentId'] == incident_id:
            return inc
    return None


def update_incident_status(incident_id, status_int):
    incident = get_incident_by_id(incident_id)
    if incident:
        incident['status'] = _INT_STATUS_MAP.get(status_int, 'open')
        incident['statusInt'] = status_int
        return True
    return False


def add_incident_note(incident_id, note_text, username='analyst@businesscorp.local'):
    incident = get_incident_by_id(incident_id)
    if incident:
        incident['notes'].append({
            'text': note_text,
            'userName': username,
            'created': '2026-06-09T12:00:00+00:00',
        })
        return True
    return False
