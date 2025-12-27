#!/usr/bin/env python3
"""Quickstart example for AWS Orchestrator.

This example demonstrates how to:
1. Create an orchestrator configuration
2. Register agents
3. Process tasks
4. Handle responses
"""

import asyncio

from aws_orchestrator import (
    Agent,
    AgentType,
    Orchestrator,
    OrchestratorConfig,
    TaskRequest,
)
from aws_orchestrator.core.models import GuardrailConfig


async def main() -> None:
    """Main example function."""
    # 1. Create orchestrator configuration
    print("🚀 Setting up AWS Orchestrator...")

    config = OrchestratorConfig(
        name="quickstart-orchestrator",
        region="us-east-1",
        agents=[
            Agent(
                name="BedrockAgent",
                agent_type=AgentType.BEDROCK,
                description="AI agent powered by AWS Bedrock",
                endpoint="arn:aws:lambda:us-east-1:123456789:function:bedrock-agent",
                timeout=60,
                metadata={"model_id": "anthropic.claude-v2"},
            ),
            Agent(
                name="AnalyticsAgent",
                agent_type=AgentType.ANALYTICS,
                description="Data analytics agent",
                endpoint="arn:aws:lambda:us-east-1:123456789:function:analytics-agent",
                timeout=45,
            ),
        ],
        guardrails=GuardrailConfig(
            enabled=True,
            pii_detection=True,
            audit_logging=True,
        ),
    )

    # 2. Initialize orchestrator
    orchestrator = Orchestrator(config)

    # 3. Check health
    health = orchestrator.health_check()
    print(f"📊 Health Status: {health.status}")
    print(f"🤖 Active Agents: {health.agents_active}/{health.agents_total}")

    # 4. Process a single task
    print("\n📝 Processing single task...")
    request = TaskRequest(
        user_id="demo-user",
        query="Analyze customer sentiment from Q4 sales data",
        preferred_agent=AgentType.BEDROCK,
    )

    response = await orchestrator.process_task(request)
    print(f"✅ Task Status: {response.status}")
    print(f"⏱️  Execution Time: {response.execution_time:.3f}s")
    print(f"🤖 Agent Used: {response.agent_name}")
    if response.result:
        print(f"📊 Result: {response.result.get('response', 'N/A')}")

    # 5. Process batch tasks
    print("\n📦 Processing batch tasks...")
    batch_requests = [
        TaskRequest(user_id="user-1", query="What are the top products?"),
        TaskRequest(user_id="user-2", query="Send notification to sales team"),
        TaskRequest(user_id="user-3", query="Generate quarterly report"),
    ]

    batch_responses = await orchestrator.process_batch(batch_requests)
    print(f"✅ Processed {len(batch_responses)} tasks")

    for idx, resp in enumerate(batch_responses, 1):
        print(f"  Task {idx}: {resp.status} ({resp.execution_time:.3f}s)")

    # 6. Demonstrate PII masking
    print("\n🔒 Testing PII detection...")
    pii_request = TaskRequest(
        user_id="security-test",
        query="Contact me at john.doe@example.com or call 555-123-4567",
    )

    pii_response = await orchestrator.process_task(pii_request)
    print(f"🔒 PII Masked Query: {pii_request.query}")

    print("\n✅ Quickstart complete!")


if __name__ == "__main__":
    asyncio.run(main())
