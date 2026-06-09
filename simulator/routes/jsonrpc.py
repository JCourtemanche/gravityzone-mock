"""
JSON-RPC 2.0 dispatcher for all GravityZone API services.

All API calls use POST /api/<version>/jsonrpc/<service> with body:
  {"jsonrpc": "2.0", "method": "<method>", "params": {...}, "id": 1}

The service path and version are ignored for routing — only the "method"
field determines which handler runs.
"""
import random
from flask import Blueprint, request, jsonify
from auth import require_basic_auth
from generators.endpoints import get_endpoints, get_endpoint_by_id
from generators.incidents import get_incidents, get_incident_by_id, update_incident_status, add_incident_note
from generators.tasks import create_task, get_task_status, create_activity, get_activity
from generators.base import generate_guid, generate_sha256

jsonrpc_bp = Blueprint('jsonrpc', __name__)


def _ok(result, req_id=1):
    return jsonify({'jsonrpc': '2.0', 'result': result, 'id': req_id})


def _err(code, message, req_id=1):
    return jsonify({'jsonrpc': '2.0', 'error': {'code': code, 'message': message, 'data': {}}, 'id': req_id}), 400


def _strip_internal(d):
    """Remove keys that start with '_' (internal mock fields)."""
    return {k: v for k, v in d.items() if not k.startswith('_')}


# ---------------------------------------------------------------------------
# companies service
# ---------------------------------------------------------------------------

def handle_get_company_details(params):
    return {
        'id': 'gz-company-001',
        'name': 'Business Corp',
        'companyType': 'company',
        'address': '1 Security Blvd, San Francisco, CA 94105',
        'phone': '+1-555-0100',
        'suspended': False,
        'licenseDetails': {
            'count': 500,
            'used': 48,
            'type': 'business',
            'expiryDate': '2027-12-31',
        },
    }


# ---------------------------------------------------------------------------
# network service
# ---------------------------------------------------------------------------

