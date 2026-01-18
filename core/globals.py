# Simple in-memory cache for task progress
# Format: { 'task_id': { 'status': 'processing', 'percent': 0, 'eta': '...', 'msg': '...' } }
PROGRESS_CACHE = {}
