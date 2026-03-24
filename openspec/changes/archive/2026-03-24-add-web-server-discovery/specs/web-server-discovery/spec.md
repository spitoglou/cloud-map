## ADDED Requirements

### Requirement: Auto-Detection of Web Servers
The system SHALL automatically detect nginx and Apache httpd on each reachable server
by checking for the existence of standard configuration directories. No inventory
configuration is required for auto-detection.

#### Scenario: Nginx auto-detected
- **WHEN** a server is reachable
- **AND** `/etc/nginx/` exists on the server
- **THEN** the system parses nginx configs for domain information

#### Scenario: Apache auto-detected
- **WHEN** a server is reachable
- **AND** `/etc/httpd/` or `/etc/apache2/` exists on the server
- **THEN** the system parses Apache configs for domain information

#### Scenario: No web server found
- **WHEN** a server is reachable
- **AND** no web server config directories exist
- **THEN** the system skips domain discovery for that server without error

#### Scenario: Discovery disabled via inventory
- **WHEN** a server has `webservers: false` in the inventory
- **THEN** the system skips auto-detection for that server

### Requirement: Nginx Domain Extraction
The system SHALL extract configured domains from nginx server blocks by parsing
`server_name` directives across nginx configuration files on remote servers via SSH.

#### Scenario: Nginx domains found
- **WHEN** nginx config files contain `server_name` directives
- **THEN** the system returns a list of domains with their source config files

#### Scenario: Custom nginx config path
- **WHEN** a server has `webservers: [{type: nginx, config_path: /opt/nginx/conf}]`
- **THEN** the system searches the specified path instead of the default

### Requirement: Apache Httpd Domain Extraction
The system SHALL extract configured domains from Apache httpd virtual hosts by parsing
`ServerName` and `ServerAlias` directives across httpd configuration files via SSH.

#### Scenario: Apache domains found
- **WHEN** Apache config files contain `ServerName` or `ServerAlias` directives
- **THEN** the system returns a list of domains with their source config files

#### Scenario: Both default Apache paths checked
- **WHEN** auto-detection is active and no custom config_path is set
- **THEN** the system checks both `/etc/httpd/` and `/etc/apache2/`

### Requirement: Domains CLI Command
The system SHALL provide a `cloud-map domains` command that displays discovered
domains in a table grouped by server, showing domain name, web server type, and
config file path.

#### Scenario: Display domains table
- **WHEN** the user runs `cloud-map domains`
- **THEN** discovered domains are shown in a Rich table grouped by server

#### Scenario: No domains discovered
- **WHEN** no web servers are detected on any server
- **THEN** the command displays a message indicating no domains were found

### Requirement: Domains in Web Dashboard
The system SHALL display discovered domains in the web monitoring dashboard as a
dedicated "Domains" tab with collapsible server groups.

#### Scenario: Domains tab shows discovered domains
- **WHEN** the user opens the Domains tab in the dashboard
- **THEN** domains are listed grouped by server with web server type and config file
