import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_directories(host):
    if host.system_info.distribution == "ubuntu":
        dirs = [
            "/etc/postgresql/12/main",
            "/var/run/postgresql"
        ]
    if host.system_info.distribution == "centos":
        dirs = [
            "/etc/postgresql/12/data",
            "/var/run/postgresql"
        ]
    for dir in dirs:
        d = host.file(dir)
        assert d.is_directory
        assert d.exists

def test_files(host):
    if host.system_info.distribution == "ubuntu":
        files = [
            "/etc/postgresql/12/main/pg_hba.conf",
            "/etc/postgresql/12/main/pg_ident.conf",
            "/var/run/postgresql/12-main.pid"
        ]
    if host.system_info.distribution == "centos":
        files = [
            "/etc/postgresql/12/data/pg_hba.conf",
            "/etc/postgresql/12/data/pg_ident.conf",
            "/var/run/postgresql/12-data.pid"
        ]

    for file in files:
        f = host.file(file)
        assert f.exists
        assert f.is_file

def test_service(host):
    if host.system_info.distribution == "ubuntu":
        s = host.service("postgresql")
    if host.system_info.distribution == "centos":
        s = host.service("postgresql-12")
    assert s.is_enabled
    assert s.is_running


def test_socket(host):
    sockets = [
        "tcp://127.0.0.1:5432"
    ]
    for socket in sockets:
        s = host.socket(socket)
        assert s.is_listening