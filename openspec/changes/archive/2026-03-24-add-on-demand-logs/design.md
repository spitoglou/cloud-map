## Context
Cloud Map already has SSH connections to all servers and knows the names and types
of all services. Fetching logs is a natural extension — one SSH command per request.

## Goals / Non-Goals
- Goals:
  - Fetch recent logs for any Docker container or systemd service by name
  - CLI command for quick terminal access to logs
  - Web dashboard integration for point-and-click log viewing
  - Configurable tail length (number of lines)
  - CLI `--follow` flag for live tailing
- Non-Goals:
  - Log aggregation or storage (logs are fetched live, not persisted)
  - Full-text search across logs
  - Streaming logs via WebSocket in the web UI (future work)
  - Log rotation management

## Decisions
- **SSH commands**: Use `docker logs --tail <N> <container>` for Docker and
  `journalctl -u <service> -n <N> --no-pager` for systemd. Simple, standard,
  no extra dependencies on the server side.
- **API design**: `GET /api/logs/{server}/{service}?lines=100` returns plain text.
  Using plain text rather than JSON avoids escaping issues and is more natural for
  log content. The response includes a `Content-Type: text/plain` header.
- **Web UI**: A modal/panel that opens when clicking a service row in the Containers
  or Services tab. Fetches logs via the API and displays in a monospace pre-formatted
  block. Includes a line count selector and a refresh button.
- **No caching**: Logs are always fetched live — they change constantly and caching
  would defeat the purpose. Each request opens one short-lived SSH command.
- **CLI `--follow`**: Uses `docker logs -f` or `journalctl -f` with streaming stdout.
  Only available in CLI, not web (would need WebSocket).

## Risks / Trade-offs
- **Large log output**: Fetching too many lines could be slow or consume memory.
  Mitigation: default to 100 lines, cap at 10000 via validation.
- **Permission issues**: Some containers or services may require elevated privileges
  to read logs. Mitigation: return the error message from the SSH command.
- **Server/service name resolution**: The API needs to map names back to
  `ServerConfig` objects. Mitigation: look up by `server.name` from the inventory.

## Open Questions
- None currently.
