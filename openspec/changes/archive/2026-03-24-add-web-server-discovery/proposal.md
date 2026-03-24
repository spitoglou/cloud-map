# Change: Add Web Server Configuration Discovery

## Why
Operations teams need visibility into which domains are configured across their fleet
without manually SSH-ing into each server to inspect nginx/httpd configs. This is
especially useful for auditing, migration planning, and catching stale or misconfigured
virtual hosts.

## What Changes
- Add a new `src/cloud_map/webserver.py` module that SSHes into servers, auto-detects
  nginx and Apache httpd by checking for config directories, and parses out configured
  server names / domains
- Auto-detection is enabled by default for all reachable servers — no inventory changes
  required. An optional `webservers` inventory field allows overriding config paths or
  disabling discovery per server (`webservers: false`)
- Expose discovered domains in the CLI via a new `cloud-map domains` command
- Expose discovered domains in the web dashboard as a new "Domains" tab
- Include domain data in the JSON API (`/api/status`) and state cache
- Add a new `web-server-discovery` capability spec

## Impact
- Affected specs: new `web-server-discovery`, modified `server-connectivity` (optional inventory override), modified `web-dashboard` (new tab), modified `state-cache` (new data)
- Affected code: `models.py`, `config.py`, `collector.py`, `cache.py`, `web.py`, `cli.py`, `display.py`, `dashboard.html`, new `webserver.py`
