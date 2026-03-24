"""System resource collection via SSH (memory, CPU, disk)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cloud_map.models import CpuInfo, DiskInfo, MemoryInfo, ResourceInfo

if TYPE_CHECKING:
    from cloud_map.models import ServerConfig
    from cloud_map.ssh import SSHManager

# Single compound command to minimize SSH round-trips
_RESOURCE_CMD = " && ".join(
    [
        "free -b | grep Mem",
        "echo '---SEPARATOR---'",
        "nproc",
        "echo '---SEPARATOR---'",
        "vmstat 1 2 | tail -1",
        "echo '---SEPARATOR---'",
        "df -B1 -x tmpfs -x devtmpfs -x squashfs --output=target,size,used,avail 2>/dev/null"
        " || df -B1 --output=target,size,used,avail 2>/dev/null"
        " || df -k",
    ]
)


async def collect_resources(ssh: SSHManager, server: ServerConfig) -> ResourceInfo:
    """Collect memory, CPU, and disk info from a remote server."""
    try:
        output = await ssh.run_command(server, _RESOURCE_CMD)
    except RuntimeError:
        return ResourceInfo()

    sections = output.split("---SEPARATOR---")
    if len(sections) < 4:
        return ResourceInfo()

    memory = _parse_free(sections[0].strip())
    cpu_cores = _parse_nproc(sections[1].strip())
    cpu_usage = _parse_vmstat(sections[2].strip())
    disks = _parse_df(sections[3].strip())

    cpu = None
    if cpu_cores is not None:
        cpu = CpuInfo(cores=cpu_cores, usage_percent=cpu_usage or 0.0)

    return ResourceInfo(memory=memory, cpu=cpu, disks=disks)


def _parse_free(output: str) -> MemoryInfo | None:
    """Parse `free -b | grep Mem` output.

    Format: Mem:  total  used  free  shared  buff/cache  available
    """
    for line in output.splitlines():
        if line.startswith("Mem:"):
            parts = line.split()
            if len(parts) >= 7:
                return MemoryInfo(
                    total=int(parts[1]),
                    used=int(parts[2]),
                    available=int(parts[6]),
                )
    return None


def _parse_nproc(output: str) -> int | None:
    """Parse `nproc` output."""
    line = output.strip().splitlines()[-1] if output.strip() else ""
    try:
        return int(line.strip())
    except ValueError:
        return None


def _parse_vmstat(output: str) -> float | None:
    """Parse `vmstat 1 2 | tail -1` to get CPU usage.

    The last column (id) is idle %; usage = 100 - idle.
    vmstat columns: r b swpd free buff cache si so bi bo in cs us sy id wa st
    """
    line = output.strip().splitlines()[-1] if output.strip() else ""
    parts = line.split()
    if len(parts) >= 15:
        try:
            idle = float(parts[14])
            return round(100.0 - idle, 1)
        except (ValueError, IndexError):
            return None
    return None


def _parse_df(output: str) -> list[DiskInfo]:
    """Parse `df -B1 --output=target,size,used,avail` output."""
    disks = []
    lines = output.strip().splitlines()
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) >= 4:
            try:
                mount = parts[0]
                total = int(parts[1])
                used = int(parts[2])
                available = int(parts[3])
                disks.append(DiskInfo(mount=mount, total=total, used=used, available=available))
            except ValueError:
                continue
    return disks


def format_bytes(value: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(value) < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"
