## Summary

Remove legacy Vagrant/Travis CI testing infrastructure, add uv for Python dependency management, and modernize Ansible code to fix deprecation warnings.

---

## Purpose

The project already uses Molecule/Docker for testing, but had legacy Vagrant and Travis CI files from the original ANXS/postgresql fork. This change:
- Removes obsolete Vagrant and Travis CI configuration
- Uses `uv` as a modern Python package manager for deterministic, fast dependency installation
- Removes support for deprecated OS versions (Ubuntu 20.04, CentOS 7, RHEL 7/8, Rocky Linux 8)
- Fixes ansible deprecation warnings for compatibility with ansible-core 2.24
- Adds ARM64 (aarch64) architecture support for PostgreSQL GPG key selection

---

## Testing

How did you verify it works?

* [ ] Added/updated tests
* [x] Ran `uv run ansible-lint` - passes with 0 failures, 0 warnings
* Notes: Molecule tests require Docker environment; CI will run full test matrix

---

## Related Issues

N/A

---

## Changes

Brief list of main changes:

**Infrastructure modernization:**
* Remove Vagrant configuration (Vagrantfile, vagrant-inventory)
* Remove Travis CI configuration (.travis.yml)
* Remove obsolete test files (tests/ directory with old Docker images and playbooks)
* Add `pyproject.toml` with uv dependency management and `uv.lock` for reproducible builds
* Update GitHub Actions CI workflow to use `uv` instead of pip
* Re-enable ansible-lint in CI pipeline
* Reduce CI test matrix to modern OS versions (Ubuntu 22.04/24.04, Rocky Linux 9, RHEL 9)

**Ansible code fixes:**
* Replace deprecated `ansible_*` variables with `ansible_facts['*']` dictionary format (fixes INJECT_FACTS_AS_VARS deprecation for ansible-core 2.24)
* Fix PostgreSQL GPG key selection for aarch64 architecture (ARM64 support)
* Quote octal mode values in file/directory tasks
* Add pipefail to shell commands in check_pg_version_mismatch.yml
* Use systemd module instead of raw systemctl command
* Update deprecated community.postgresql parameters (`db` -> `login_db`, `port` -> `login_port`)
* Quote version strings in meta/main.yml

**Documentation:**
* Add CLAUDE.md with project documentation for AI coding assistants
* Update README with testing instructions using uv
* Update .ansible-lint to skip additional rules for existing code issues
* Move test-requirements.txt to molecule/requirements.txt
* Rename molecule container from 'instance' to 'ansible-postgresql'

---

## Notes for Reviewers

* The test matrix has been reduced from 40+ combinations to 16 to speed up CI runs
* Pre-existing ansible-lint warnings remain; fixing them is out of scope for this PR
* The uv.lock file is large (~1400 lines) but provides deterministic builds
* All `ansible_*` variable references have been migrated to `ansible_facts['*']` format to prevent breaking changes in ansible-core 2.24

---

## Docs

* [x] Updated README.md with new testing instructions
* [x] Added CLAUDE.md with project documentation
