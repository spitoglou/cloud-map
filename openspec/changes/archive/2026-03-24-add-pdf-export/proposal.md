# Change: Add PDF export to all CLI commands

## Why
Users need printable reports of server health, container status, and connectivity checks for documentation, audits, or offline review.

## What Changes
- Add `--pdf <path>` flag to all CLI commands (`ping`, `status`, `containers`, `services`)
- Add `fpdf2` dependency for PDF generation
- Create `pdf.py` module with formatted table output mirroring terminal display

## Impact
- Affected specs: `pdf-export` (new)
- Affected code: `cli.py`, new `pdf.py`
