"""Core orchestrator engine with async task management.

This module implements the main orchestration logic for managing multiple
agents, routing tasks, and enforcing compliance guardrails.
"""

import asyncio
import time
from typing import Dict, List, Optional
from uuid import UUID

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from aws_orchestrator.core.models import (
    Agent,
    AgentStatus,
    AgentType,
    HealthCheck,
    OrchestratorConfig,
    TaskRequest,
    TaskResponse,
)
from aws_orchestrator.guardrails.compliance import ComplianceEngine

logger = structlog.get_logger(__name__)


class Orchestrator:
    """Main orchestrator for multi-agent task execution.

    This class manages agent registration, task routing, and execution
    with built-in retry logic, timeout handling, and compliance enforcement.

    Attributes:
        config: Orchestrator configuration
        agents: Registered agents indexed by ID
        compliance: Compliance guardrail engine
        _start_time: Orchestrator start timestamp
        _task_queue: Async task queue
    """

    def __init__(self, config: OrchestratorConfig) -> None:
        """Initialize the orchestrator.

        Args:
            config: Orchestrator configuration
        """
        self.config = config
        self.agents: Dict[UUID, Agent] = {}
        self.compliance = ComplianceEngine(config.guardrails)
        self._start_time = time.time()
        self._task_queue: asyncio.Queue[TaskRequest] = asyncio.Queue(
            maxsize=config.max_concurrent_tasks
        )
        self._running = False

        # Register agents from config
        for agent in config.agents:
            self.register_agent(agent)

        logger.info(
            "orchestrator_initialized",
            name=config.name,
            region=config.region,
            agents_count=len(self.agents),
        )

    def register_agent(self, agent: Agent) -> None:
        """Register a new agent.

        Args:
            agent: Agent configuration to register
        """
        self.agents[agent.id] = agent
        logger.info(
            "agent_registered",
            agent_id=str(agent.id),
            agent_name=agent.name,
            agent_type=agent.agent_type,
        )

    def unregister_agent(self, agent_id: UUID) -> None:
        """Unregister an agent.

        Args:
            agent_id: ID of agent to remove
        """
        if agent_id in self.agents:
            agent = self.agents.pop(agent_id)
            logger.info("agent_unregistered", agent_id=str(agent_id), agent_name=agent.name)

    def get_agent_by_type(self, agent_type: AgentType) -> Optional[Agent]:
        """Find the first enabled agent of a specific type.

        Args:
            agent_type: Type of agent to find

        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.enabled:
                return agent
        return None

    def select_agent(self, request: TaskRequest) -> Optional[Agent]:
        """Select the best agent for a task request.

        This implements intelligent agent selection based on:
        1. Preferred agent type from request
        2. Agent availability and load
        3. Agent capabilities

        Args:
            request: Incoming task request

        Returns:
            Selected agent or None if no suitable agent found
        """
        # Use preferred agent if specified
        if request.preferred_agent:
            agent = self.get_agent_by_type(request.preferred_agent)
            if agent:
                logger.debug(
                    "agent_selected_by_preference",
                    agent_name=agent.name,
                    agent_type=agent.agent_type,
                )
                return agent

        # Simple selection: first available agent
        # TODO: Implement load-based selection algorithm
        for agent in self.agents.values():
            if agent.enabled:
                logger.debug(
                    "agent_selected_default",
                    agent_name=agent.name,
                    agent_type=agent.agent_type,
                )
                return agent

        logger.warning("no_agent_available", task_id=str(request.task_id))
        return None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _execute_agent_task(
        self, agent: Agent, request: TaskRequest
    ) -> Dict[str, object]:
        """Execute a task on a specific agent with retry logic.

        Args:
            agent: Agent to execute the task
            request: Task request

        Returns:
            Task execution result

        Raises:
            TimeoutError: If task exceeds timeout
            Exception: For other execution failures
        """
        logger.info(
            "task_execution_started",
            task_id=str(request.task_id),
            agent_name=agent.name,
            agent_type=agent.agent_type,
        )

        try:
            # Apply compliance guardrails
            validated_request = await self.compliance.validate_request(request)

            # Simulate agent execution (replace with actual AWS Lambda/API call)
            await asyncio.sleep(0.5)  # Simulate processing

            result = {
                "status": "success",
                "data": f"Processed by {agent.name}",
                "query": validated_request.query,
                "timestamp": time.time(),
            }

            # Apply output guardrails
            filtered_result = await self.compliance.filter_response(result)

            logger.info(
                "task_execution_completed",
                task_id=str(request.task_id),
                agent_name=agent.name,
            )

            return filtered_result

        except asyncio.TimeoutError:
            logger.error(
                "task_execution_timeout",
                task_id=str(request.task_id),
                agent_name=agent.name,
                timeout=agent.timeout,
            )
            raise
        except Exception as e:
            logger.error(
                "task_execution_failed",
                task_id=str(request.task_id),
                agent_name=agent.name,
                error=str(e),
            )
            raise

    async def process_task(self, request: TaskRequest) -> TaskResponse:
        """Process a single task request.

        Args:
            request: Task request to process

        Returns:
            Task response with results or error
        """
        start_time = time.time()

        # Select agent
        agent = self.select_agent(request)
        if not agent:
            return TaskResponse(
                task_id=request.task_id,
                agent_id=UUID(int=0),
                agent_name="none",
                status=AgentStatus.FAILED,
                error="No suitable agent available",
                execution_time=time.time() - start_time,
            )

        try:
            # Execute task with timeout
            result = await asyncio.wait_for(
                self._execute_agent_task(agent, request),
                timeout=agent.timeout,
            )

            return TaskResponse(
                task_id=request.task_id,
                agent_id=agent.id,
                agent_name=agent.name,
                status=AgentStatus.SUCCESS,
                result=result,
                execution_time=time.time() - start_time,
            )

        except asyncio.TimeoutError:
            return TaskResponse(
                task_id=request.task_id,
                agent_id=agent.id,
                agent_name=agent.name,
                status=AgentStatus.TIMEOUT,
                error=f"Task exceeded timeout of {agent.timeout}s",
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return TaskResponse(
                task_id=request.task_id,
                agent_id=agent.id,
                agent_name=agent.name,
                status=AgentStatus.FAILED,
                error=str(e),
                execution_time=time.time() - start_time,
            )

    async def process_batch(self, requests: List[TaskRequest]) -> List[TaskResponse]:
        """Process multiple tasks concurrently.

        Args:
            requests: List of task requests

        Returns:
            List of task responses
        """
        logger.info("batch_processing_started", batch_size=len(requests))

        tasks = [self.process_task(request) for request in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=False)

        logger.info("batch_processing_completed", batch_size=len(requests))
        return list(responses)

    def health_check(self) -> HealthCheck:
        """Check orchestrator health status.

        Returns:
            Health check information
        """
        active_agents = sum(1 for agent in self.agents.values() if agent.enabled)

        return HealthCheck(
            status="healthy" if active_agents > 0 else "degraded",
            agents_active=active_agents,
            agents_total=len(self.agents),
            uptime_seconds=time.time() - self._start_time,
        )

    async def start(self) -> None:
        """Start the orchestrator background processing."""
        self._running = True
        logger.info("orchestrator_started", name=self.config.name)

    async def stop(self) -> None:
        """Stop the orchestrator gracefully."""
        self._running = False
        logger.info("orchestrator_stopped", name=self.config.name)
