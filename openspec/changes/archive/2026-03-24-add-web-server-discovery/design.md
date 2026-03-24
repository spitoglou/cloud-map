## Context
Cloud Map already SSHes into servers to collect Docker, systemd, and resource data.
Adding nginx/httpd config parsing follows the same pattern: run a remote command,
parse the output, map to domain objects.

## Goals / Non-Goals
- Goals:
  - Auto-detect nginx and Apache httpd on reachable servers by checking for config
    directories — works out of the box with zero inventory changes
  - Extract domains from nginx `server_name` directives and Apache `ServerName`/
    `ServerAlias` directives
  - Support both nginx and Apache httpd on the same server
  - Follow includes/conf.d patterns to find all virtual host files
  - Show domains in CLI table and web dashboard
  - Allow inventory overrides for custom config paths or to disable discovery
- Non-Goals:
  - Validating DNS resolution or SSL certificate status (future work)
  - Modifying web server configurations
  - Supporting other web servers (Caddy, Traefik, etc.) in this change

## Decisions
- **Auto-detection by default**: On each reachable server, check if standard config
  directories exist (`/etc/nginx/`, `/etc/httpd/`, `/etc/apache2/`). If found, parse
  them. This means the feature works immediately without any inventory changes.
  Alternative: opt-in via inventory — rejected because it adds friction and the
  detection check is cheap (a single `test -d` command).
- **Inventory override (optional)**: Users can add `webservers` to a server entry to
  specify custom paths or disable discovery:
  ```yaml
  # Custom path
  webservers:
    - type: nginx
      config_path: /opt/nginx/conf

  # Disable auto-detection
  webservers: false
  ```
- **Remote parsing via shell commands**: Use `grep -rh` over config directories to
  extract `server_name` (nginx) and `ServerName`/`ServerAlias` (httpd) lines. This
  avoids transferring full config files and works across distros.
- **Config paths**: Default detection paths:
  - nginx: `/etc/nginx/`
  - httpd: `/etc/httpd/` and `/etc/apache2/` (both checked)
- **Data model**: New `DomainInfo` dataclass with fields: domain, web_server_type,
  config_file (where found). Attached to `ServerStatus` as an optional list.

## Risks / Trade-offs
- **Extra SSH commands**: Auto-detection adds 2-3 lightweight `test -d` commands per
  server. Mitigation: these are fast and run concurrently with other collection.
- **Permission issues**: Reading config files requires appropriate SSH user permissions.
  Mitigation: graceful fallback with an error message if permission denied.
- **Varied config layouts**: Distros differ in Apache config paths (`/etc/httpd` vs
  `/etc/apache2`). Mitigation: check both default paths; allow override via inventory.

## Open Questions
- None currently.
