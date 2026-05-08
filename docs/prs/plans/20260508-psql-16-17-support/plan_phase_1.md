# Phase 1 — Role Defaults & Version Artifacts

## Goal
Introduce PostgreSQL 16 and 17 support within the core Ansible role while promoting PostgreSQL 17 to the default version, ensuring configuration templates and version-aware variables remain accurate without yet modifying broader test or documentation layers.

## Scope
- Role defaults, vars, and templates required to recognize and configure PostgreSQL versions 16 and 17.
- No documentation, Molecule matrix, or CI workflow changes (handled in later phases).

## Tasks
- [x] Update `defaults/main.yml` to set `postgresql_version: 17` and expand any mappings (e.g., `postgresql_postgis_release_compatibility`) to include 16 and 17; validate derived variables like `postgresql_version_terse`.
- [x] Add version-specific overrides in `vars/postgresql_16.yml` and `vars/postgresql_17.yml` if new defaults (e.g., `postgresql_recovery_prefetch`) diverge from prior versions; otherwise document intentional reuse.
- [x] Create `templates/postgresql.conf-16.j2` and `templates/postgresql.conf-17.j2` based on upstream configs, pruning parameters removed in 16/17 (e.g., `vacuum_defer_cleanup_age`, `promote_trigger_file`).
- [x] Review tasks (e.g., `install_apt.yml`, `install_rhel.yml`, extensions/FDW tasks) for hard-coded version lists; refactor to rely on expanded mappings or add 16/17 explicitly where needed.
- [x] Add defensive Ansible assertions in `tasks/main.yml` (or a dedicated sanity task) confirming the requested `postgresql_version` has matching template and vars entries to provide early failure.
- [x] Run linting (`uv run ansible-lint`) to ensure playbook style compliance.
- [x] Execute a Molecule converge (Ubuntu 24.04, PostgreSQL 17) to verify template rendering and service startup; capture logs for future phases.

## Acceptance Criteria
- Role default version is 17, and both 16 and 17 can be provisioned without errors across Debian and RHEL task paths.
- Version-specific templates and vars exist (or are explicitly documented unnecessary) for 16 and 17, with assertions guarding unsupported versions.
- `uv run ansible-lint` succeeds, and a Molecule converge for Ubuntu 24.04 + PostgreSQL 17 completes without failure.

## Edge Cases to Address
- PGDG repositories may not publish PostgreSQL 16/17 packages for a given distro architecture; surface a clear failure via assertions instead of silent fallback.
- PostGIS compatibility mapping might be missing entries; ensure `postgresql_postgis_release_compatibility` raises an informative error when a version lacks mapping.
- Upstream sample configs could introduce parameters that aren’t templated; confirm templates either expose sane defaults or document why they are omitted.

## Tests (Must be implemented in this phase)
- Manual Molecule command: `MOLECULE_DISTRO=ubuntu2404 MOLECULE_POSTGRESQL_VERSION=17 uv run --python 3.12 molecule converge`
- Lint: `uv run --python 3.12 ansible-lint`
- Verify template syntax via `ansible-playbook --syntax-check` if issues suspected.

## Verification Steps
- Run `uv run ansible-lint`; ensure exit status 0.
- Execute the Molecule converge command above; confirm service `postgresql` is active and configuration files rendered with version 17 paths.
- Optionally inspect rendered `postgresql.conf` to confirm version-specific settings (e.g., `recovery_prefetch`) align with expectations.
