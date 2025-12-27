"""Pytest configuration and shared fixtures.

This module provides common fixtures and configuration for all tests.
"""

import pytest

from aws_orchestrator.core.models import (
    Agent,
    AgentType,
    GuardrailConfig,
    OrchestratorConfig,
)


@pytest.fixture
def sample_bedrock_agent() -> Agent:
    """Create a sample Bedrock agent for testing.

    Returns:
        Sample Bedrock agent configuration
    """
    return Agent(
        name="TestBedrockAgent",
        agent_type=AgentType.BEDROCK,
        description="Test Bedrock agent",
        endpoint="arn:aws:lambda:us-east-1:123456789:function:test-bedrock",
        timeout=30,
        retry_attempts=3,
        metadata={"model_id": "anthropic.claude-v2"},
    )


@pytest.fixture
def sample_analytics_agent() -> Agent:
    """Create a sample Analytics agent for testing.

    Returns:
        Sample Analytics agent configuration
    """
    return Agent(
        name="TestAnalyticsAgent",
        agent_type=AgentType.ANALYTICS,
        description="Test Analytics agent",
        endpoint="arn:aws:lambda:us-east-1:123456789:function:test-analytics",
        timeout=45,
    )


@pytest.fixture
def sample_orchestrator_config(
    sample_bedrock_agent: Agent, sample_analytics_agent: Agent
) -> OrchestratorConfig:
    """Create a sample orchestrator configuration for testing.

    Args:
        sample_bedrock_agent: Bedrock agent fixture
        sample_analytics_agent: Analytics agent fixture

    Returns:
        Sample orchestrator configuration
    """
    return OrchestratorConfig(
        name="test-orchestrator",
        region="us-east-1",
        agents=[sample_bedrock_agent, sample_analytics_agent],
        guardrails=GuardrailConfig(
            enabled=True,
            pii_detection=True,
            audit_logging=True,
        ),
        max_concurrent_tasks=10,
    )


@pytest.fixture
def sample_guardrail_config() -> GuardrailConfig:
    """Create a sample guardrail configuration for testing.

    Returns:
        Sample guardrail configuration
    """
    return GuardrailConfig(
        enabled=True,
        pii_detection=True,
        encryption_at_rest=True,
        audit_logging=True,
    )


# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)
