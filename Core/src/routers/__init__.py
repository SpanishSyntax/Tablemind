from .job import router as router_job
from .media import router as router_media
from .model import router as router_model
from .prompt import router as router_prompt

__all__ = [
    "router_job",
    "router_media",
    "router_model",
    "router_prompt"
]
