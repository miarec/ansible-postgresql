# Plan — PostgreSQL 16 & 17 Support

## Summary
MiaRec’s `postgresql` role already provisions PostgreSQL 12–15 across Ubuntu and RHEL-family distributions, but customers now require parity for versions 16 and 17 alongside a default that tracks the latest PG release. This plan delivers that capability by extending version-aware configuration, installation logic, and documentation while preserving existing behavior for older deployments.

Implementation happens in three phases. Phase 1 updates the role’s defaults, version-specific templates, and guardrails so PostgreSQL 16/17 behave like first-class citizens. Phase 2 broadens automated coverage—Molecule scenarios and GitHub Actions matrices—ensuring CI validates every supported distro/version combination, including TLS scenarios. Phase 3 closes the loop with documentation, metadata updates, and final verifications so consumers immediately understand the new support story.

Each phase has its own acceptance criteria and test plan, executed sequentially. Linting and targeted Molecule runs provide quick feedback early, while expanded test matrices in Phase 2 and Phase 3 offer confidence before release. No new dependencies or tech-stack shifts are anticipated, keeping risk low.

## 0. References

### 0.1 Specification (Always Read)
- [spec.md](spec.md) — Detailed requirements, UX expectations, acceptance criteria.

### 0.2 Phase Plans (Read Relevant Phase)
- [plan_phase_1.md](plan_phase_1.md) — Role defaults & version artifacts.
- [plan_phase_2.md](plan_phase_2.md) — Test matrix & CI expansion.
- [plan_phase_3.md](plan_phase_3.md) — Documentation, metadata & final verification.

### 0.3 Research (Read to Understand Codebase)
- [research.md](research.md) — Code exploration notes, existing patterns, CI constraints.

### 0.4 Source Document (Read if Requested)
- [idea.md](idea.md) — Original concept and approach outline.

## 1. Software Design Document (SDD)

### 1.1 Goals & Constraints
- Add PostgreSQL 16 and 17 support without regressing behavior for versions 12–15.
- Promote PostgreSQL 17 to the default `postgresql_version`.
- Keep implementation additive; avoid breaking existing playbooks or requiring new dependencies.
- Maintain CI runtime within GitHub Actions limits (~6 hours per workflow); be ready to shard if expansion causes issues.

### 1.2 Proposed Architecture (High-level)
- Continue leveraging data-driven configuration: version-specific values reside in YAML maps and templates keyed by major version.
- Installation logic remains split by package manager (APT/YUM/DNF); new versions integrate via `postgresql_version` variables.
- Testing infrastructure (Molecule + GitHub Actions) uses environment-driven matrices; expand matrices to include new versions while reusing scenario logic.

### 1.3 Data Model & Types (Signatures, not full code)
- `postgresql_postgis_release_compatibility` (YAML map): `major_version (int)` → `postgis_version (string)`. Extend with entries for `16` and `17` using PGDG-published PostGIS versions (confirm at implementation time).
- `vars/postgresql_<major>.yml`: YAML documents overriding version-specific settings (e.g., `postgresql_recovery_prefetch: "off"`). If no overrides required, create minimal file with comment for parity.
- Assertions task (Ansible): expects `postgresql_version` (string/number) and checks presence in `postgresql_supported_versions` list derived from templates directory.

### 1.4 Module / File-level Design
- `defaults/main.yml`: Update default version, extend compatibility maps, ensure repository URLs work generically. Document format: YAML key/value pairs.
- `vars/postgresql_16.yml`, `vars/postgresql_17.yml`: Minimal overrides; maintain structure consistent with existing version files.
- `templates/postgresql.conf-16.j2`, `templates/postgresql.conf-17.j2`: Jinja2 templates cloned from upstream sample configs with MiaRec overrides appended (e.g., `{{ postgresql_listen_addresses }}`).
- `tasks/main.yml`: Insert assertion block verifying requested version has matching template/vars entries (use `assert` module).
- `molecule/default/molecule.yml`, `molecule/tls/molecule.yml`: Update env defaults and documentation comments to include new versions.
- `.github/workflows/ci.yml`: Adjust strategy matrices to cover 12–17 (default) and 12,15,16,17 (TLS).
- `README.md`, `meta/main.yml`: Update compatibility tables and supported versions metadata.

