import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

postgresql_version = os.environ.get('POSTGRESQL_VERSION')

# The directory the role manages. converge.yml points the postgresql_ssl_*_file
# variables here, and the role creates it and uploads the files from the
# control machine.
SERVER_TLS_DIR = "/etc/postgresql/tls"

# The client files that prepare.yml uploads for these tests. They are a test
# fixture, not something the role manages.
CLIENT_TLS_DIR = "/root/tls-client"

SERVICE_USER = "postgres"
SERVICE_GROUP = "postgres"


def test_postgresql_service_running(host):
    """Verify PostgreSQL service is enabled and running."""
    if host.system_info.distribution == "ubuntu":
        s = host.service("postgresql")
    else:
        s = host.service("postgresql-{}".format(postgresql_version))
    assert s.is_enabled
    assert s.is_running


def test_postgresql_port_listening(host):
    """Verify PostgreSQL is listening on port 5432."""
    s = host.socket("tcp://0.0.0.0:5432")
    assert s.is_listening


def test_postgresql_ssl_enabled(host):
    """Verify PostgreSQL has SSL enabled in configuration."""
    if host.system_info.distribution == "ubuntu":
        conf_path = "/etc/postgresql/{}/main/postgresql.conf".format(
            postgresql_version)
    else:
        conf_path = "/etc/postgresql/{}/data/postgresql.conf".format(
            postgresql_version)

    conf = host.file(conf_path)
    assert conf.exists
    assert conf.contains("ssl = on")


def test_tls_files_uploaded(host):
    """The role uploaded the server certificate, the key, and the CA certificate."""
    for name in ("server.crt", "server.key", "ca.crt"):
        f = host.file(f"{SERVER_TLS_DIR}/{name}")
        assert f.exists, f"TLS file not found: {SERVER_TLS_DIR}/{name}"
        assert f.is_file, f"Not a file: {SERVER_TLS_DIR}/{name}"


def test_ca_key_not_on_host(host):
    """The CA private key stays on the control machine."""
    assert not host.file(f"{SERVER_TLS_DIR}/ca.key").exists


def test_tls_file_permissions(host):
    """The role uploads the private key readable by the service group only."""
    key = host.file(f"{SERVER_TLS_DIR}/server.key")
    assert key.user == "root", "server.key is not owned by root"
    assert key.group == SERVICE_GROUP, f"server.key is not group {SERVICE_GROUP}"
    assert key.mode == 0o640, "server.key is not 0640"
    for name in ("ca.crt", "server.crt"):
        cert = host.file(f"{SERVER_TLS_DIR}/{name}")
        assert cert.user == "root", f"{name} is not owned by root"
        assert cert.mode == 0o644, f"{name} is not 0644"
    # The role created the directory, so it has the fixed mode, not the umask.
    tls_dir = host.file(SERVER_TLS_DIR)
    assert tls_dir.is_directory
    assert tls_dir.user == "root", "TLS directory is not owned by root"
    assert tls_dir.mode == 0o755, "TLS directory is not 0755"


def test_service_user_can_read_tls_key(host):
    """The service user reads the private key through the service group."""
    result = host.run(f"runuser -u {SERVICE_USER} -- cat {SERVER_TLS_DIR}/server.key")
    assert result.rc == 0, f"{SERVICE_USER} cannot read server.key: {result.stderr}"


def test_postgresql_tls_connection_with_sslmode_require(host):
    """Verify PostgreSQL accepts TLS connections with sslmode=require."""
    cmd = host.run(
        'psql "host=127.0.0.1 user=postgres dbname=postgres sslmode=require" '
        "-c 'SELECT 1;'"
    )
    assert cmd.rc == 0, f"Expected rc=0, got rc={cmd.rc}, stderr={cmd.stderr}"


def test_postgresql_tls_connection_with_verify_ca(host):
    """Verify PostgreSQL accepts TLS connections with CA verification."""
    cmd = host.run(
        'psql "host=127.0.0.1 user=postgres dbname=postgres '
        f'sslmode=verify-ca sslrootcert={CLIENT_TLS_DIR}/ca.crt" '
        "-c 'SELECT 1;'"
    )
    assert cmd.rc == 0, f"Expected rc=0, got rc={cmd.rc}, stderr={cmd.stderr}"


def test_postgresql_tls_connection_with_client_cert(host):
    """Verify PostgreSQL accepts TLS connections with client certificates."""
    cmd = host.run(
        'psql "host=127.0.0.1 user=postgres dbname=postgres '
        'sslmode=verify-ca '
        f'sslrootcert={CLIENT_TLS_DIR}/ca.crt '
        f'sslcert={CLIENT_TLS_DIR}/client.crt '
        f'sslkey={CLIENT_TLS_DIR}/client.key" '
        "-c 'SELECT 1;'"
    )
    assert cmd.rc == 0, f"Expected rc=0, got rc={cmd.rc}, stderr={cmd.stderr}"


def test_postgresql_tls_connection_with_invalid_client_cert_fails(host):
    """Verify PostgreSQL rejects a client certificate the uploaded CA didn't sign."""
    cmd = host.run(
        'psql "host=127.0.0.1 user=postgres dbname=postgres '
        'sslmode=verify-ca '
        f'sslrootcert={CLIENT_TLS_DIR}/ca.crt '
        f'sslcert={CLIENT_TLS_DIR}/invalid-client.crt '
        f'sslkey={CLIENT_TLS_DIR}/invalid-client.key" '
        "-c 'SELECT 1;'"
    )
    assert cmd.rc != 0, "Connection with a self-signed client certificate should be rejected"


def test_postgresql_ssl_info_in_connection(host):
    """Verify SSL is actually being used in the connection."""
    cmd = host.run(
        'psql "host=127.0.0.1 user=postgres dbname=postgres sslmode=require" '
        "-c 'SHOW ssl;'"
    )
    assert cmd.rc == 0, f"Expected rc=0, got rc={cmd.rc}, stderr={cmd.stderr}"
    assert "on" in cmd.stdout


def test_postgresql_connection_without_tls_fails(host):
    """Verify PostgreSQL rejects non-TLS connections (hostssl only in pg_hba)."""
    cmd = host.run(
        'psql "host=127.0.0.1 user=postgres dbname=postgres sslmode=disable" '
        "-c 'SELECT 1;'"
    )
    # Connection should fail when TLS is required via hostssl-only pg_hba config
    assert cmd.rc != 0, "Connection without TLS should be rejected"
