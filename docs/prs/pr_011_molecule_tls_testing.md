# Pull Request Description Template

## Summary

Add molecule testing scenario for PostgreSQL TLS/SSL configuration, similar to PR #11 in ansible-role-redis.

---

## Purpose

- **Test TLS functionality**: Verify the role's SSL support works correctly with certificate-based connections
- **Improve test coverage**: Add comprehensive tests for TLS connections including positive and negative test cases
- **Add query verification**: Add basic PostgreSQL connectivity test (`SELECT 1`) to default molecule scenario

---

## Testing

How did you verify it works?

* [x] Added/updated tests
* [x] Ran `uv run ansible-lint`
* [x] Ran `uv run molecule test -s tls` (passed locally)
* [x] Ran `uv run molecule test -s default` (passed locally)
* Notes: New `molecule/tls` scenario with 8 TestInfra tests covering service status, port listening, SSL configuration, TLS connections with various sslmodes, and non-TLS rejection

---

## Related Issues

N/A - Feature improvement PR

---

## Changes

Brief list of main changes:

* **New molecule/tls scenario**: Complete TLS testing with certificate generation in prepare.yml
* **Certificate generation**: CA, server, client, and invalid client certificates for comprehensive testing
* **TestInfra tests**: 8 tests verifying TLS functionality and security:
  - Service running and enabled
  - Port 5432 listening
  - SSL enabled in postgresql.conf
  - TLS connection with `sslmode=require`
  - TLS connection with CA verification (`sslmode=verify-ca`)
  - TLS connection with client certificates
  - SSL info verification (`SHOW ssl`)
  - Non-TLS connections rejected (negative test)
* **Default scenario enhancement**: Added `test_postgresql_query` to verify basic connectivity with `SELECT 1`
* **CI workflow**: Added `test-tls` job testing all 4 distros with PostgreSQL 12 and 15

---

## Notes for Reviewers

- The prepare.yml creates postgres user/group before certificates so the server key can have proper group ownership (0640) for PostgreSQL to read
- Tests use `hostssl` entries in pg_hba.conf with `trust` auth method for testing simplicity
- Invalid client certificate is self-signed (not CA-signed) to test that only CA-signed certs are accepted
- Tests verify both positive cases (valid TLS works) and negative cases (non-TLS fails with hostssl-only config)

---

## Docs

* [x] N/A - TLS configuration is already documented in defaults/main.yml variables
