"""PDF report generation for Cloud Map."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from fpdf import FPDF

from cloud_map.models import HealthStatus, ServerStatus, ServiceType

_STATUS_COLORS = {
    HealthStatus.HEALTHY: (0, 180, 0),
    HealthStatus.UNHEALTHY: (220, 0, 0),
    HealthStatus.DEGRADED: (220, 180, 0),
    HealthStatus.UNKNOWN: (150, 150, 150),
}

_HEADER_BG = (40, 40, 40)
_HEADER_FG = (255, 255, 255)
_ROW_BG_ALT = (245, 245, 245)
_ROW_BG = (255, 255, 255)


class CloudMapPDF(FPDF):
    """PDF document with Cloud Map branding."""

    def __init__(self) -> None:
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Cloud Map Report", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        self.cell(0, 5, f"Generated: {timestamp}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str) -> None:
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def _table_header(self, columns: list[tuple[str, int]]) -> None:
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*_HEADER_BG)
        self.set_text_color(*_HEADER_FG)
        for label, width in columns:
            self.cell(width, 8, label, border=1, fill=True, align="C")
        self.ln()
        self.set_text_color(0, 0, 0)

    def _table_row(self, cells: list[tuple[str, int]], row_index: int) -> None:
        bg = _ROW_BG_ALT if row_index % 2 == 0 else _ROW_BG
        self.set_fill_color(*bg)
        self.set_font("Helvetica", "", 9)
        for text, width in cells:
            self.cell(width, 7, text, border=1, fill=True)
        self.ln()

    def _health_cell(self, status: HealthStatus, width: int) -> None:
        color = _STATUS_COLORS[status]
        self.set_text_color(*color)
        self.set_font("Helvetica", "B", 9)
        self.cell(width, 7, status.value, border=1, fill=True, align="C")
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 9)


def generate_status_pdf(
    statuses: list[ServerStatus],
    output_path: str | Path,
    cached: bool = False,
    cache_age: str | None = None,
) -> Path:
    """Generate a PDF report for the status command."""
    path = Path(output_path)
    pdf = CloudMapPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    if cached and cache_age:
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Cached data - Last updated: {cache_age}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

    pdf.section_title("Service Health Overview")

    cols = [
        ("Server", 35),
        ("Hostname", 35),
        ("Status", 25),
        ("Service", 30),
        ("Type", 20),
        ("Detail", 30),
        ("Health", 15),
    ]
    pdf._table_header(cols)

    row_idx = 0
    for server in statuses:
        if not server.reachable:
            bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(35, 7, server.name, border=1, fill=True)
            pdf.cell(35, 7, server.hostname, border=1, fill=True)
            pdf.cell(25, 7, "UNREACHABLE", border=1, fill=True, align="C")
            pdf.cell(30, 7, "-", border=1, fill=True)
            pdf.cell(20, 7, "-", border=1, fill=True)
            pdf.cell(30, 7, server.error or "", border=1, fill=True)
            pdf._health_cell(HealthStatus.UNKNOWN, 15)
            pdf.ln()
            row_idx += 1
        elif not server.services:
            bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(35, 7, server.name, border=1, fill=True)
            pdf.cell(35, 7, server.hostname, border=1, fill=True)
            pdf.cell(25, 7, "OK", border=1, fill=True, align="C")
            pdf.cell(30, 7, "-", border=1, fill=True)
            pdf.cell(20, 7, "-", border=1, fill=True)
            pdf.cell(30, 7, "no services", border=1, fill=True)
            pdf.cell(15, 7, "-", border=1, fill=True, align="C")
            pdf.ln()
            row_idx += 1
        else:
            for i, svc in enumerate(server.services):
                bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
                pdf.set_fill_color(*bg)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(35, 7, server.name if i == 0 else "", border=1, fill=True)
                pdf.cell(35, 7, server.hostname if i == 0 else "", border=1, fill=True)
                if i == 0:
                    overall = _overall_health(server)
                    pdf.cell(25, 7, overall.value.upper(), border=1, fill=True, align="C")
                else:
                    pdf.cell(25, 7, "", border=1, fill=True)
                pdf.cell(30, 7, svc.name[:20], border=1, fill=True)
                pdf.cell(20, 7, svc.service_type.value, border=1, fill=True, align="C")
                pdf.cell(30, 7, svc.detail[:22], border=1, fill=True)
                pdf._health_cell(svc.health, 15)
                pdf.ln()
                row_idx += 1

    pdf.ln(5)
    _add_fleet_summary(pdf, statuses)

    pdf.output(str(path))
    return path


def generate_ping_pdf(results: list[tuple[str, str, bool]], output_path: str | Path) -> Path:
    """Generate a PDF report for the ping command."""
    path = Path(output_path)
    pdf = CloudMapPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.section_title("Connectivity Check")

    cols = [("Server", 50), ("Hostname", 60), ("Status", 40)]
    pdf._table_header(cols)

    for i, (name, hostname, reachable) in enumerate(results):
        bg = _ROW_BG_ALT if i % 2 == 0 else _ROW_BG
        pdf.set_fill_color(*bg)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(50, 7, name, border=1, fill=True)
        pdf.cell(60, 7, hostname, border=1, fill=True)
        if reachable:
            pdf.set_text_color(0, 180, 0)
            pdf.cell(40, 7, "Reachable", border=1, fill=True, align="C")
        else:
            pdf.set_text_color(220, 0, 0)
            pdf.cell(40, 7, "Unreachable", border=1, fill=True, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln()

    pdf.output(str(path))
    return path


def generate_containers_pdf(statuses: list[ServerStatus], output_path: str | Path) -> Path:
    """Generate a PDF report for the containers command."""
    path = Path(output_path)
    pdf = CloudMapPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.section_title("Docker Containers")

    cols = [("Server", 35), ("Container", 40), ("Detail", 65), ("Health", 20)]
    pdf._table_header(cols)

    row_idx = 0
    for server in statuses:
        docker_svcs = [s for s in server.services if s.service_type == ServiceType.DOCKER]
        if not server.reachable:
            bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(35, 7, server.name, border=1, fill=True)
            pdf.cell(40, 7, "-", border=1, fill=True)
            pdf.cell(65, 7, "unreachable", border=1, fill=True)
            pdf.cell(20, 7, "-", border=1, fill=True, align="C")
            pdf.ln()
            row_idx += 1
        elif not docker_svcs:
            bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(35, 7, server.name, border=1, fill=True)
            pdf.cell(40, 7, "-", border=1, fill=True)
            pdf.cell(65, 7, "no containers", border=1, fill=True)
            pdf.cell(20, 7, "-", border=1, fill=True, align="C")
            pdf.ln()
            row_idx += 1
        else:
            for i, svc in enumerate(docker_svcs):
                bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
                pdf.set_fill_color(*bg)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(35, 7, server.name if i == 0 else "", border=1, fill=True)
                pdf.cell(40, 7, svc.name[:28], border=1, fill=True)
                pdf.cell(65, 7, svc.detail[:48], border=1, fill=True)
                pdf._health_cell(svc.health, 20)
                pdf.ln()
                row_idx += 1

    pdf.output(str(path))
    return path


def generate_services_pdf(statuses: list[ServerStatus], output_path: str | Path) -> Path:
    """Generate a PDF report for the services command."""
    path = Path(output_path)
    pdf = CloudMapPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.section_title("Systemd Services")

    cols = [("Server", 35), ("Service", 45), ("State", 55), ("Health", 25)]
    pdf._table_header(cols)

    row_idx = 0
    for server in statuses:
        systemd_svcs = [s for s in server.services if s.service_type == ServiceType.SYSTEMD]
        if not server.reachable:
            bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(35, 7, server.name, border=1, fill=True)
            pdf.cell(45, 7, "-", border=1, fill=True)
            pdf.cell(55, 7, "unreachable", border=1, fill=True)
            pdf.cell(25, 7, "-", border=1, fill=True, align="C")
            pdf.ln()
            row_idx += 1
        elif not systemd_svcs:
            bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
            pdf.set_fill_color(*bg)
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(35, 7, server.name, border=1, fill=True)
            pdf.cell(45, 7, "-", border=1, fill=True)
            pdf.cell(55, 7, "no services", border=1, fill=True)
            pdf.cell(25, 7, "-", border=1, fill=True, align="C")
            pdf.ln()
            row_idx += 1
        else:
            for i, svc in enumerate(systemd_svcs):
                bg = _ROW_BG_ALT if row_idx % 2 == 0 else _ROW_BG
                pdf.set_fill_color(*bg)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(35, 7, server.name if i == 0 else "", border=1, fill=True)
                pdf.cell(45, 7, svc.name[:30], border=1, fill=True)
                pdf.cell(55, 7, svc.detail[:40], border=1, fill=True)
                pdf._health_cell(svc.health, 25)
                pdf.ln()
                row_idx += 1

    pdf.output(str(path))
    return path


def _overall_health(server: ServerStatus) -> HealthStatus:
    """Determine overall server health."""
    summary = server.summary
    if summary[HealthStatus.UNHEALTHY] > 0:
        return HealthStatus.UNHEALTHY
    if summary[HealthStatus.DEGRADED] > 0:
        return HealthStatus.DEGRADED
    if summary[HealthStatus.UNKNOWN] > 0 and summary[HealthStatus.HEALTHY] == 0:
        return HealthStatus.UNKNOWN
    return HealthStatus.HEALTHY


def _add_fleet_summary(pdf: CloudMapPDF, statuses: list[ServerStatus]) -> None:
    """Add fleet-level summary to PDF."""
    totals = {s: 0 for s in HealthStatus}
    for server in statuses:
        if not server.reachable:
            totals[HealthStatus.UNKNOWN] += 1
        else:
            for svc in server.services:
                totals[svc.health] += 1

    total = sum(totals.values())
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, f"Fleet Summary: {total} services", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for status, count in totals.items():
        if count > 0:
            color = _STATUS_COLORS[status]
            pdf.set_text_color(*color)
            pdf.cell(0, 6, f"  {status.value}: {count}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
