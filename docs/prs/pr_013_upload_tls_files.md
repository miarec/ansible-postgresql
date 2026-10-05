# 2026-10-04-upload-tls-files

Moves the TLS file upload into the role, so a renewed certificate restarts only the service that reads it.

## 🎯 Problem

The ansible-miarec playbooks deploy several services, often on one host, and upload the TLS files of each service with a shared task in `pre_tasks`. Each play then restarts its service from `post_tasks` when a variable registered by that task reports a change. Registered variables survive across plays, so one changed certificate restarts every service deployed later on the same host, including services that never read the file. The playbooks also depend on a variable name internal to the shared task file.

---

## 👀 What changes for users

Before, the role expected the TLS files to exist on the host. After, setting `postgresql_ssl_cert_file_src`, `postgresql_ssl_key_file_src`, and `postgresql_ssl_ca_file_src` makes the role copy the files from the Ansible control machine, set root ownership with mode 0644 for certificates and 0640 for private keys readable by the PostgreSQL service group, and restarts PostgreSQL when a file changed. Leaving the variables empty, the default, keeps the previous behavior.

---

## 💥 Impact

* **Who is affected**: deployments that set the new `*_src` variables, starting with ansible-miarec.
* **Who is not affected**: existing deployments. The defaults are empty, so no new task runs and no restart is added.
* **Conditions**: `postgresql_ssl` enabled and at least one `*_src` variable set.

---

## 🔧 Implementation notes

* The upload runs before the configuration tasks, so the files exist when PostgreSQL reloads with `ssl = on`. PostgreSQL accepts a root-owned key with mode 0640.
* The TLS Molecule scenarios move the generated files to the control machine and let the role upload them, so a passing test proves the upload. The fixtures no longer create the service group ahead of time.
