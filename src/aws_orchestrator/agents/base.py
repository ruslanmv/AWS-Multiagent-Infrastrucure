"""Base agent interface for all agent implementations.

This module defines the abstract base class that all agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from aws_orchestrator.core.models import Agent, TaskRequest


class BaseAgent(ABC):
    """Abstract base class for all agents.

    All agent implementations must inherit from this class and implement
    the execute method.

    Attributes:
        config: Agent configuration
    """

    def __init__(self, config: Agent) -> None:
        """Initialize the agent.

        Args:
            config: Agent configuration
        """
        self.config = config

    @abstractmethod
    async def execute(self, request: TaskRequest) -> Dict[str, Any]:
        """Execute a task.

        Args:
            request: Task request to process

        Returns:
            Task execution result

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement execute method")

    def validate_config(self) -> bool:
        """Validate agent configuration.

        Returns:
            True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.config.endpoint:
            raise ValueError("Agent endpoint must be configured")
        if self.config.timeout <= 0:
            raise ValueError("Agent timeout must be positive")
        return True
