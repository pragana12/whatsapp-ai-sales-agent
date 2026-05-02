import json
from pathlib import Path
from typing import Protocol, cast

from src.core.models import AgentConfig


class AgentConfigRepository(Protocol):
    def get_config(self) -> AgentConfig:
        """Return the agent configuration."""


class FileAgentConfigRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def get_config(self) -> AgentConfig:
        with self._path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return cast(AgentConfig, data)
