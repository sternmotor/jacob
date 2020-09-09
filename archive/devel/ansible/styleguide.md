# Ansible style guide

## Writing Yaml

It is easier to read long lists than long horizontal lines but long text make it harder to keep an overview. [There we are](https://www.jeffgeerling.com/blog/yaml-best-practices-ansible-playbooks-tasks).

Put less than 3 arguments into single line ...
```yaml
- name: Install percona APT key
  apt_key: keyserver= keys.gnupg.net id=1C4CBDCDCD2EFD2A
```

```yaml
- name: Install software packages
  apt: state=installed
    name:
    - percona-toolkit
    - xtrabackup
```

... but create a list view for more than 2 arguments
```yaml
- name: Set up mysql config file /etc/mysql/my.cnf
  template:
    src: my.cnf.j2
    dest: /etc/mysql/my.cnf
    mode: u=rw,g=r,o=r
    owner: root
    group: root
    backup: yes
  notify:
    - Restart mysql
```

Split long shell commands into multiple lines
```yaml
- name: Install Drupal.
  command: >
    drush si -y
    --site-name="{{ drupal_site_name }}"
    --account-name=admin
    --account-pass={{ drupal_admin_pass }}
    --db-url=mysql://root@localhost/{{ domain }}
    chdir={{ drupal_core_path }}
    creates={{ drupal_core_path }}/sites/default/settings.php
```