### 1.5 Interfaces & Contracts
- Role variable contract: `postgresql_version` accepts strings or integers representing major versions in `{12,13,14,15,16,17}`. Consumers expect the role to install matching packages and configure services accordingly.
- Molecule environment contract: `MOLECULE_POSTGRESQL_VERSION` must accept `"12"` through `"17"`. Scenario playbooks consume this via `lookup('env', 'POSTGRESQL_VERSION')`.
- CI matrix contract: Workflow expects environment variables per matrix axis; maintain naming to prevent breakage in GitHub Actions YAML.

### 1.6 Key Algorithms (Pseudo-code)
```
# tasks/assert_supported_version.yml
- name: Gather supported template versions
  set_fact:
    postgresql_supported_versions: "{{ lookup('fileglob', 'templates/postgresql.conf-*.j2') | map('basename') | map('regex_replace', 'postgresql.conf-(\\d+)\\.j2', '\\1') }}"

- name: Ensure requested version is supported
  assert:
    that:
      - (postgresql_version | string) in postgresql_supported_versions
    fail_msg: "postgresql_version {{ postgresql_version }} lacks template/vars definitions. Supported: {{ postgresql_supported_versions }}"
```

```
# Molecule matrix snippet (conceptual)
for distro in [ubuntu2204, ubuntu2404, rockylinux9, rhel9]:
  for pg_version in [12, 13, 14, 15, 16, 17]:
    run_molecule_test(scenario="default", env={MOLECULE_DISTRO: distro, MOLECULE_POSTGRESQL_VERSION: pg_version})
```

### 1.7 Testing Architecture
- Phase 1: `uv run ansible-lint`, targeted Molecule converge (`ubuntu2404` + `PG17`) to verify templates and tasks.
- Phase 2: Molecule full `test` for representative combos (Ubuntu 24.04 + PG16, Rocky Linux 9 + PG17 TLS) plus GitHub Actions matrix shape validation.
- Phase 3: Documentation-focused but rerun Molecule scenarios (full or sampled) to confirm final state; capture outputs for Outcomes.
- No additional fixtures; existing Testinfra tests adapt by referencing version environment variable. If expansions require new fixtures, prefer function-scoped to reduce cross-test bleed.

### 1.8 Edge Cases
- PGDG mirrors may lag for certain architectures; assertions should fail fast with actionable messages.
- PostGIS compatibility might trail new PostgreSQL releases; provide clear guidance for manual override or deferral.
- Increased CI matrix size could exceed workflow runtime; be prepared to shard or reduce frequency if observed.
- TLS scenario may expose certificate generation issues for new versions; ensure failure surfaces with logs.

### 1.9 Observability & Ops (if relevant)
- Leverage existing Ansible logging; no new telemetry requirements.
- Encourage capturing Molecule logs for new versions to assist troubleshooting; store summarized findings in Surprises & Discoveries if anomalies appear.

## Edge Cases (Cross-cutting)
- Ensure templates for 16/17 include any new parameters introduced upstream (e.g., `event_triggers` defaults in v17).
- Validate repository URLs remain correct when distribution codename changes (e.g., Ubuntu 24.04 `noble` in apt repo string).
- Confirm service enablement semantics on systemd remain intact—particularly the `postgresql-<version>` units on RHEL-derived systems.
- Document how to proceed if PGDG delays PostGIS packages; include fallback instructions in README or spec deferral notes.

## 2. Phase Breakdown (Approval checkpoint)

### Phase 1. Role Defaults & Version Artifacts (pending)
- Goal: Introduce PostgreSQL 16/17 support in core role config, promoting version 17 as default.
- Acceptance criteria: Default updated to 17, assertions guarding unsupported versions, Molecule converge (Ubuntu 24.04 + PG17) and lint pass.
- Tests: `uv run ansible-lint`; `MOLECULE_DISTRO=ubuntu2404 MOLECULE_POSTGRESQL_VERSION=17 uv run molecule converge`.
- Plan doc: [plan_phase_1.md](plan_phase_1.md)

