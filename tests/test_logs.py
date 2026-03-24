"""Tests for on-demand log retrieval."""

from unittest.mock import AsyncMock

import pytest

from cloud_map.logs import (
    MAX_LINES,
    _shell_quote,
    fetch_docker_logs,
    fetch_logs,
    fetch_systemd_logs,
)
from cloud_map.models import ServerConfig


@pytest.fixture
def server():
    return ServerConfig(name="web-1", hostname="10.0.0.1")


@pytest.fixture
def mock_ssh():
    ssh = AsyncMock()
    ssh.run_command = AsyncMock(return_value="log line 1\nlog line 2\n")
    return ssh


class TestShellQuote:
    def test_simple_string(self):
        assert _shell_quote("nginx") == "'nginx'"

    def test_string_with_single_quote(self):
        assert _shell_quote("it's") == "'it'\\''s'"

    def test_empty_string(self):
        assert _shell_quote("") == "''"


class TestFetchDockerLogs:
    async def test_fetches_logs(self, mock_ssh, server):
        result = await fetch_docker_logs(mock_ssh, server, "nginx", lines=50)
        assert result == "log line 1\nlog line 2\n"
        cmd = mock_ssh.run_command.call_args[0][1]
        assert "docker logs --tail 50" in cmd
        assert "'nginx'" in cmd

    async def test_caps_at_max_lines(self, mock_ssh, server):
        await fetch_docker_logs(mock_ssh, server, "nginx", lines=99999)
        cmd = mock_ssh.run_command.call_args[0][1]
        assert f"--tail {MAX_LINES}" in cmd


class TestFetchSystemdLogs:
    async def test_fetches_logs(self, mock_ssh, server):
        result = await fetch_systemd_logs(mock_ssh, server, "redis", lines=200)
        assert result == "log line 1\nlog line 2\n"
        cmd = mock_ssh.run_command.call_args[0][1]
        assert "journalctl -u 'redis'" in cmd
        assert "-n 200" in cmd


class TestFetchLogs:
    async def test_dispatches_docker(self, mock_ssh, server):
        await fetch_logs(mock_ssh, server, "nginx", "docker", 100)
        cmd = mock_ssh.run_command.call_args[0][1]
        assert "docker logs" in cmd

    async def test_dispatches_systemd(self, mock_ssh, server):
        await fetch_logs(mock_ssh, server, "redis", "systemd", 100)
        cmd = mock_ssh.run_command.call_args[0][1]
        assert "journalctl" in cmd
