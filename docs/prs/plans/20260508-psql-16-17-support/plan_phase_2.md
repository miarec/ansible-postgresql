# Phase 2 — Test Matrix & CI Expansion

## Goal
Extend automated coverage to validate PostgreSQL versions 12–17 across supported distributions in both Molecule default and TLS scenarios, and ensure GitHub Actions matrices reflect the broader support scope.

## Scope
- Molecule scenario definitions (`molecule/default`, `molecule/tls`) and associated tests.
- GitHub Actions workflow matrices.
- No README or metadata updates (reserved for Phase 3).

## Tasks
- [x] Update `molecule/default/molecule.yml` to widen `MOLECULE_POSTGRESQL_VERSION` defaults and document accepted values; ensure the scenario correctly leverages the environment variable for 16/17.
- [x] Adjust `molecule/default/converge.yml`/tests if any assertions or task guards rely on a capped version list; confirm service name checks remain version-agnostic. *(Reviewed — no changes required.)*
- [x] Modify `molecule/tls/molecule.yml` to mirror the expanded version matrix (12, 15, 16, 17); audit TLS-specific playbooks for assumptions about version-specific paths.
- [x] Refresh `molecule/tls/tests` as needed to handle the broader version range (e.g., socket paths, service names). *(Reviewed — existing assertions already version-agnostic.)*
- [x] Update `.github/workflows/ci.yml` matrices to include PostgreSQL versions 16 and 17 for both default and TLS jobs; verify runtime expectations and note mitigation if needed.
- [x] Re-run targeted Molecule scenarios to validate template rendering and service health for representative distro/version pairs.

## Acceptance Criteria
- Molecule default scenario succeeds for at least PostgreSQL 16 and 17 on a representative distro (Ubuntu 24.04 or equivalent).
- Molecule TLS scenario succeeds for PostgreSQL 16 and 17 on a representative distro (Rocky Linux 9 or equivalent).
- GitHub Actions workflow matrices include versions 12–17 (default) and 12, 15, 16, 17 (TLS) without configuration errors.

## Edge Cases to Address
- Expanded GitHub Actions matrices may exceed job runtime limits; plan mitigations such as matrix partitioning if builds approach the six-hour cap.
- TLS scenario might require additional package dependencies or kernel parameters for newer PostgreSQL releases; ensure playbooks fail with clear messages when prerequisites are missing.
- Molecule tests must accurately detect service names (`postgresql` vs. `postgresql-<version>`); avoid false failures caused by distro-specific naming.

## Tests (Must be implemented in this phase)
- ✅ `MOLECULE_DISTRO=ubuntu2404 MOLECULE_POSTGRESQL_VERSION=16 uv run --python 3.12 molecule test`
- ✅ `MOLECULE_DISTRO=rockylinux9 MOLECULE_POSTGRESQL_VERSION=17 uv run --python 3.12 molecule test -s tls`
- Optional spot checks on additional distro/version combinations if runtime permits.

## Verification Steps
- Execute the commands above; ensure both Molecule scenarios complete without failure and services are reported running.
- Review GitHub Actions workflow syntax via `act` dry-run if available or manual YAML linting; otherwise double-check matrix shape matches expectations.
