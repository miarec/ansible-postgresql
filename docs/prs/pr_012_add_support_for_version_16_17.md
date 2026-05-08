# Pull Request Description Template

## 🔍 Summary

- promote PostgreSQL 17 to the default version for the `miarec.postgresql` role
- add first-class support for PostgreSQL 16/17 via version-specific templates, vars, and PostGIS compatibility mappings
- expand Molecule and CI matrices to cover versions 12–17 (default) and 12/15/16/17 (TLS), while documenting the upstream gaps for RHEL-family repos
- refresh documentation and planning artifacts to reflect the new support surface

---

## 🎯 Purpose

Customers need automation coverage for PostgreSQL 16 and 17, and the role should track the latest major release by default. This PR extends version handling, keeps backward compatibility for 12–15, and ensures our CI/test story validates the broader matrix.

---

## 🧪 Testing

How did you verify it works?

* [ ] Added/updated tests
* [ ] Ran `pytest`
* [x] `MOLECULE_DISTRO=ubuntu2204 MOLECULE_POSTGRESQL_VERSION={12,13,14,15,16,17} uv run --python 3.12 molecule test`
* [x] `MOLECULE_DISTRO=ubuntu2404 MOLECULE_POSTGRESQL_VERSION={12,13,14,15,16,17} uv run --python 3.12 molecule test`
* [x] `MOLECULE_DISTRO=rockylinux9 MOLECULE_POSTGRESQL_VERSION={14,15,16,17} uv run --python 3.12 molecule test`
* [x] `MOLECULE_DISTRO=rhel9 MOLECULE_POSTGRESQL_VERSION={14,15,16,17} uv run --python 3.12 molecule test`
* [x] `MOLECULE_DISTRO=ubuntu2204|ubuntu2404 MOLECULE_POSTGRESQL_VERSION={12,15,16,17} uv run --python 3.12 molecule test -s tls`
* [x] `MOLECULE_DISTRO=rockylinux9|rhel9 MOLECULE_POSTGRESQL_VERSION={15,16,17} uv run --python 3.12 molecule test -s tls`

Notes:

- PGDG no longer serves PostgreSQL 12/13 packages for RHEL 9 / Rocky Linux 9; those combinations fail with HTTP 410 when provisioning, so they are excluded from the CI matrix.

---

## 📌 Related Issues

Closes #N/A

---

## 🚀 Changes

Brief list of main changes:

* promote PostgreSQL 17 to the default, extend PostGIS compatibility map, and add guardrails for supported versions
* add `postgresql.conf-16/17` templates and placeholder vars while pruning removed GUCs and aligning configs with upstream samples
* widen Molecule and GitHub Actions matrices (with RHEL9/Rocky9 exclusions for 12/13) and refresh docs/plans to communicate the new support policy

---

## ⚠️ Notes for Reviewers

- RHEL 9 / Rocky Linux 9 cannot install PostgreSQL 12 or 13 from PGDG anymore; CI matrices and README mark these combinations as non-production.
- The new assertion in `tasks/main.yml` fails fast if a caller requests a PostgreSQL major without matching templates/vars.

---

## 📚 Docs

* [x] Updated README compatibility matrix and Molecule usage notes
* [x] Added planning docs under `docs/prs/plans/20260508-psql-16-17-support/`
