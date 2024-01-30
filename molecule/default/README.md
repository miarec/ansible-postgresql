# Molecule test this role

Run Molecule test
```
molecule test
```

Run test with variable example
```
MOLECULE_DISTRO=centos7 MOLECULE_POSTGRESQL_VERSION=12 molecule test
```

## Variables
 - `MOLECULE_DISTRO` OS of docker container to test, default `ubuntu2204`
    List of tested distros
    - `rhel7`
    - `rhel8`
    - `ubuntu2204`
    - `ubuntu2004`
    - `rockylinux8`
    - `rockylinux9`
    - `centos7`
 - `MOLECULE_POSTGRESQL_VERSION` defines variable `postgresql_version`, default `12`