### Phase 2. Test Matrix & CI Expansion (pending)
- Goal: Expand Molecule scenarios and CI matrices to exercise PostgreSQL 12–17 across supported distros and TLS.
- Acceptance criteria: Molecule default and TLS scenarios succeed for representative PG16/PG17 runs; GitHub Actions matrices updated with new versions.
- Tests: `MOLECULE_DISTRO=ubuntu2404 MOLECULE_POSTGRESQL_VERSION=16 uv run molecule test`; `MOLECULE_DISTRO=rockylinux9 MOLECULE_POSTGRESQL_VERSION=17 uv run molecule test -s tls`.
- Plan doc: [plan_phase_2.md](plan_phase_2.md)

### Phase 3. Documentation, Metadata & Final Verification (pending)
- Goal: Refresh documentation/metadata and complete regression verification.
- Acceptance criteria: README and metadata highlight 16/17 support and default change; Molecule regressions succeed for representative combinations.
- Tests: `uv run molecule test`; `uv run molecule test -s tls` (with PG17).
- Plan doc: [plan_phase_3.md](plan_phase_3.md)

## 3. Living Sections (Mandatory)

> **Instructions for maintainers:**
>
> This plan is a living document. As you make key design decisions, update the plan to record both the decision and the thinking behind it. Record all decisions in the `Decision Log` section.
>
> Maintain the `Progress` section in this plan and in the corresponding phase document. Mark tasks as `[ ]` not started, `[~]` in progress, or `[x]` done.
>
> When you discover optimizer behavior, performance tradeoffs, unexpected bugs, or inverse/unapply semantics that shaped your approach, capture those observations in the `Surprises & Discoveries` section with short evidence snippets (test output is ideal).
>
> If you change course mid-implementation, document why in the `Decision Log` and reflect the implications in `Progress`. Plans are guides for the next contributor as much as checklists for you.
>
> At completion of a major task or the full plan, write an `Outcomes & Retrospective` entry summarizing what was achieved, what remains, and lessons learned.
>
> **This document must describe not just the what but the why for almost everything.**

### 3.1 Progress
- [x] Phase 1 — Role Defaults & Version Artifacts
- [x] Phase 2 — Test Matrix & CI Expansion
- [x] Phase 3 — Documentation, Metadata & Final Verification

### 3.2 Decision Log
- **PostGIS compatibility mapping** — Map PostgreSQL 16 & 17 to PostGIS 3.6 packages shipped by PGDG.
  - Date: 2026-05-08
  - Rationale: Verified apt repository lists `postgresql-16/17-postgis-3` at version 3.6.x; ensures extension installs succeed.
- **Template parameter pruning** — Removed legacy settings (`db_user_namespace`, `old_snapshot_threshold`, `vacuum_defer_cleanup_age`, `promote_trigger_file`) from PostgreSQL 17 template and aligned 16 template with upstream removals.
  - Date: 2026-05-08
  - Rationale: PostgreSQL 17 rejects these parameters; pruning keeps services startable out of the box.
- **CI matrix expansion** — Extended Molecule GitHub workflow to test PostgreSQL 12–17 (default) and 12, 15, 16, 17 (TLS); scenario defaults now align with PostgreSQL 17.
  - Date: 2026-05-08
  - Rationale: Ensures continuous integration covers the newly supported versions across all distros and scenarios.

### 3.3 Surprises & Discoveries
- **Molecule converge block resolved** — Initial converge failed because Docker daemon was unavailable; reran successfully once Docker access granted.
- **ansible-lint python pin** — Needed `uv run --python 3.12 ansible-lint` because ansible-core packaged with Python 3.14 is incompatible (<2.20.0).
- **PostgreSQL 17 config changes** — PG17 removed several configuration GUCs (e.g., `db_user_namespace`, `promote_trigger_file`); templates must exclude them to allow cluster start.
- **TLS scenario runtime** — Rockylinux9 TLS run with PostgreSQL 17 completed in ~7.5 minutes; monitor CI duration post-matrix expansion.
- **No changelog maintained** — Repository lacks a changelog; documented decision to leave this phase task as N/A.

### 3.4 Outcomes & Retrospective
(To be filled after completion)
