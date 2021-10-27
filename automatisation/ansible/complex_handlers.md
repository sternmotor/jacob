Ansible complex handler configs
===============================


Example: determine postgresql server version, restart or reload it

  handlers:

  - name: retrieve postgres version
    command: psql -U postgres -Atc 'SHOW server_version'
    register: postgresql_version_result
    changed_when: false
    listen:
    - reload postgresql
    - restart postgresql

  - name: register server major version
    set_fact:
      postgresql_major_version: "{{ postgresql_version_result.stdout.split('.')[0] }}"
    listen:
    - reload postgresql
    - restart postgresql

  - name: do reload postgresql
    service:
      name: "postgresql-{{ postgresql_major_version }}"
      state: reloaded
    listen: reload postgresql

  - name: do restart postgresql
    service:
      name: "postgresql-{{ postgresql_major_version }}"
      state: restarted
    listen: restart postgresql
