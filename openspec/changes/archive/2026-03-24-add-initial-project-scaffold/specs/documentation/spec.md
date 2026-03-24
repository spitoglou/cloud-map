## ADDED Requirements

### Requirement: Documentation Structure
The system SHALL maintain a `docs/` folder containing markdown files that document architecture, capabilities, and usage.

#### Scenario: Required documentation files exist
- **WHEN** the project is set up
- **THEN** the `docs/` folder contains at minimum: `architecture.md`, `capabilities.md`, and `configuration.md`

### Requirement: Architecture Documentation
The `docs/architecture.md` file SHALL describe the overall system design, component relationships, data flow, and key technical decisions.

#### Scenario: Architecture reflects current design
- **WHEN** a developer reads `docs/architecture.md`
- **THEN** they understand the system's module structure, SSH connectivity model, data flow from servers to visualization, and caching strategy

### Requirement: Capabilities Documentation
The `docs/capabilities.md` file SHALL describe each feature of the system, its CLI commands, options, and expected behavior.

#### Scenario: Capabilities list is complete
- **WHEN** a developer reads `docs/capabilities.md`
- **THEN** every CLI command and its flags are documented with usage examples

### Requirement: Mandatory Documentation Updates
All code changes that add, modify, or remove functionality MUST include corresponding updates to the relevant documentation files in `docs/`. This SHALL be enforced via a pre-commit hook that checks whether `docs/` files are included in commits that touch `src/`.

#### Scenario: Code change with documentation update
- **WHEN** a developer modifies files under `src/cloud_map/`
- **THEN** the commit MUST also include changes to at least one file under `docs/`, or the pre-commit hook rejects the commit

#### Scenario: Documentation-only change
- **WHEN** a developer modifies only files under `docs/`
- **THEN** the pre-commit hook allows the commit without requiring `src/` changes

#### Scenario: Non-code change
- **WHEN** a developer modifies only files outside `src/` and `docs/` (e.g., tests, config)
- **THEN** the pre-commit hook allows the commit without requiring `docs/` changes
