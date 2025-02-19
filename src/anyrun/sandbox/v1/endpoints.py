"""Sandbox API v1 endpoints."""

# Analysis endpoints
ANALYSIS_CREATE = "/v1/analysis"
ANALYSIS_GET = "/v1/analysis/{task_id}"
ANALYSIS_LIST = "/v1/analysis"
ANALYSIS_MONITOR = "/v1/analysis/monitor/{task_id}"
ANALYSIS_ADD_TIME = "/v1/analysis/addtime/{task_id}"
ANALYSIS_STOP = "/v1/analysis/stop/{task_id}"
ANALYSIS_DELETE = "/v1/analysis/delete/{task_id}"

# Environment endpoints
ENVIRONMENT_INFO = "/v1/environment"

# User endpoints
USER_INFO = "/v1/user"
USER_PRESETS = "/v1/user/presets"
