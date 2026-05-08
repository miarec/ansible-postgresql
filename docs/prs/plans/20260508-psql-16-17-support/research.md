# Research — PostgreSQL 16 & 17 Support Exploration

## Role Architecture Recap
- Entry point: `tasks/main.yml` loads OS-specific vars (`vars/Debian.yml`, `vars/RedHat.yml`, etc.) followed by version-specific overrides (`vars/postgresql_<version>.yml`), then orchestrates install, extensions, configuration, and verification tasks.
- Debian/Ubuntu installs (`install_apt.yml`) rely on `postgresql_version` to name packages (`postgresql-<version>`, `postgresql-client-<version>`, etc.) and assume PGDG repository availability controlled by `postgresql_apt_repository`.
- RHEL-family installs (`install_rhel.yml`, `install_fedora.yml`) compute package names via `postgresql_version_terse`; service names use `postgresql-<version>` conventions as defined in `vars/RedHat.yml`.
- Configuration templates live under `templates/postgresql.conf-<version>.j2`. Versions 9.1 through 15 exist; new versions will follow the same naming convention.

## Testing & CI Landscape
- Molecule default scenario (`molecule/default/molecule.yml`) parameterizes distro (`MOLECULE_DISTRO`) and PostgreSQL version (`MOLECULE_POSTGRESQL_VERSION`), defaulting to 15; converge playbook sets `postgresql_version` accordingly.
- TLS scenario (`molecule/tls/`) mirrors the structure with dedicated playbooks/tests; currently only versions 12 and 15 are exercised.
- GitHub Actions workflow (`.github/workflows/ci.yml`) executes Molecule tests across matrix `{ubuntu2204, ubuntu2404, rockylinux9, rhel9} × {12,13,14,15}` for the default scenario and `{12,15}` for TLS.
- Testinfra validations (`molecule/default/tests/test_defaults.py`) assert directory, file, service, socket health; logic already branches on distro because service name differs (`postgresql` vs. `postgresql-<version>`).

## Configuration & Defaults
- `defaults/main.yml` sets `postgresql_version: 15`, builds `postgresql_version_terse`, and contains large map `postgresql_postgis_release_compatibility` (last entries up to version 15).
- `vars/postgresql_15.yml` only overrides `postgresql_recovery_prefetch`. Earlier versions have similar minimal overrides.
- PGDG repository URLs derive from `postgresql_version` (APT/DNF/YUM baseurls). No hard-coded version lists but caution required for validations and docs.

## Known Constraints & Considerations
- PostGIS compatibility data must be extended to 16/17; if upstream packaging lags, role should fail early or allow user-specified overrides.
- TLS scenario uses environment-provided version variable; ensure certificates and playbooks respect new directory structures.
- GitHub Actions runtime will increase with additional versions; monitor for step timeouts (6-hour limit) and consider staggering if necessary.
- No evidence of existing tests that assert the default value of `postgresql_version`; plan to rely on Molecule runs plus targeted assertions.

## Patterns to Reuse
- Version-specific templates named `postgresql.conf-<major>.j2` seeded from PostgreSQL sample configs with role overrides appended.
- Version guard logic implemented via maps (e.g., PostGIS compatibility) rather than conditionals scattered through tasks.
- Molecule scenario parameterization via environment variables; avoid duplicating configuration in GitHub workflows beyond matrix expansion.

## Patterns Not Applicable / To Avoid
- Avoid copying legacy version gating logic that enumerates explicit version lists inside tasks; prefer deriving compatibility from data maps to reduce drift.
- Do not create wrapper tasks for repository setup per version; existing tasks already rely on computed base URLs.

## Outstanding Questions
- None identified during research; spec confirms direction.

## Useful Links
- PostgreSQL 16 sample config: https://raw.githubusercontent.com/postgres/postgres/REL_16_STABLE/src/backend/utils/misc/postgresql.conf.sample
- PostgreSQL 17 sample config: https://raw.githubusercontent.com/postgres/postgres/REL_17_STABLE/src/backend/utils/misc/postgresql.conf.sample
- PostGIS compatibility matrix: https://trac.osgeo.org/postgis/wiki/UsersWikiPostgreSQLPostGIS
