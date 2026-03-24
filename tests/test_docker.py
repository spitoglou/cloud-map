"""Tests for Docker output parsing."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from cloud_map.docker import DockerNotAvailableError, list_containers
from cloud_map.models import HealthStatus


def _make_docker_line(
    id_="abc123",
    name="web",
    image="nginx:latest",
    status="Up 2 hours",
    state="running",
    ports="0.0.0.0:80->80/tcp",
):
    return json.dumps(
        {
            "ID": id_,
            "Name": name,
            "Image": image,
            "Status": status,
            "State": state,
            "Ports": ports,
        }
    )


@pytest.fixture
def ssh_mock():
    ssh = MagicMock()
    ssh.run_command = AsyncMock()
    return ssh


@pytest.fixture
def server():
    from cloud_map.models import ServerConfig

    return ServerConfig(name="test", hostname="10.0.0.1")


@pytest.mark.asyncio
async def test_list_containers_parses_output(ssh_mock, server):
    ssh_mock.run_command.return_value = (
        _make_docker_line(name="web", status="Up 2 hours (healthy)", state="running")
        + "\n"
        + _make_docker_line(
            id_="def456",
            name="db",
            image="postgres:16",
            status="Up 1 hour",
            state="running",
            ports="5432/tcp",
        )
    )
    containers = await list_containers(ssh_mock, server)
    assert len(containers) == 2
    assert containers[0].name == "web"
    assert containers[0].health == "healthy"
    assert containers[0].health_status == HealthStatus.HEALTHY
    assert containers[1].name == "db"
    assert containers[1].health == "no healthcheck"


@pytest.mark.asyncio
async def test_list_containers_empty(ssh_mock, server):
    ssh_mock.run_command.return_value = ""
    containers = await list_containers(ssh_mock, server)
    assert containers == []


@pytest.mark.asyncio
async def test_docker_not_available(ssh_mock, server):
    ssh_mock.run_command.side_effect = RuntimeError("docker: command not found")
    with pytest.raises(DockerNotAvailableError):
        await list_containers(ssh_mock, server)
