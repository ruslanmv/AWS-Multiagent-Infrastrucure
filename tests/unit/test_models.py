"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from aws_orchestrator.core.models import Agent, AgentType, OrchestratorConfig, TaskRequest


class TestAgent:
    """Test Agent model validation."""

    def test_agent_creation_valid(self) -> None:
        """Test creating a valid agent."""
        agent = Agent(
            name="TestAgent",
            agent_type=AgentType.BEDROCK,
            endpoint="arn:aws:lambda:us-east-1:123456789:function:test",
            timeout=30,
        )

        assert agent.name == "TestAgent"
        assert agent.agent_type == AgentType.BEDROCK
        assert agent.timeout == 30
        assert agent.enabled is True

    def test_agent_invalid_endpoint(self) -> None:
        """Test agent creation with invalid endpoint."""
        with pytest.raises(ValidationError):
            Agent(
                name="TestAgent",
                agent_type=AgentType.BEDROCK,
                endpoint="invalid-endpoint",
            )

    def test_agent_timeout_bounds(self) -> None:
        """Test agent timeout validation."""
        with pytest.raises(ValidationError):
            Agent(
                name="TestAgent",
                agent_type=AgentType.BEDROCK,
                endpoint="arn:aws:lambda:us-east-1:123456789:function:test",
                timeout=0,  # Invalid: must be >= 1
            )

        with pytest.raises(ValidationError):
            Agent(
                name="TestAgent",
                agent_type=AgentType.BEDROCK,
                endpoint="arn:aws:lambda:us-east-1:123456789:function:test",
                timeout=1000,  # Invalid: must be <= 900
            )


class TestTaskRequest:
    """Test TaskRequest model."""

    def test_task_request_creation(self) -> None:
        """Test creating a valid task request."""
        request = TaskRequest(
            user_id="user-123",
            query="Test query",
        )

        assert request.user_id == "user-123"
        assert request.query == "Test query"
        assert request.task_id is not None
        assert request.timestamp is not None

    def test_task_request_with_context(self) -> None:
        """Test task request with additional context."""
        request = TaskRequest(
            user_id="user-123",
            query="Test query",
            context={"source": "api", "version": "1.0"},
            preferred_agent=AgentType.ANALYTICS,
        )

        assert request.context["source"] == "api"
        assert request.preferred_agent == AgentType.ANALYTICS


class TestOrchestratorConfig:
    """Test OrchestratorConfig model."""

    def test_config_creation(self) -> None:
        """Test creating orchestrator configuration."""
        config = OrchestratorConfig(
            name="test-orchestrator",
            region="us-east-1",
        )

        assert config.name == "test-orchestrator"
        assert config.region == "us-east-1"
        assert config.max_concurrent_tasks == 10

    def test_config_invalid_region(self) -> None:
        """Test configuration with invalid region."""
        with pytest.raises(ValidationError):
            OrchestratorConfig(
                name="test-orchestrator",
                region="invalid-region",
            )

    def test_config_with_agents(self) -> None:
        """Test configuration with agents."""
        agent = Agent(
            name="TestAgent",
            agent_type=AgentType.BEDROCK,
            endpoint="arn:aws:lambda:us-east-1:123456789:function:test",
        )

        config = OrchestratorConfig(
            name="test-orchestrator",
            region="us-east-1",
            agents=[agent],
        )

        assert len(config.agents) == 1
        assert config.agents[0].name == "TestAgent"
