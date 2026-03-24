"""SSH connection management."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import asyncssh

if TYPE_CHECKING:
    from cloud_map.models import ServerConfig


class SSHManager:
    """Manages SSH connections to remote servers."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._connections: dict[str, asyncssh.SSHClientConnection] = {}

    async def connect(self, server: ServerConfig) -> asyncssh.SSHClientConnection:
        """Establish or reuse an SSH connection to a server."""
        if server.name in self._connections:
            conn = self._connections[server.name]
            # Check if connection is still alive
            try:
                await asyncio.wait_for(conn.run("echo ok", check=True), timeout=5.0)
                return conn
            except Exception:
                del self._connections[server.name]

        kwargs: dict = {
            "host": server.hostname,
            "port": server.port,
            "username": server.username,
            "known_hosts": None,
        }

        if server.key_path:
            kwargs["client_keys"] = [server.key_path]
        if server.password:
            kwargs["password"] = server.password
        if not server.key_path and not server.password:
            # Try agent-based auth
            kwargs["agent_forwarding"] = False

        conn = await asyncio.wait_for(
            asyncssh.connect(**kwargs),
            timeout=self.timeout,
        )
        self._connections[server.name] = conn
        return conn

    async def run_command(self, server: ServerConfig, command: str) -> str:
        """Execute a command on a remote server and return stdout."""
        conn = await self.connect(server)
        result = await asyncio.wait_for(
            conn.run(command, check=False),
            timeout=self.timeout,
        )
        if result.exit_status != 0:
            raise RuntimeError(
                f"Command failed on {server.name}: {command}\n"
                f"Exit code: {result.exit_status}\n"
                f"Stderr: {result.stderr}"
            )
        return result.stdout or ""

    async def check_reachable(self, server: ServerConfig) -> bool:
        """Check if a server is reachable via SSH."""
        try:
            await self.connect(server)
            return True
        except Exception:
            return False

    async def close(self, server_name: str | None = None) -> None:
        """Close connection(s)."""
        if server_name:
            conn = self._connections.pop(server_name, None)
            if conn:
                conn.close()
        else:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()

    async def close_all(self) -> None:
        """Close all connections."""
        await self.close()
