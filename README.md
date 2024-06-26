# ansbile-postgreql
![CI](https://github.com/miarec/ansible-postgresql/actions/workflows/ci.yml/badge.svg?event=push)


Ansible role which installs and configures PostgreSQL, extensions, databases and users.


#### Installation

This has been tested on Ansible 2.4.0 and higher.

To install:

```
ansible-galaxy install miarec.postgresql
```

#### Example Playbook

Including an example of how to use your role:

    - hosts: postgresql-server
      become: yes
      roles:
         - { role: miarec.postgresql }



#### Compatibility matrix

| Distribution / PostgreSQL | 12 | 13 | 14 | 15 |
| ------------------------- |:---:|:---:|:---:|:---:|
| Ubuntu 20.04 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|
| Ubuntu 22.04 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|
| CentOS 7 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|
| RockyLinux8 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|
| RockyLinux9 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|
| RHEL 7 | :white_check_mark: | :white_check_mark:| :warning:| :warning:|
| RHEL 8 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|
| RHEL 9 | :white_check_mark: | :white_check_mark:| :white_check_mark:| :white_check_mark:|

- :white_check_mark: - tested, works fine
- :warning: - Not for production use
- :grey_question: - will work in the future (help out if you can)
- :interrobang: - maybe works, not tested
- :no_entry: - Has reached End of Life (EOL)



#### Variables

```yaml
# Basic settings
postgresql_version: 12
postgresql_encoding: "UTF-8"
postgresql_locale: "en_US.UTF-8"
postgresql_ctype: "en_US.UTF-8"

postgresql_admin_user: "postgres"
postgresql_default_auth_method: "peer"

postgresql_service_enabled: false # should the service be enabled, default is true

postgresql_cluster_name: "main"
postgresql_cluster_reset: false

# List of databases to be created (optional)
# Note: for more flexibility with extensions use the postgresql_database_extensions setting.
postgresql_databases:
  - name: foobar
    owner: baz          # optional; specify the owner of the database
    hstore: yes         # flag to install the hstore extension on this database (yes/no)
    uuid_ossp: yes      # flag to install the uuid-ossp extension on this database (yes/no)
    citext: yes         # flag to install the citext extension on this database (yes/no)
    encoding: "UTF-8"   # override global {{ postgresql_encoding }} variable per database
    lc_collate: "en_GB.UTF-8"   # override global {{ postgresql_locale }} variable per database
    lc_ctype: "en_GB.UTF-8"     # override global {{ postgresql_ctype }} variable per database

# List of database extensions to be created (optional)
postgresql_database_extensions:
  - db: foobar
    extensions:
      - hstore
      - citext

# List of users to be created (optional)
postgresql_users:
  - name: baz
    pass: pass
    encrypted: yes  # if password should be encrypted, postgresql >= 10 does only accepts encrypted passwords

# List of schemas to be created (optional)
postgresql_database_schemas:
  - database: foobar           # database name
    schema: acme               # schema name
    state: present

  - database: foobar           # database name
    schema: acme_baz           # schema name
    owner: baz                 # owner name
    state: present

# List of user privileges to be applied (optional)
postgresql_user_privileges:
  - name: baz                   # user name
    db: foobar                  # database
    priv: "ALL"                 # privilege string format: example: INSERT,UPDATE/table:SELECT/anothertable:ALL
    role_attr_flags: "CREATEDB" # role attribute flags
```

There's a lot more knobs and bolts to set, which you can find in the [defaults/main.yml](./defaults/main.yml)


#### Testing

This project comes with a Vagrantfile, this is a fast and easy way to test changes to the role, fire it up with `vagrant up`

See [vagrant docs](https://docs.vagrantup.com/v2/) for getting setup with vagrant

Once your VM is up, you can reprovision it using either `vagrant provision`, or `ansible-playbook tests/playbook.yml -i vagrant-inventory`

If you want to toy with the test play, see [tests/playbook.yml](./tests/playbook.yml), and change the variables in [tests/vars.yml](./tests/vars.yml)

If you are contributing, please first test your changes within the vagrant environment, (using the targeted distribution), and if possible, ensure your change is covered in the tests found in [.travis.yml](./.travis.yml)


#### License

Licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.