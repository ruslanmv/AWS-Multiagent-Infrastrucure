"""AWS Orchestrator - Multi-Agent Orchestration Framework for AWS.

A production-ready framework for deploying and managing multi-agent systems
on AWS with built-in compliance guardrails.

Author: Ruslan Magana (ruslanmv.com)
License: Apache 2.0
"""

__version__ = "0.1.0"
__author__ = "Ruslan Magana"
__email__ = "contact@ruslanmv.com"

from aws_orchestrator.core.orchestrator import Orchestrator
from aws_orchestrator.core.models import (
    Agent,
    AgentType,
    OrchestratorConfig,
    TaskRequest,
    TaskResponse,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "Orchestrator",
    "Agent",
    "AgentType",
    "OrchestratorConfig",
    "TaskRequest",
    "TaskResponse",
]
