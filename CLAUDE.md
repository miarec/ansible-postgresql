This file provides guidance to coding agent when working with code in this repository.

## Overview

This is an Ansible role (`miarec.postgresql`) for installing and configuring PostgreSQL on Ubuntu (22.04, 24.04), Rocky Linux 9, and RHEL 9. It supports PostgreSQL versions 12-15.

## Testing Commands

Run molecule tests with specific distribution and PostgreSQL version:
```bash
# Run tests (defaults to ubuntu2404 and PostgreSQL 12)
uv run molecule test

# Run with specific distro and version
MOLECULE_DISTRO=rockylinux9 MOLECULE_POSTGRESQL_VERSION=15 uv run molecule test

# Individual molecule phases
uv run molecule create
uv run molecule converge
uv run molecule verify
uv run molecule destroy

# Run ansible-lint
uv run ansible-lint
```

Valid `MOLECULE_DISTRO` values: `ubuntu2204`, `ubuntu2404`, `rockylinux9`, `rhel9`

## Role Architecture

**Entry point:** `tasks/main.yml` orchestrates the full workflow:
1. Load OS-specific variables from `vars/` (RedHat vs Debian family)
2. Load PostgreSQL version-specific variables from `vars/postgresql_*.yml`
3. Install PostgreSQL (platform-specific: `install_apt.yml`, `install_rhel.yml`, `install_fedora.yml`)
4. Install extensions and foreign data wrappers
5. Configure PostgreSQL (`configure.yml` - generates `postgresql.conf`, `pg_hba.conf`, `pg_ident.conf`)
6. Create users, databases, schemas, and apply privileges

**Key configuration files generated:**
- `postgresql.conf` from `templates/postgresql.conf.j2`
- `pg_hba.conf` from `templates/pg_hba.conf.j2`
- `pg_ident.conf` from `templates/pg_ident.conf.j2`

**Variable precedence:**
- `defaults/main.yml` - extensive PostgreSQL configuration defaults (600+ lines)
- `vars/{os_family}.yml` - OS-specific paths and package names
- `vars/postgresql_{version}.yml` - version-specific settings

## Key Variables

- `postgresql_version`: Target PostgreSQL version (12, 13, 14, 15)
- `postgresql_databases`: List of databases to create
- `postgresql_users`: List of users to create
- `postgresql_database_schemas`: List of schemas to create
- `postgresql_pg_hba_custom`: Custom pg_hba.conf entries
- `postgresql_listen_addresses`: Network interfaces to listen on

## Platform Differences

**Debian/Ubuntu:**
- Config directory: `/etc/postgresql/{version}/{cluster_name}/`
- Data directory: `/var/lib/postgresql/{version}/{cluster_name}/`
- Service name: `postgresql`

**RedHat/CentOS/Rocky:**
- Config directory: `/etc/postgresql/{version}/data/` (role creates this structure)
- Data directory: `/var/lib/pgsql/{version}/data/`
- Service name: `postgresql-{version}`
