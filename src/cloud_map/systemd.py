"""Systemd service management via SSH."""

from __future__ import annotations

import fnmatch
from typing import TYPE_CHECKING

from cloud_map.models import SystemdServiceInfo

if TYPE_CHECKING:
    from cloud_map.models import ServerConfig
    from cloud_map.ssh import SSHManager

# systemctl list-units output columns we parse
_LIST_CMD = "systemctl list-units --type=service --no-legend --no-pager --plain --output=short"

_SHOW_PROPS = "--property=Id,ActiveState,SubState,Description --no-pager"


async def list_services(ssh: SSHManager, server: ServerConfig) -> list[SystemdServiceInfo]:
    """List systemd services on a remote server.

    If server.systemd_services is non-empty, only those services are checked.
    Otherwise, all services are auto-discovered and filtered by systemd_exclude.
    """
    try:
        if server.systemd_services:
            return await _list_explicit(ssh, server)
        return await _list_discovered(ssh, server)
    except RuntimeError as e:
        if "not found" in str(e).lower():
            raise SystemdNotAvailableError(f"systemd not available on {server.name}") from e
        raise


async def _list_explicit(ssh: SSHManager, server: ServerConfig) -> list[SystemdServiceInfo]:
    """Query explicitly listed services."""
    service_names = " ".join(server.systemd_services)
    output = await ssh.run_command(server, f"systemctl show {service_names} {_SHOW_PROPS}")
    return _parse_systemctl_show(output)


async def _list_discovered(ssh: SSHManager, server: ServerConfig) -> list[SystemdServiceInfo]:
    """Auto-discover all services, then filter by exclude patterns."""
    # Get list of all service unit names
    output = await ssh.run_command(server, _LIST_CMD)
    unit_names = _parse_unit_names(output)

    # Apply exclude patterns
    unit_names = _apply_exclude(unit_names, server.systemd_exclude)

    if not unit_names:
        return []

    # Get detailed info for remaining services
    names_arg = " ".join(unit_names)
    show_output = await ssh.run_command(server, f"systemctl show {names_arg} {_SHOW_PROPS}")
    return _parse_systemctl_show(show_output)


def _parse_unit_names(output: str) -> list[str]:
    """Parse unit names from systemctl list-units output.

    Each line looks like:
      nginx.service loaded active running A high performance web server
    We extract the first column (unit name) and strip the .service suffix.
    """
    names = []
    for line in output.strip().splitlines():
        parts = line.split()
        if not parts:
            continue
        unit = parts[0].strip()
        # Only include .service units
        if unit.endswith(".service"):
            names.append(unit[: -len(".service")])
    return names


def _apply_exclude(names: list[str], patterns: list[str]) -> list[str]:
    """Filter out service names matching any exclude pattern (glob/fnmatch)."""
    if not patterns:
        return names
    return [name for name in names if not any(fnmatch.fnmatch(name, pat) for pat in patterns)]


def _parse_systemctl_show(output: str) -> list[SystemdServiceInfo]:
    """Parse output of systemctl show for multiple services."""
    services = []
    current: dict[str, str] = {}

    for line in output.splitlines():
        line = line.strip()
        if not line:
            if current:
                services.append(_build_service_info(current))
                current = {}
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            current[key.strip()] = value.strip()

    if current:
        services.append(_build_service_info(current))

    return services


def _build_service_info(props: dict[str, str]) -> SystemdServiceInfo:
    """Build a SystemdServiceInfo from parsed properties."""
    name = props.get("Id", "unknown")
    # Strip .service suffix for cleaner display
    if name.endswith(".service"):
        name = name[: -len(".service")]
    return SystemdServiceInfo(
        name=name,
        active_state=props.get("ActiveState", "unknown"),
        sub_state=props.get("SubState", "unknown"),
        description=props.get("Description", ""),
    )


class SystemdNotAvailableError(Exception):
    """Raised when systemd is not available on a server."""
