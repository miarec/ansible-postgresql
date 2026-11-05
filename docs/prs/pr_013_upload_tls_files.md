# 2026-10-04-upload-tls-files

Moves the TLS file upload into the role, so a renewed certificate restarts only the service that reads it. The role sets permissions only on the files it uploads, and fails the play before it touches `postgresql.conf` when the service user can't read a TLS file.

## 🎯 Problem

The ansible-miarec playbooks deploy several services, often on one host, and upload the TLS files of each service with a shared task in `pre_tasks`. Each play then restarts its service from `post_tasks` when a variable registered by that task reports a change. Registered variables survive across plays, so one changed certificate restarts every service deployed later on the same host, including services that never read the file. The playbooks also depend on a variable name internal to the shared task file.

A TLS file that the `postgres` user can't read used to surface only when the service restarted, after the play had already written `ssl = on`.

---

## 👀 What changes for users

Before, the role expected the TLS files to exist on the host. After, setting `postgresql_ssl_cert_file_src`, `postgresql_ssl_key_file_src`, and `postgresql_ssl_ca_file_src` makes the role copy the files from the Ansible control machine, set root ownership with mode 0644 for certificates and 0640 for private keys readable by the PostgreSQL service group, and restarts PostgreSQL when a file changed. Leaving the variables empty, the default, keeps the previous behavior.

When `postgresql_ssl` is on, the role now also checks, as the service user, that every TLS file in use is readable: the certificate, the key, and the CA, CRL, and DH parameter files when set. The check runs through `runuser`, which applies the user's supplementary groups the way systemd does, so it covers directory traversal, the file mode, and the group membership, for files the role uploaded and files that arrived by other means. A failure names the user and the path and leaves the host untouched.

---

## 💥 Impact

* **Who is affected**: deployments that set the new `*_src` variables, starting with ansible-miarec. Deployments with `postgresql_ssl` on get the readability check; a host where `postgres` can't read a TLS file now fails the play instead of failing the service at its next restart.
* **Who is not affected**: deployments without TLS. The defaults are empty, so no new task runs and no restart is added.
* **Conditions**: `postgresql_ssl` enabled, and for the upload at least one `*_src` variable set.

---

## 🔧 Implementation notes

* The upload runs before the configuration tasks, so the files exist when PostgreSQL reloads with `ssl = on`. PostgreSQL accepts a root-owned key with mode 0640.
* `tasks/tls_upload.yml` sets permissions only on the files it uploads. A missing parent directory is created as `0755 root:root`, regardless of the host's umask, and an existing one is left alone. Pointed at a shared directory such as `/etc/ssl/private`, the role no longer rewrites the directory's group and mode, which used to cut other services off from their own keys. A file that is already on the host, because its `*_src` variable is empty, is left as is.
* `tasks/tls_verify.yml` runs `test -r` on every TLS file in use as `postgresql_service_user`. It runs after the upload and before `configure.yml`.
* The `tls` Molecule scenario generates the test CA and certificates on the control machine, in the Molecule ephemeral directory, with a play on `localhost`. Nothing in prepare writes to `/etc/postgresql/tls`. The role creates that directory and uploads the server certificate, the key, and the CA certificate during converge, the same way the production playbooks do. The CA private key never reaches the target, and verify asserts that. The client files that the tests pass to `psql` are a fixture in `/root/tls-client`.
* The verify tests check that the uploaded key is `root:postgres` 0640, the certificates 0644, the directory `0755 root`, that `postgres` can read the key through `runuser`, and that the server rejects a client certificate the CA didn't sign.
* `.yamllint` mirrors the `yaml[...]` skips in `.ansible-lint` and sets the values ansible-lint requires, so `uv run yamllint .` and `uv run ansible-lint` agree.
