"""Tests for system resource collection and parsing."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cloud_map.models import ServerConfig
from cloud_map.resources import (
    _parse_df,
    _parse_free,
    _parse_nproc,
    _parse_vmstat,
    collect_resources,
    format_bytes,
)

FREE_OUTPUT = "Mem:    8345088000  3172352000   2097152000    524288000  3075584000  4648960000"

NPROC_OUTPUT = "4"

VMSTAT_OUTPUT = (
    " 1  0      0 2097152   524288 3075584    0    0     0     0  150  300  5  3 92  0  0"
)

DF_OUTPUT = """\
Mounted on              1B-blocks         Used    Available
/                    53687091200  21474836480  29360128000
/boot                  1073741824    209715200    796917760
/home                107374182400  42949672960  59055800320
"""


class TestParseFree:
    def test_valid_output(self):
        mem = _parse_free(FREE_OUTPUT)
        assert mem is not None
        assert mem.total == 8345088000
        assert mem.used == 3172352000
        assert mem.available == 4648960000
        assert 37 < mem.used_percent < 39

    def test_empty_output(self):
        assert _parse_free("") is None

    def test_no_mem_line(self):
        assert _parse_free("Swap: 0 0 0") is None


class TestParseNproc:
    def test_valid(self):
        assert _parse_nproc(NPROC_OUTPUT) == 4

    def test_empty(self):
        assert _parse_nproc("") is None

    def test_invalid(self):
        assert _parse_nproc("not a number") is None


class TestParseVmstat:
    def test_valid(self):
        usage = _parse_vmstat(VMSTAT_OUTPUT)
        assert usage is not None
        assert usage == 8.0  # 100 - 92

    def test_empty(self):
        assert _parse_vmstat("") is None


class TestParseDf:
    def test_valid(self):
        disks = _parse_df(DF_OUTPUT)
        assert len(disks) == 3
        assert disks[0].mount == "/"
        assert disks[0].total == 53687091200
        assert disks[0].used == 21474836480
        assert 39 < disks[0].used_percent < 41

    def test_empty(self):
        assert _parse_df("") == []


class TestFormatBytes:
    def test_bytes(self):
        assert format_bytes(500) == "500.0 B"

    def test_kb(self):
        assert format_bytes(2048) == "2.0 KB"

    def test_mb(self):
        assert format_bytes(5 * 1024 * 1024) == "5.0 MB"

    def test_gb(self):
        assert format_bytes(3 * 1024 * 1024 * 1024) == "3.0 GB"


@pytest.fixture
def ssh_mock():
    ssh = MagicMock()
    ssh.run_command = AsyncMock()
    return ssh


@pytest.fixture
def server():
    return ServerConfig(name="test", hostname="10.0.0.1")


@pytest.mark.asyncio
async def test_collect_resources_success(ssh_mock, server):
    ssh_mock.run_command.return_value = (
        FREE_OUTPUT
        + "\n---SEPARATOR---\n"
        + NPROC_OUTPUT
        + "\n---SEPARATOR---\n"
        + VMSTAT_OUTPUT
        + "\n---SEPARATOR---\n"
        + DF_OUTPUT
    )
    info = await collect_resources(ssh_mock, server)
    assert info.memory is not None
    assert info.cpu is not None
    assert info.cpu.cores == 4
    assert info.cpu.usage_percent == 8.0
    assert len(info.disks) == 3


@pytest.mark.asyncio
async def test_collect_resources_command_failure(ssh_mock, server):
    ssh_mock.run_command.side_effect = RuntimeError("command failed")
    info = await collect_resources(ssh_mock, server)
    assert info.memory is None
    assert info.cpu is None
    assert info.disks == []
