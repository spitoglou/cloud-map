"""Web server configuration discovery via SSH."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cloud_map.models import DomainInfo, WebServerConfig, WebServerType

if TYPE_CHECKING:
    from cloud_map.models import ServerConfig
    from cloud_map.ssh import SSHManager

_NGINX_DEFAULT_PATHS = ["/etc/nginx"]
_HTTPD_DEFAULT_PATHS = ["/etc/httpd", "/etc/apache2"]

# Domains to ignore (catch-all / default entries).
_IGNORED_DOMAINS = {"_", "", "localhost", "default", "*"}


async def discover_domains(
    ssh: SSHManager,
    server: ServerConfig,
) -> list[DomainInfo]:
    """Discover domains configured in web servers on a remote server.

    Behaviour depends on ``server.webservers``:
    * ``None`` – auto-detect nginx and httpd by probing default paths.
    * ``False`` – skip discovery entirely.
    * ``list[WebServerConfig]`` – use the explicit list (with optional custom paths).
    """
    if server.webservers is False:
        return []

    domains: list[DomainInfo] = []

    if server.webservers is None:
        # Auto-detect: probe default directories.
        detected = await _auto_detect(ssh, server)
        for ws in detected:
            domains.extend(await _collect_for_type(ssh, server, ws))
    else:
        for ws in server.webservers:
            domains.extend(await _collect_for_type(ssh, server, ws))

    return domains


async def _auto_detect(
    ssh: SSHManager,
    server: ServerConfig,
) -> list[WebServerConfig]:
    """Probe standard paths to detect installed web servers."""
    all_paths = [(WebServerType.NGINX, p) for p in _NGINX_DEFAULT_PATHS] + [
        (WebServerType.HTTPD, p) for p in _HTTPD_DEFAULT_PATHS
    ]
    # Single compound command: test -d for each path.
    checks = " && ".join(
        f'test -d {p} && echo "YES:{ws_type.value}:{p}" || echo "NO:{ws_type.value}:{p}"'
        for ws_type, p in all_paths
    )
    try:
        output = await ssh.run_command(server, checks)
    except RuntimeError:
        return []

    detected: list[WebServerConfig] = []
    for line in output.strip().splitlines():
        line = line.strip()
        if line.startswith("YES:"):
            _, ws_type_str, path = line.split(":", 2)
            detected.append(WebServerConfig(type=WebServerType(ws_type_str), config_path=path))
    return detected


async def _collect_for_type(
    ssh: SSHManager,
    server: ServerConfig,
    ws: WebServerConfig,
) -> list[DomainInfo]:
    """Collect domains for a specific web server type."""
    if ws.type == WebServerType.NGINX:
        return await _parse_nginx(ssh, server, ws)
    return await _parse_httpd(ssh, server, ws)


async def _parse_nginx(
    ssh: SSHManager,
    server: ServerConfig,
    ws: WebServerConfig,
) -> list[DomainInfo]:
    """Extract domains from nginx server_name directives."""
    paths = [ws.config_path] if ws.config_path else _NGINX_DEFAULT_PATHS
    domains: list[DomainInfo] = []
    for path in paths:
        cmd = f"grep -rHn 'server_name' {path} 2>/dev/null || true"
        try:
            output = await ssh.run_command(server, cmd)
        except RuntimeError:
            continue
        for line in output.strip().splitlines():
            parsed = _parse_nginx_line(line)
            if parsed:
                domains.extend(parsed)
    return domains


def _parse_nginx_line(line: str) -> list[DomainInfo]:
    """Parse a single grep output line for nginx server_name."""
    # Format: /path/to/file:lineno:    server_name example.com www.example.com;
    match = re.match(r"^(.+?):\d+:\s*server_name\s+(.+?)\s*;", line)
    if not match:
        return []
    config_file = match.group(1)
    names = match.group(2).split()
    results = []
    for name in names:
        name = name.strip().rstrip(";")
        if name.lower() not in _IGNORED_DOMAINS:
            results.append(
                DomainInfo(
                    domain=name,
                    web_server_type=WebServerType.NGINX,
                    config_file=config_file,
                )
            )
    return results


async def _parse_httpd(
    ssh: SSHManager,
    server: ServerConfig,
    ws: WebServerConfig,
) -> list[DomainInfo]:
    """Extract domains from Apache ServerName/ServerAlias directives."""
    paths = [ws.config_path] if ws.config_path else _HTTPD_DEFAULT_PATHS
    domains: list[DomainInfo] = []
    for path in paths:
        cmd = f"grep -rHni -E '(ServerName|ServerAlias)' {path} 2>/dev/null || true"
        try:
            output = await ssh.run_command(server, cmd)
        except RuntimeError:
            continue
        for line in output.strip().splitlines():
            parsed = _parse_httpd_line(line)
            if parsed:
                domains.extend(parsed)
    return domains


def _parse_httpd_line(line: str) -> list[DomainInfo]:
    """Parse a single grep output line for Apache ServerName/ServerAlias."""
    # Format: /path/to/file:lineno:  ServerName example.com
    # or:     /path/to/file:lineno:  ServerAlias www.example.com alias.example.com
    match = re.match(r"^(.+?):\d+:\s*(?:ServerName|ServerAlias)\s+(.+)", line, re.IGNORECASE)
    if not match:
        return []
    config_file = match.group(1)
    names = match.group(2).split()
    results = []
    for name in names:
        name = name.strip()
        if name.lower() not in _IGNORED_DOMAINS:
            results.append(
                DomainInfo(
                    domain=name,
                    web_server_type=WebServerType.HTTPD,
                    config_file=config_file,
                )
            )
    return results
