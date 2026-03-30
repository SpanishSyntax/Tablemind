from shared_db import TableInfo
from shared_models.targets import CoreTargetTable


class TargetTable(CoreTargetTable):

    PROMPTS = TableInfo("prompts", "resources")
    MODELS = TableInfo("ai_models", "resources")
    API_KEYS = TableInfo("api_keys", "resources")

    JOBS = TableInfo("jobs", "jobs")
    CHUNKS = TableInfo("chunks", "jobs")
