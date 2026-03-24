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
    display_domains_table,
    display_ping_results,
    display_resources_table,
    display_services_table,
    display_status_table,
)
from cloud_map.pdf import (
    generate_containers_pdf,
    generate_domains_pdf,
    generate_ping_pdf,
    generate_resources_pdf,
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


@cli.command()
@_pdf_option
@click.pass_context
def resources(ctx: click.Context, pdf_path: str | None) -> None:
    """Display system resources (CPU, memory, disk) across all servers."""
    inventory = _load_inventory(ctx)
    statuses = asyncio.run(collect_all(inventory))
    save_cache(list(statuses), inventory.cache_path)
    display_resources_table(list(statuses))

    if pdf_path:
        path = generate_resources_pdf(list(statuses), pdf_path)
        console.print(f"[green]PDF saved to:[/green] {path}")


@cli.command()
@_pdf_option
@click.pass_context
def domains(ctx: click.Context, pdf_path: str | None) -> None:
    """Display discovered web server domains across all servers."""
    inventory = _load_inventory(ctx)
    statuses = asyncio.run(collect_all(inventory))
    save_cache(list(statuses), inventory.cache_path)
    display_domains_table(list(statuses))

    if pdf_path:
        path = generate_domains_pdf(list(statuses), pdf_path)
        console.print(f"[green]PDF saved to:[/green] {path}")


@cli.command("logs")
@click.argument("server")
@click.argument("service")
@click.option("--lines", "-n", default=100, type=int, help="Number of log lines to fetch.")
@click.option("--follow", "-f", is_flag=True, help="Stream logs continuously (Ctrl+C to stop).")
@click.pass_context
def logs_cmd(ctx: click.Context, server: str, service: str, lines: int, follow: bool) -> None:
    """View logs for a container or service on a server."""
    import sys

    from cloud_map.logs import MAX_LINES

    inventory = _load_inventory(ctx)
    server_cfg = next((s for s in inventory.servers if s.name == server), None)
    if not server_cfg:
        console.print(f"[red]Error:[/red] Server '{server}' not found in inventory.")
        raise SystemExit(1)

    lines = max(1, min(lines, MAX_LINES))

    # Determine service type from cached data if available.
    svc_type = _detect_service_type(inventory, server, service)

    if follow:
        _follow_logs(server_cfg, service, svc_type, lines)
    else:
        output = asyncio.run(_fetch_logs(server_cfg, service, svc_type, lines))
        sys.stdout.write(output)
        if output and not output.endswith("\n"):
            sys.stdout.write("\n")


def _detect_service_type(inventory, server_name: str, service_name: str) -> str:
    """Try to detect whether a service is docker or systemd from cached data."""
    try:
        from cloud_map.cache import load_cache

        statuses, _ = load_cache(inventory.cache_path)
        for s in statuses:
            if s.name == server_name:
                for svc in s.services:
                    if svc.name == service_name:
                        return svc.service_type.value
    except (FileNotFoundError, KeyError):
        pass
    # Default to docker; if that fails the error message will hint at the issue.
    return "docker"


async def _fetch_logs(server_cfg, service: str, svc_type: str, lines: int) -> str:
    from cloud_map.logs import fetch_logs
    from cloud_map.ssh import SSHManager

    ssh = SSHManager()
    try:
        return await fetch_logs(ssh, server_cfg, service, svc_type, lines)
    finally:
        await ssh.close_all()


def _follow_logs(server_cfg, service: str, svc_type: str, lines: int) -> None:
    """Stream logs using --follow."""
    import subprocess

    if svc_type == "docker":
        cmd = f"docker logs --tail {lines} -f {service}"
    else:
        cmd = f"journalctl -u {service} -n {lines} --no-pager -f"

    # Build SSH command to stream.
    ssh_args = ["ssh", "-o", "StrictHostKeyChecking=no"]
    if server_cfg.key_path:
        ssh_args += ["-i", server_cfg.key_path]
    if server_cfg.port != 22:
        ssh_args += ["-p", str(server_cfg.port)]
    ssh_args.append(f"{server_cfg.username}@{server_cfg.hostname}")
    ssh_args.append(cmd)

    try:
        subprocess.run(ssh_args)
    except KeyboardInterrupt:
        pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Address to bind the web server to.")
@click.option("--port", default=8000, type=int, help="Port to bind the web server to.")
@click.option("--refresh", default=30, type=int, help="Default auto-refresh interval in seconds.")
@click.pass_context
def web(ctx: click.Context, host: str, port: int, refresh: int) -> None:
    """Start the web monitoring dashboard."""
    import uvicorn

    from cloud_map.web import app, configure

    inventory = _load_inventory(ctx)
    configure(inventory, refresh=refresh)
    console.print(f"[green]Starting dashboard at[/green] http://{host}:{port}/")
    uvicorn.run(app, host=host, port=port, log_level="info")


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
