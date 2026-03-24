## 1. Dependencies & Project Setup
- [x] 1.1 Add `fastapi`, `jinja2`, and `uvicorn` to `pyproject.toml` dependencies
- [x] 1.2 Create `src/cloud_map/templates/` directory

## 2. Web Application
- [x] 2.1 Create `src/cloud_map/web.py` with FastAPI app, Jinja2 template setup, and routes
- [x] 2.2 Implement `GET /` route rendering the dashboard template with collected data
- [x] 2.3 Implement `GET /api/status` JSON endpoint returning server statuses and resources
- [x] 2.4 Add cache-aware collection (use existing cache with short TTL to avoid repeated SSH calls)

## 3. Dashboard Template
- [x] 3.1 Create `dashboard.html` Jinja2 template with status overview, containers, services, and resources sections
- [x] 3.2 Add auto-refresh JavaScript that polls `/api/status` on a configurable interval
- [x] 3.3 Include basic CSS styling (inline or minimal static file)

## 4. CLI Integration
- [x] 4.1 Add `cloud-map web` command to `cli.py` with `--host`, `--port`, and `--refresh` options
- [x] 4.2 Wire the command to start uvicorn with the FastAPI app

## 5. Documentation & Testing
- [x] 5.1 Update `README.md` with web dashboard usage instructions
- [x] 5.2 Add unit tests for API endpoint responses
- [x] 5.3 Add unit test for the `web` CLI command startup
