"""Core data models for AWS Orchestrator using Pydantic V2.

This module defines the foundational data structures for agents, tasks,
and orchestration configuration with strict type validation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class AgentType(str, Enum):
    """Supported agent types in the orchestration system."""

    BEDROCK = "bedrock"
    ANALYTICS = "analytics"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


class AgentStatus(str, Enum):
    """Agent execution status."""

    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class GuardrailType(str, Enum):
    """Types of compliance guardrails."""

    DATA_VALIDATION = "data_validation"
    ACCESS_CONTROL = "access_control"
    LOGGING_MONITORING = "logging_monitoring"
    PRIVACY_COMPLIANCE = "privacy_compliance"


class Agent(BaseModel):
    """Agent configuration and metadata.

    Attributes:
        id: Unique agent identifier
        name: Human-readable agent name
        agent_type: Type of agent (bedrock, analytics, etc.)
        description: Agent purpose and capabilities
        endpoint: AWS Lambda ARN or API endpoint
        timeout: Maximum execution time in seconds
        retry_attempts: Number of retry attempts on failure
        enabled: Whether the agent is active
        metadata: Additional agent-specific configuration
    """

    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=100)
    agent_type: AgentType
    description: str = Field(default="")
    endpoint: str = Field(..., min_length=1)
    timeout: int = Field(default=30, ge=1, le=900)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    enabled: bool = Field(default=True)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Validate endpoint is a valid ARN or URL."""
        if not (v.startswith("arn:aws:lambda:") or v.startswith("http")):
            raise ValueError("Endpoint must be a Lambda ARN or HTTP(S) URL")
        return v

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        json_schema_extra = {
            "example": {
                "name": "BedrockAgent",
                "agent_type": "bedrock",
                "description": "AI agent powered by AWS Bedrock",
                "endpoint": "arn:aws:lambda:us-east-1:123456789:function:bedrock-agent",
                "timeout": 60,
                "retry_attempts": 3,
            }
        }


class TaskRequest(BaseModel):
    """Incoming task request to the orchestrator.

    Attributes:
        task_id: Unique task identifier
        user_id: User making the request
        query: User's query or command
        context: Additional context data
        preferred_agent: Optional specific agent to use
        timestamp: Request creation time
    """

    task_id: UUID = Field(default_factory=uuid4)
    user_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1, max_length=10000)
    context: Dict[str, Any] = Field(default_factory=dict)
    preferred_agent: Optional[AgentType] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "query": "Analyze customer sentiment from last quarter",
                "context": {"source": "web-app", "region": "us-east-1"},
            }
        }


class TaskResponse(BaseModel):
    """Response from agent task execution.

    Attributes:
        task_id: Associated task identifier
        agent_id: Agent that processed the task
        agent_name: Name of the agent
        status: Execution status
        result: Task result data
        error: Error message if failed
        execution_time: Time taken in seconds
        timestamp: Response creation time
    """

    task_id: UUID
    agent_id: UUID
    agent_name: str
    status: AgentStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: float = Field(ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class GuardrailConfig(BaseModel):
    """Configuration for compliance guardrails.

    Attributes:
        enabled: Whether guardrails are active
        types: List of guardrail types to enforce
        pii_detection: Enable PII detection and masking
        encryption_at_rest: Require encryption at rest
        audit_logging: Enable comprehensive audit logging
        iam_policies: IAM policy ARNs to enforce
    """

    enabled: bool = Field(default=True)
    types: List[GuardrailType] = Field(default_factory=list)
    pii_detection: bool = Field(default=True)
    encryption_at_rest: bool = Field(default=True)
    audit_logging: bool = Field(default=True)
    iam_policies: List[str] = Field(default_factory=list)


class OrchestratorConfig(BaseModel):
    """Main orchestrator configuration.

    Attributes:
        name: Orchestrator instance name
        region: AWS region
        agents: Registered agents
        guardrails: Guardrail configuration
        max_concurrent_tasks: Maximum parallel tasks
        default_timeout: Default task timeout
        enable_caching: Enable response caching
        log_level: Logging level
    """

    name: str = Field(default="default-orchestrator")
    region: str = Field(default="us-east-1")
    agents: List[Agent] = Field(default_factory=list)
    guardrails: GuardrailConfig = Field(default_factory=GuardrailConfig)
    max_concurrent_tasks: int = Field(default=10, ge=1, le=100)
    default_timeout: int = Field(default=30, ge=1, le=900)
    enable_caching: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    @field_validator("region")
    @classmethod
    def validate_region(cls, v: str) -> str:
        """Validate AWS region format."""
        valid_regions = [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
        ]
        if v not in valid_regions:
            raise ValueError(f"Region must be one of {valid_regions}")
        return v


class HealthCheck(BaseModel):
    """System health check response.

    Attributes:
        status: Overall system status
        timestamp: Check timestamp
        agents_active: Number of active agents
        agents_total: Total number of agents
        uptime_seconds: System uptime
    """

    status: str = Field(default="healthy")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agents_active: int = Field(ge=0)
    agents_total: int = Field(ge=0)
    uptime_seconds: float = Field(ge=0)
