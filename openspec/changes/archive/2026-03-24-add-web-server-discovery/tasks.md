## 1. Data Model
- [x] 1.1 Add `DomainInfo` dataclass to `models.py` (domain, web_server_type, config_file)
- [x] 1.2 Add `WebServerConfig` to `models.py` (type, config_path)
- [x] 1.3 Add optional `webservers` field to `ServerConfig` (list, False, or None for auto-detect)
- [x] 1.4 Add optional `domains` list to `ServerStatus`

## 2. Inventory Configuration
- [x] 2.1 Update `config.py` to parse optional `webservers` entries (list of overrides, `false`, or absent)

## 3. Web Server Parser Module
- [x] 3.1 Create `src/cloud_map/webserver.py`
- [x] 3.2 Implement auto-detection: check `/etc/nginx/`, `/etc/httpd/`, `/etc/apache2/` via `test -d`
- [x] 3.3 Implement nginx domain extraction via SSH (`server_name` directives)
- [x] 3.4 Implement Apache httpd domain extraction via SSH (`ServerName`/`ServerAlias`)
- [x] 3.5 Handle permission errors, missing web servers, and `webservers: false` gracefully

## 4. Integration
- [x] 4.1 Update `collector.py` to call web server discovery for reachable servers
- [x] 4.2 Update `cache.py` to serialize/deserialize domain data
- [x] 4.3 Update `web.py` API serialization to include domains

## 5. CLI
- [x] 5.1 Add `cloud-map domains` command to `cli.py`
- [x] 5.2 Add `display_domains_table` to `display.py`
- [x] 5.3 Add `--pdf` support for domains command

## 6. Web Dashboard
- [x] 6.1 Add "Domains" tab to `dashboard.html`
- [x] 6.2 Render domains grouped by server with collapsible sections

## 7. Documentation & Testing
- [x] 7.1 Update `README.md` with domains command and inventory config
- [x] 7.2 Update `docs/capabilities.md` and `docs/architecture.md`
- [x] 7.3 Add unit tests for auto-detection logic
- [x] 7.4 Add unit tests for nginx parsing
- [x] 7.5 Add unit tests for Apache httpd parsing
- [x] 7.6 Add web dashboard test for domains data
