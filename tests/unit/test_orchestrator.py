"""Unit tests for Orchestrator."""

import pytest

from aws_orchestrator.core.models import Agent, AgentType, OrchestratorConfig, TaskRequest
from aws_orchestrator.core.orchestrator import Orchestrator


class TestOrchestrator:
    """Test Orchestrator functionality."""

    @pytest.fixture
    def sample_agent(self) -> Agent:
        """Create a sample agent for testing."""
        return Agent(
            name="TestAgent",
            agent_type=AgentType.BEDROCK,
            endpoint="arn:aws:lambda:us-east-1:123456789:function:test",
            timeout=30,
        )

    @pytest.fixture
    def orchestrator(self, sample_agent: Agent) -> Orchestrator:
        """Create an orchestrator instance for testing."""
        config = OrchestratorConfig(
            name="test-orchestrator",
            region="us-east-1",
            agents=[sample_agent],
        )
        return Orchestrator(config)

    def test_orchestrator_initialization(self, orchestrator: Orchestrator) -> None:
        """Test orchestrator initialization."""
        assert orchestrator.config.name == "test-orchestrator"
        assert len(orchestrator.agents) == 1

    def test_register_agent(self, orchestrator: Orchestrator) -> None:
        """Test agent registration."""
        new_agent = Agent(
            name="NewAgent",
            agent_type=AgentType.ANALYTICS,
            endpoint="arn:aws:lambda:us-east-1:123456789:function:new",
        )

        initial_count = len(orchestrator.agents)
        orchestrator.register_agent(new_agent)

        assert len(orchestrator.agents) == initial_count + 1
        assert new_agent.id in orchestrator.agents

    def test_unregister_agent(self, orchestrator: Orchestrator, sample_agent: Agent) -> None:
        """Test agent unregistration."""
        orchestrator.unregister_agent(sample_agent.id)
        assert sample_agent.id not in orchestrator.agents

    def test_get_agent_by_type(self, orchestrator: Orchestrator) -> None:
        """Test finding agent by type."""
        agent = orchestrator.get_agent_by_type(AgentType.BEDROCK)
        assert agent is not None
        assert agent.agent_type == AgentType.BEDROCK

        agent = orchestrator.get_agent_by_type(AgentType.ANALYTICS)
        assert agent is None

    def test_select_agent(self, orchestrator: Orchestrator) -> None:
        """Test agent selection."""
        request = TaskRequest(
            user_id="test-user",
            query="Test query",
        )

        agent = orchestrator.select_agent(request)
        assert agent is not None

    def test_select_agent_with_preference(self, orchestrator: Orchestrator) -> None:
        """Test agent selection with preferred type."""
        request = TaskRequest(
            user_id="test-user",
            query="Test query",
            preferred_agent=AgentType.BEDROCK,
        )

        agent = orchestrator.select_agent(request)
        assert agent is not None
        assert agent.agent_type == AgentType.BEDROCK

    @pytest.mark.asyncio
    async def test_process_task(self, orchestrator: Orchestrator) -> None:
        """Test task processing."""
        request = TaskRequest(
            user_id="test-user",
            query="Test query",
        )

        response = await orchestrator.process_task(request)

        assert response.task_id == request.task_id
        assert response.status in ["success", "failed", "timeout"]

    def test_health_check(self, orchestrator: Orchestrator) -> None:
        """Test health check."""
        health = orchestrator.health_check()

        assert health.status in ["healthy", "degraded"]
        assert health.agents_total == 1
        assert health.agents_active >= 0
