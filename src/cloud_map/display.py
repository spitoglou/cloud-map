"""Rich terminal display for health visualization."""

from __future__ import annotations

from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.text import Text

from cloud_map.models import HealthStatus, ServerStatus
from cloud_map.resources import format_bytes

console = Console()

_STATUS_COLORS = {
    HealthStatus.HEALTHY: "green",
    HealthStatus.UNHEALTHY: "red",
    HealthStatus.DEGRADED: "yellow",
    HealthStatus.UNKNOWN: "dim",
}

_STATUS_SYMBOLS = {
    HealthStatus.HEALTHY: "●",
    HealthStatus.UNHEALTHY: "●",
    HealthStatus.DEGRADED: "●",
    HealthStatus.UNKNOWN: "○",
}


def display_status_table(
    statuses: list[ServerStatus],
    cached: bool = False,
    collected_at: datetime | None = None,
    cache_age: str | None = None,
) -> None:
    """Display a color-coded health status table."""
    if cached and cache_age:
        console.print(f"\n[dim]Cached data — Last updated: {cache_age}[/dim]")

    table = Table(title="Cloud Map — Service Health", show_lines=True)
    table.add_column("Server", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Services", min_width=40)

    for server in statuses:
        server_status = _server_health_indicator(server)
        services_text = _format_services(server)
        table.add_row(
            f"{server.name}\n[dim]{server.hostname}[/dim]",
            server_status,
            services_text,
        )

    console.print(table)
    console.print()

    # Fleet summary
    _display_fleet_summary(statuses)


def display_ping_results(results: list[tuple[str, str, bool]]) -> None:
    """Display SSH ping results."""
    table = Table(title="Cloud Map — Connectivity Check")
    table.add_column("Server", style="bold")
    table.add_column("Hostname")
    table.add_column("Status", justify="center")

    for name, hostname, reachable in results:
        if reachable:
            status = Text("✓ Reachable", style="green")
        else:
            status = Text("✗ Unreachable", style="red")
        table.add_row(name, hostname, status)

    console.print(table)


def display_containers_table(statuses: list[ServerStatus]) -> None:
    """Display Docker containers across servers."""
    table = Table(title="Cloud Map — Docker Containers", show_lines=True)
    table.add_column("Server", style="bold")
    table.add_column("Container")
    table.add_column("Status")
    table.add_column("Health", justify="center")

    for server in statuses:
        from cloud_map.models import ServiceType

        docker_services = [s for s in server.services if s.service_type == ServiceType.DOCKER]
        if not server.reachable:
            table.add_row(server.name, "[dim]—[/dim]", "[dim]unreachable[/dim]", "")
        elif not docker_services:
            table.add_row(server.name, "[dim]—[/dim]", "[dim]no containers[/dim]", "")
        else:
            for i, svc in enumerate(docker_services):
                name = server.name if i == 0 else ""
                color = _STATUS_COLORS[svc.health]
                symbol = _STATUS_SYMBOLS[svc.health]
                table.add_row(
                    name,
                    svc.name,
                    svc.detail,
                    Text(f"{symbol} {svc.health.value}", style=color),
                )

    console.print(table)


def display_services_table(statuses: list[ServerStatus]) -> None:
    """Display systemd services across servers."""
    table = Table(title="Cloud Map — Systemd Services", show_lines=True)
    table.add_column("Server", style="bold")
    table.add_column("Service")
    table.add_column("State")
    table.add_column("Health", justify="center")

    for server in statuses:
        from cloud_map.models import ServiceType

        systemd_services = [s for s in server.services if s.service_type == ServiceType.SYSTEMD]
        if not server.reachable:
            table.add_row(server.name, "[dim]—[/dim]", "[dim]unreachable[/dim]", "")
        elif not systemd_services:
            table.add_row(server.name, "[dim]—[/dim]", "[dim]no services[/dim]", "")
        else:
            for i, svc in enumerate(systemd_services):
                name = server.name if i == 0 else ""
                color = _STATUS_COLORS[svc.health]
                symbol = _STATUS_SYMBOLS[svc.health]
                table.add_row(
                    name,
                    svc.name,
                    svc.detail,
                    Text(f"{symbol} {svc.health.value}", style=color),
                )

    console.print(table)


def _server_health_indicator(server: ServerStatus) -> Text:
    """Generate overall health indicator for a server."""
    if not server.reachable:
        return Text("○ UNKNOWN", style="dim")

    summary = server.summary
    if summary[HealthStatus.UNHEALTHY] > 0:
        return Text("● UNHEALTHY", style="red")
    if summary[HealthStatus.DEGRADED] > 0:
        return Text("● DEGRADED", style="yellow")
    if summary[HealthStatus.UNKNOWN] > 0 and summary[HealthStatus.HEALTHY] == 0:
        return Text("○ UNKNOWN", style="dim")
    return Text("● HEALTHY", style="green")


def _format_services(server: ServerStatus) -> Text:
    """Format service list with health indicators."""
    if not server.reachable:
        return Text(f"unreachable: {server.error or 'unknown'}", style="dim")

    text = Text()
    for i, svc in enumerate(server.services):
        if i > 0:
            text.append("\n")
        color = _STATUS_COLORS[svc.health]
        symbol = _STATUS_SYMBOLS[svc.health]
        type_tag = f"[{svc.service_type.value}]"
        text.append(f"{symbol} ", style=color)
        text.append(f"{svc.name} ", style="bold")
        text.append(f"{type_tag} ", style="dim")
        text.append(svc.detail, style="dim")
    return text


def _display_fleet_summary(statuses: list[ServerStatus]) -> None:
    """Display fleet-level health summary."""
    totals = {s: 0 for s in HealthStatus}
    for server in statuses:
        if not server.reachable:
            # Count all potential services as unknown
            totals[HealthStatus.UNKNOWN] += 1
        else:
            for svc in server.services:
                totals[svc.health] += 1

    total = sum(totals.values())
    parts = []
    for status, count in totals.items():
        if count > 0:
            color = _STATUS_COLORS[status]
            parts.append(f"[{color}]{count} {status.value}[/{color}]")

    console.print(f"Fleet: {total} services — {', '.join(parts)}")


def display_resources_table(statuses: list[ServerStatus]) -> None:
    """Display system resource usage across servers."""
    table = Table(title="Cloud Map — System Resources", show_lines=True)
    table.add_column("Server", style="bold")
    table.add_column("CPU Cores", justify="center")
    table.add_column("CPU Usage", justify="center")
    table.add_column("Memory", min_width=25)
    table.add_column("Disks", min_width=35)

    for server in statuses:
        if not server.reachable:
            table.add_row(
                f"{server.name}\n[dim]{server.hostname}[/dim]",
                "[dim]—[/dim]",
                "[dim]—[/dim]",
                "[dim]unreachable[/dim]",
                "[dim]unreachable[/dim]",
            )
            continue

        r = server.resources
        if not r:
            table.add_row(
                f"{server.name}\n[dim]{server.hostname}[/dim]",
                "[dim]—[/dim]",
                "[dim]—[/dim]",
                "[dim]no data[/dim]",
                "[dim]no data[/dim]",
            )
            continue

        # CPU
        cores = str(r.cpu.cores) if r.cpu else "—"
        if r.cpu:
            usage = r.cpu.usage_percent
            usage_color = "green" if usage < 70 else "yellow" if usage < 90 else "red"
            cpu_usage = f"[{usage_color}]{usage:.1f}%[/{usage_color}]"
        else:
            cpu_usage = "—"

        # Memory
        if r.memory:
            pct = r.memory.used_percent
            mem_color = "green" if pct < 70 else "yellow" if pct < 90 else "red"
            mem_text = (
                f"[{mem_color}]{pct:.1f}% used[/{mem_color}]\n"
                f"[dim]{format_bytes(r.memory.used)} / {format_bytes(r.memory.total)}[/dim]\n"
                f"[dim]{format_bytes(r.memory.available)} available[/dim]"
            )
        else:
            mem_text = "—"

        # Disks
        if r.disks:
            disk_parts = []
            for d in r.disks:
                pct = d.used_percent
                d_color = "green" if pct < 70 else "yellow" if pct < 90 else "red"
                disk_parts.append(
                    f"[bold]{d.mount}[/bold] "
                    f"[{d_color}]{pct:.1f}%[/{d_color}] "
                    f"[dim]{format_bytes(d.used)}/{format_bytes(d.total)}[/dim]"
                )
            disk_text = "\n".join(disk_parts)
        else:
            disk_text = "—"

        table.add_row(
            f"{server.name}\n[dim]{server.hostname}[/dim]",
            cores,
            cpu_usage,
            mem_text,
            disk_text,
        )

    console.print(table)
