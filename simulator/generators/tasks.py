import time
import uuid

_TASKS = {}      # taskId -> task dict
_ACTIVITIES = {}  # activityId -> activity dict

# GravityZone task type ints
TASK_TYPE_ISOLATE = 16
TASK_TYPE_DEISOLATE = 17
TASK_TYPE_KILL_PROCESS = 21
TASK_TYPE_UPLOAD = 24

_TASK_TYPE_MAP = {
    'isolate': TASK_TYPE_ISOLATE,
    'deisolate': TASK_TYPE_DEISOLATE,
    'kill_process': TASK_TYPE_KILL_PROCESS,
    'upload': TASK_TYPE_UPLOAD,
}

# GravityZone task status ints: 1=pending, 2=processing, 3=processed
_AUTO_COMPLETE_SECONDS = 3


def create_task(task_type_key, endpoint_id, endpoint_name):
    task_id = str(uuid.uuid4())
    _TASKS[task_id] = {
        'taskId': task_id,
        'status': 2,
        'type': _TASK_TYPE_MAP.get(task_type_key, TASK_TYPE_ISOLATE),
        'subtasks': [
            {
                'endpointId': endpoint_id,
                'endpointName': endpoint_name,
                'status': 2,
                'startDate': '2026-06-09T12:00:00+00:00',
                'endDate': None,
                'errorCode': '0',
                'errorMessage': 'Success',
            }
        ],
        '_created_at': time.time(),
    }
    return task_id


def get_task_status(task_id):
    task = _TASKS.get(task_id)
    if not task:
        return None
    if time.time() - task['_created_at'] > _AUTO_COMPLETE_SECONDS:
        task['status'] = 3
        for sub in task['subtasks']:
            sub['status'] = 3
            sub['endDate'] = '2026-06-09T12:00:05+00:00'
    return task


def create_activity(activity_type, endpoint_id):
    """Create an async investigation activity (download=1, run_command=2)."""
    activity_id = str(uuid.uuid4())
    file_id = str(uuid.uuid4()).replace('-', '')
    _ACTIVITIES[activity_id] = {
        'activityId': activity_id,
        'type': activity_type,
        'status': 'in_progress',
        'bucket': 'investigationFiles',
        'fileId': file_id,
        'endpointId': endpoint_id,
        '_created_at': time.time(),
    }
    return activity_id


def get_activity(activity_id):
    activity = _ACTIVITIES.get(activity_id)
    if not activity:
        return None
    if time.time() - activity['_created_at'] > _AUTO_COMPLETE_SECONDS:
        activity['status'] = 'success'
    return activity
