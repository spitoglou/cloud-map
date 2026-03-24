"""Tests for systemd output parsing and discovery."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cloud_map.models import HealthStatus, ServerConfig
from cloud_map.systemd import (
    SystemdNotAvailableError,
    _apply_exclude,
    _parse_unit_names,
    list_services,
)


@pytest.fixture
def ssh_mock():
    ssh = MagicMock()
    ssh.run_command = AsyncMock()
    return ssh


SYSTEMCTL_SHOW_OUTPUT = """\
Id=nginx.service
ActiveState=active
SubState=running
Description=A high performance web server

Id=postgresql.service
ActiveState=failed
SubState=failed
Description=PostgreSQL database server
"""

SYSTEMCTL_LIST_OUTPUT = """\
dbus.service                loaded active running D-Bus System Message Bus
nginx.service               loaded active running A high performance web server
postgresql.service          loaded active running PostgreSQL database server
systemd-journald.service    loaded active running Journal Service
systemd-logind.service      loaded active running User Login Management
redis-server.service        loaded active running Advanced key-value store
"""


@pytest.mark.asyncio
async def test_explicit_services(ssh_mock):
    """When systemd_services is set, only those are queried."""
    server = ServerConfig(
        name="test", hostname="10.0.0.1", systemd_services=["nginx", "postgresql"]
    )
    ssh_mock.run_command.return_value = SYSTEMCTL_SHOW_OUTPUT
    services = await list_services(ssh_mock, server)
    assert len(services) == 2
    assert services[0].name == "nginx"
    assert services[0].health_status == HealthStatus.HEALTHY
    assert services[1].name == "postgresql"
    assert services[1].health_status == HealthStatus.UNHEALTHY
    # Should call systemctl show, not list-units
    call_args = ssh_mock.run_command.call_args[0][1]
    assert "systemctl show" in call_args


@pytest.mark.asyncio
async def test_auto_discover_all(ssh_mock):
    """When systemd_services is empty, all services are discovered."""
    server = ServerConfig(name="test", hostname="10.0.0.1")
    ssh_mock.run_command.side_effect = [
        SYSTEMCTL_LIST_OUTPUT,  # list-units call
        SYSTEMCTL_SHOW_OUTPUT,  # show call (for the discovered services)
    ]
    await list_services(ssh_mock, server)
    assert ssh_mock.run_command.call_count == 2
    first_call = ssh_mock.run_command.call_args_list[0][0][1]
    assert "list-units" in first_call


@pytest.mark.asyncio
async def test_auto_discover_with_exclude(ssh_mock):
    """Exclude patterns filter out matching services."""
    server = ServerConfig(
        name="test",
        hostname="10.0.0.1",
        systemd_exclude=["systemd-*", "dbus"],
    )
    ssh_mock.run_command.side_effect = [
        SYSTEMCTL_LIST_OUTPUT,
        SYSTEMCTL_SHOW_OUTPUT,
    ]
    await list_services(ssh_mock, server)
    # The show command should only contain non-excluded services
    show_call = ssh_mock.run_command.call_args_list[1][0][1]
    assert "systemd-journald" not in show_call
    assert "systemd-logind" not in show_call
    assert "dbus" not in show_call
    assert "nginx" in show_call
    assert "postgresql" in show_call
    assert "redis-server" in show_call


@pytest.mark.asyncio
async def test_systemd_not_available(ssh_mock):
    server = ServerConfig(name="test", hostname="10.0.0.1", systemd_services=["nginx"])
    ssh_mock.run_command.side_effect = RuntimeError("systemctl: command not found")
    with pytest.raises(SystemdNotAvailableError):
        await list_services(ssh_mock, server)


class TestParseUnitNames:
    def test_parses_service_names(self):
        names = _parse_unit_names(SYSTEMCTL_LIST_OUTPUT)
        assert "nginx" in names
        assert "postgresql" in names
        assert "dbus" in names
        assert "systemd-journald" in names

    def test_empty_output(self):
        assert _parse_unit_names("") == []
        assert _parse_unit_names("\n\n") == []


class TestApplyExclude:
    def test_no_patterns(self):
        names = ["nginx", "dbus", "systemd-journald"]
        assert _apply_exclude(names, []) == names

    def test_exact_match(self):
        names = ["nginx", "dbus", "redis"]
        assert _apply_exclude(names, ["dbus"]) == ["nginx", "redis"]

    def test_glob_pattern(self):
        names = ["nginx", "systemd-journald", "systemd-logind", "redis"]
        result = _apply_exclude(names, ["systemd-*"])
        assert result == ["nginx", "redis"]

    def test_multiple_patterns(self):
        names = ["nginx", "dbus", "systemd-journald", "redis"]
        result = _apply_exclude(names, ["systemd-*", "dbus"])
        assert result == ["nginx", "redis"]
