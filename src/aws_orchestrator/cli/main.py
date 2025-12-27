"""Beautiful CLI interface using Typer and Rich.

This module provides the main command-line interface for AWS Orchestrator
with colorful output, progress bars, and tables.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aws_orchestrator import __version__
from aws_orchestrator.core.models import (
    Agent,
    AgentType,
    GuardrailConfig,
    OrchestratorConfig,
    TaskRequest,
)
from aws_orchestrator.core.orchestrator import Orchestrator
from aws_orchestrator.utils.logger import setup_logging

app = typer.Typer(
    name="aws-orchestrator",
    help="Production-ready multi-agent orchestration for AWS",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        console.print(f"[bold cyan]AWS Orchestrator[/bold cyan] version {__version__}")
        console.print(f"[dim]Author: Ruslan Magana (ruslanmv.com)[/dim]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """AWS Orchestrator - Multi-Agent Orchestration Framework for AWS."""
    pass


@app.command()
def init(
    name: str = typer.Option("my-orchestrator", help="Orchestrator name"),
    region: str = typer.Option("us-east-1", help="AWS region"),
    output: Path = typer.Option(
        Path("orchestrator-config.json"), help="Output configuration file"
    ),
) -> None:
    """Initialize a new orchestrator configuration.

    Creates a sample configuration file with example agents and guardrails.
    """
    console.print(
        Panel.fit(
            "[bold cyan]Initializing AWS Orchestrator[/bold cyan]",
            border_style="cyan",
        )
    )

    # Create sample configuration
    config = OrchestratorConfig(
        name=name,
        region=region,
        agents=[
            Agent(
                name="BedrockAgent",
                agent_type=AgentType.BEDROCK,
                description="AI agent powered by AWS Bedrock",
                endpoint="arn:aws:lambda:us-east-1:123456789:function:bedrock-agent",
                timeout=60,
            ),
            Agent(
                name="AnalyticsAgent",
                agent_type=AgentType.ANALYTICS,
                description="Data analytics and insights",
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

    # Write configuration
    with open(output, "w") as f:
        f.write(config.model_dump_json(indent=2))

    console.print(f"[green]✓[/green] Configuration created: {output}")
    console.print(f"[dim]Orchestrator name:[/dim] {name}")
    console.print(f"[dim]Region:[/dim] {region}")
    console.print(f"[dim]Agents:[/dim] {len(config.agents)}")


@app.command()
def run(
    query: str = typer.Argument(..., help="Query to process"),
    user_id: str = typer.Option("cli-user", help="User ID"),
    agent_type: Optional[str] = typer.Option(None, help="Preferred agent type"),
    debug: bool = typer.Option(False, help="Enable debug logging"),
) -> None:
    """Execute a query using the orchestrator.

    Process a single query through the multi-agent system with
    automatic agent selection and compliance guardrails.
    """
    setup_logging("DEBUG" if debug else "INFO")

    console.print(
        Panel.fit(
            "[bold cyan]AWS Orchestrator - Task Execution[/bold cyan]",
            border_style="cyan",
        )
    )

    # Create sample orchestrator
    config = OrchestratorConfig(
        name="cli-orchestrator",
        agents=[
            Agent(
                name="BedrockAgent",
                agent_type=AgentType.BEDROCK,
                description="AI agent powered by AWS Bedrock",
                endpoint="arn:aws:lambda:us-east-1:123456789:function:bedrock-agent",
                timeout=60,
                metadata={"model_id": "anthropic.claude-v2"},
            ),
        ],
    )

    orchestrator = Orchestrator(config)

    # Create task request
    request = TaskRequest(
        user_id=user_id,
        query=query,
        preferred_agent=AgentType(agent_type) if agent_type else None,
    )

    # Execute task
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing query...", total=None)

        async def execute() -> None:
            response = await orchestrator.process_task(request)

            progress.update(task, completed=True)

            # Display results
            result_table = Table(title="Task Result", show_header=True, header_style="bold cyan")
            result_table.add_column("Field", style="cyan")
            result_table.add_column("Value", style="white")

            result_table.add_row("Task ID", str(response.task_id))
            result_table.add_row("Agent", response.agent_name)
            result_table.add_row("Status", f"[green]{response.status}[/green]")
            result_table.add_row("Execution Time", f"{response.execution_time:.3f}s")

            if response.result:
                result_table.add_row("Result", str(response.result.get("response", "N/A")))

            if response.error:
                result_table.add_row("Error", f"[red]{response.error}[/red]")

            console.print(result_table)

        asyncio.run(execute())


@app.command()
def health() -> None:
    """Check orchestrator health status.

    Displays the current health status of the orchestrator including
    active agents and system uptime.
    """
    config = OrchestratorConfig(
        name="health-check",
        agents=[
            Agent(
                name="BedrockAgent",
                agent_type=AgentType.BEDROCK,
                endpoint="arn:aws:lambda:us-east-1:123456789:function:bedrock-agent",
            ),
        ],
    )

    orchestrator = Orchestrator(config)
    health_status = orchestrator.health_check()

    health_table = Table(title="Health Check", show_header=True, header_style="bold cyan")
    health_table.add_column("Metric", style="cyan")
    health_table.add_column("Value", style="white")

    health_table.add_row("Status", f"[green]{health_status.status.upper()}[/green]")
    health_table.add_row("Active Agents", str(health_status.agents_active))
    health_table.add_row("Total Agents", str(health_status.agents_total))
    health_table.add_row("Uptime", f"{health_status.uptime_seconds:.2f}s")

    console.print(health_table)


@app.command()
def agents() -> None:
    """List all available agent types.

    Shows the different types of agents supported by the orchestrator.
    """
    agents_table = Table(title="Available Agent Types", show_header=True, header_style="bold cyan")
    agents_table.add_column("Type", style="cyan")
    agents_table.add_column("Description", style="white")

    agents_table.add_row("bedrock", "AI agent powered by AWS Bedrock")
    agents_table.add_row("analytics", "Data analytics and insights")
    agents_table.add_row("notification", "Notification management")
    agents_table.add_row("custom", "Custom agent implementation")

    console.print(agents_table)


if __name__ == "__main__":
    app()
