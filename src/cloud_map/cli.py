"""CLI entry point for Cloud Map."""

from __future__ import annotations

import asyncio

import click
from rich.console import Console

from cloud_map.cache import format_cache_age, load_cache, save_cache
from cloud_map.collector import collect_all
from cloud_map.config import load_inventory
from cloud_map.display import (
    display_containers_table,
    display_ping_results,
    display_services_table,
    display_status_table,
)
from cloud_map.pdf import (
    generate_containers_pdf,
    generate_ping_pdf,
    generate_services_pdf,
    generate_status_pdf,
)
from cloud_map.ssh import SSHManager

console = Console()

DEFAULT_INVENTORY = "inventory.yaml"


def _pdf_option(f):
    """Shared --pdf option for all commands."""
    return click.option(
        "--pdf",
        "pdf_path",
        default=None,
        help="Export output to a PDF file at the given path.",
    )(f)


@click.group()
@click.option(
    "-i",
    "--inventory",
    default=DEFAULT_INVENTORY,
    envvar="CLOUD_MAP_INVENTORY",
    help="Path to inventory YAML file.",
)
@click.pass_context
def cli(ctx: click.Context, inventory: str) -> None:
    """Cloud Map — Cloud server administration and health visualization."""
    ctx.ensure_object(dict)
    ctx.obj["inventory_path"] = inventory


@cli.command()
@_pdf_option
@click.pass_context
def ping(ctx: click.Context, pdf_path: str | None) -> None:
    """Test SSH connectivity to all configured servers."""
    inventory = _load_inventory(ctx)
    ssh = SSHManager()

    async def _ping() -> list[tuple[str, str, bool]]:
        results = []
        for server in inventory.servers:
            reachable = await ssh.check_reachable(server)
            results.append((server.name, server.hostname, reachable))
        await ssh.close_all()
        return results

    results = asyncio.run(_ping())
    display_ping_results(results)

    if pdf_path:
        path = generate_ping_pdf(results, pdf_path)
        console.print(f"[green]PDF saved to:[/green] {path}")


@cli.command()
@click.option("--cached", is_flag=True, help="Show last known state without connecting.")
@_pdf_option
@click.pass_context
def status(ctx: click.Context, cached: bool, pdf_path: str | None) -> None:
    """Display health status of all servers and services."""
    inventory = _load_inventory(ctx)

    if cached:
        try:
            statuses, collected_at = load_cache(inventory.cache_path)
            age = format_cache_age(collected_at)
            display_status_table(statuses, cached=True, collected_at=collected_at, cache_age=age)
            if pdf_path:
                path = generate_status_pdf(statuses, pdf_path, cached=True, cache_age=age)
                console.print(f"[green]PDF saved to:[/green] {path}")
        except FileNotFoundError:
            console.print(
                "[yellow]No cached data available.[/yellow] "
                "Run [bold]cloud-map status[/bold] (without --cached) to collect live data."
            )
        return

    statuses = asyncio.run(collect_all(inventory))
    save_cache(list(statuses), inventory.cache_path)
    display_status_table(list(statuses))

    if pdf_path:
        path = generate_status_pdf(list(statuses), pdf_path)
        console.print(f"[green]PDF saved to:[/green] {path}")


@cli.command()
@_pdf_option
@click.pass_context
def containers(ctx: click.Context, pdf_path: str | None) -> None:
    """List Docker containers across all servers."""
    inventory = _load_inventory(ctx)
    statuses = asyncio.run(collect_all(inventory))
    save_cache(list(statuses), inventory.cache_path)
    display_containers_table(list(statuses))

    if pdf_path:
        path = generate_containers_pdf(list(statuses), pdf_path)
        console.print(f"[green]PDF saved to:[/green] {path}")


@cli.command()
@_pdf_option
@click.pass_context
def services(ctx: click.Context, pdf_path: str | None) -> None:
    """List systemd services across all servers."""
    inventory = _load_inventory(ctx)
    statuses = asyncio.run(collect_all(inventory))
    save_cache(list(statuses), inventory.cache_path)
    display_services_table(list(statuses))

    if pdf_path:
        path = generate_services_pdf(list(statuses), pdf_path)
        console.print(f"[green]PDF saved to:[/green] {path}")


def _load_inventory(ctx: click.Context):
    """Load inventory with error handling."""
    path = ctx.obj["inventory_path"]
    try:
        return load_inventory(path)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Inventory file not found: {path}")
        console.print(
            f"Create an [bold]{DEFAULT_INVENTORY}[/bold] file or use -i to specify a path."
        )
        raise SystemExit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)