def handle_get_endpoints_list(params):
    endpoints = get_endpoints()
    page = max(1, int(params.get('page', 1)))
    # Official API: default 30, max 100
    per_page = min(100, max(1, int(params.get('perPage', 30))))

    start = (page - 1) * per_page
    items = endpoints[start:start + per_page]

    # Official getEndpointsList fields (per bitdefender.com/business/support/en/77212-128483)
    public_fields = {
        'id', 'name', 'label', 'fqdn', 'groupId', 'isManaged',
        'operatingSystem', 'ip', 'macs', 'ssid', 'productOutdated', 'lastSuccessfulScan',
    }
    return {
        'items': [{k: v for k, v in ep.items() if k in public_fields} for ep in items],
        'total': len(endpoints),
        'page': page,
        'perPage': per_page,
        'pagesCount': max(1, (len(endpoints) + per_page - 1) // per_page),
    }


def handle_get_managed_endpoint_details(params):
    endpoint_id = params.get('endpointId', '')
    ep = get_endpoint_by_id(endpoint_id) or get_endpoints()[0]
    options = params.get('options', {})

    product_version = ep.get('_productVersion', '7.9.10.1234')
    # Official spec: lastSeen and agent.lastUpdate have NO timezone offset
    result = {
        'id': ep['id'],
        'name': ep['name'],
        'label': ep.get('label', ''),
        'companyId': ep.get('_companyId', 'gz-company-001'),
        'operatingSystem': ep.get('operatingSystem', ep['name']),
        'state': ep.get('_state', 1),
        'ip': ep['ip'],
        'macs': ep['macs'],
        'lastSeen': ep.get('_lastSeen', '2026-06-09T12:00:00'),  # no TZ offset
        'machineType': ep.get('_machineType', 1),
        'group': {
            'id': ep.get('_groupId', ep.get('groupId', '')),
            'name': ep.get('_groupName', 'Managed Endpoints'),
        },
        'agent': {
            'productVersion': product_version,
            'engineVersion': '7.93650',
            'primaryEngine': 3,    # 3=Local/Full
            'fallbackEngine': 2,   # 2=Hybrid/Light
            'lastUpdate': ep.get('_agent_lastUpdate', '2026-06-09T08:30:00'),  # no TZ offset
            'licensed': 1,         # 1=active
            'productOutdated': ep.get('_productOutdated', False),
            'productUpdateDisabled': False,
            'signatureOutdated': False,
            'signatureUpdateDisabled': False,
            'type': 1,             # 1=Endpoint Security
        },
        'malwareStatus': {
            'detection': False,
            'infected': False,
        },
        'policy': {
            'id': 'pol-default-001',
            'name': 'Default policy',
            'applied': True,
        },
        'modules': {
            'antimalware': True,
            'firewall': True,
            'contentControl': True,
            'deviceControl': False,
            'advancedThreatControl': True,
            'powerUser': False,
            'encryption': False,
            'edrSensor': True,      # correct field name per API spec
            'hyperDetect': True,
            'patchManagement': False,
            'relay': False,
            'sandboxAnalyzer': False,
            'exchange': False,
            'advancedAntiExploit': True,
            'containerProtection': False,
            'networkAttackDefense': True,
        },
    }
    if options.get('includeScanLogs'):
        result['scanLogs'] = [
            {
                'type': 2, 'status': 1,
                'startDate': '2026-06-09T06:00:00',
                'endDate': '2026-06-09T06:15:00',
                'threatsFound': 0,
            }
        ]
    if options.get('returnProductOutdated'):
        result['productOutdated'] = ep.get('_productOutdated', False)
    if options.get('includeLastLoggedUsers'):
        result['lastLoggedUsers'] = [
            {
                'userName': f"BUSINESSCORP\\{ep['name'].lower()}",
                'loginDate': '2026-06-09T08:00:00',  # no TZ offset
            }
        ]
    return result


def handle_get_task_status(params):
    task_id = params.get('taskId', '')
    task = get_task_status(task_id)
    if not task:
        return {'status': 3, 'type': 16, 'subtasks': []}
    return {
        'status': task['status'],
        'type': task['type'],
        'subtasks': task.get('subtasks', []),
    }


# ---------------------------------------------------------------------------
# incidents service (v1.0, v1.1, v1.2 all handled here)
# ---------------------------------------------------------------------------

def handle_get_incidents_list(params):
    incidents = get_incidents()
    page = max(1, int(params.get('page', 1)))
    per_page = min(500, max(1, int(params.get('perPage', 100))))

    start = (page - 1) * per_page
    page_items = incidents[start:start + per_page]

    items = [{k: v for k, v in inc.items() if k != 'statusInt'} for inc in page_items]
    return {
        'items': items,
        'total': len(incidents),
        'pagesCount': max(1, (len(incidents) + per_page - 1) // per_page),
        'page': page,
    }


def handle_get_incident(params):
    incident_id = params.get('id', '')
    inc = get_incident_by_id(incident_id) or get_incidents()[0]
    return {k: v for k, v in inc.items() if k != 'statusInt'}


def handle_update_incident_note(params):
    incident_id = params.get('incidentId', '')
    note = params.get('note', '')
    add_incident_note(incident_id, note)
    return True


def handle_change_incident_status(params):
    incident_id = params.get('incidentId', '')
    new_status = int(params.get('status', 1))
    update_incident_status(incident_id, new_status)
    return True


def handle_create_isolate_task(params):
    endpoint_id = params.get('endpointId', '')
    ep = get_endpoint_by_id(endpoint_id)
    name = ep['name'] if ep else 'UNKNOWN-HOST'
    return {'taskId': create_task('isolate', endpoint_id, name)}


def handle_create_restore_task(params):
    endpoint_id = params.get('endpointId', '')
    ep = get_endpoint_by_id(endpoint_id)
    name = ep['name'] if ep else 'UNKNOWN-HOST'
    return {'taskId': create_task('deisolate', endpoint_id, name)}


# ---------------------------------------------------------------------------
# investigation service
# ---------------------------------------------------------------------------

def handle_start_retrieve_file(params):
    endpoint_id = params.get('targetId', '')
    return {'activityId': create_activity(1, endpoint_id)}


def handle_start_command_execution(params):
    endpoint_id = params.get('targetId', '')
    return {'activityId': create_activity(2, endpoint_id)}


def handle_kill_process(params):
    endpoint_id = params.get('targetId', '')
    ep = get_endpoint_by_id(endpoint_id)
    name = ep['name'] if ep else 'UNKNOWN-HOST'
    return {'taskId': create_task('kill_process', endpoint_id, name)}


def handle_collect_investigation_package(params):
    endpoint_id = params.get('targetId', '')
    return {'activityId': create_activity(1, endpoint_id)}


def handle_get_investigation_file_url(params):
    activity_id = params.get('activityId', '')
    activity = get_activity(activity_id)
    if not activity:
        return {'status': 'failed', 'errorCode': '1', 'url': '', 'bucket': 'investigationFiles', 'fileId': ''}
    file_url = (
        f"http://localhost:8080/storage/{activity['bucket']}/{activity['fileId']}.zip"
        if activity['status'] == 'success' else ''
    )
    return {
        'status': activity['status'],
        'url': file_url,
        'bucket': activity['bucket'],
        'fileId': activity['fileId'],
        'errorCode': '0',
    }


# ---------------------------------------------------------------------------
# internal service (live search)
# ---------------------------------------------------------------------------

def handle_run_live_search(params):
    endpoints_list = params.get('endpoints', [])
    endpoint_id = endpoints_list[0] if endpoints_list else ''
    ep = get_endpoint_by_id(endpoint_id)
    name = ep['name'] if ep else 'UNKNOWN-HOST'
    return {'taskId': create_task('kill_process', endpoint_id, name)}


def handle_get_live_search_result(params):
    task_id = params.get('taskId', '')
    task = get_task_status(task_id)
    completed = task and task['status'] == 3

    items = []
    if completed:
        items = [
            {
                'processId': random.randint(1000, 65535),
                'processName': random.choice(['cmd.exe', 'powershell.exe', 'explorer.exe']),
                'processPath': 'C:\\Windows\\System32\\cmd.exe',
                'hash': generate_sha256(),
                'pid': random.randint(1000, 65535),
                'parentPid': random.randint(100, 999),
                'userName': 'BUSINESSCORP\\user',
                'startTime': '2026-06-09T08:00:00+00:00',
            }
            for _ in range(random.randint(1, 5))
        ]

    return {
        'status': 3 if completed else 2,
        'items': items,
        'total': len(items),
        'pagesCount': 1,
    }


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_HANDLERS = {
    'getCompanyDetails': handle_get_company_details,
    'getEndpointsList': handle_get_endpoints_list,
    'getManagedEndpointDetails': handle_get_managed_endpoint_details,
    'getTaskStatus': handle_get_task_status,
    'getIncidentsList': handle_get_incidents_list,
    'getIncident': handle_get_incident,
    'updateIncidentNote': handle_update_incident_note,
    'changeIncidentStatus': handle_change_incident_status,
    'createIsolateEndpointTask': handle_create_isolate_task,
    'createRestoreEndpointFromIsolationTask': handle_create_restore_task,
    'startRetrieveInvestigationFileFromEndpoint': handle_start_retrieve_file,
    'startCommandExecutionOnEndpoint': handle_start_command_execution,
    'killProcess': handle_kill_process,
    'collectInvestigationPackage': handle_collect_investigation_package,
    'getInvestigationFileUrl': handle_get_investigation_file_url,
    'runPredefinedLiveSearchQuery': handle_run_live_search,
    'getLiveSearchQueryTaskResult': handle_get_live_search_result,
}


@jsonrpc_bp.route('/api/<version>/jsonrpc/<service>', methods=['POST'])
@require_basic_auth
def jsonrpc_handler(version, service):
    body = request.get_json(force=True, silent=True) or {}
    method = body.get('method', '')
    params = body.get('params') or {}
    req_id = body.get('id', 1)

    handler = _HANDLERS.get(method)
    if not handler:
        return _err(-32601, f"Method not found: {method}", req_id)

    try:
        result = handler(params)
        return _ok(result, req_id)
    except Exception as exc:
        return _err(-32603, f"Internal error: {exc}", req_id)
