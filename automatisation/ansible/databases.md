Ansible database manipulation
=============================


PostgreSQL
----------


Create restricted monitoring user - see [monitoring roles][mroles]

    - name: set up postgres monitoring user
      postgresql_user:
        user: nagios
        password: 'jaevae4ahBee4Aek0uN&eece'
        groups:
        - pg_monitor
        - pg_read_all_settings
        - pg_read_all_stats
        - pg_stat_scan_tables
        state: present
      environment:
        PGOPTIONS: "-c password_encryption=scram-sha-256"

Set up user login

  - name: set up replication user in postgresql
    blockinfile:
      path: "{{ postgresql_data_dir }}/pg_hba.conf"
      marker: "# {mark} ANSIBLE {{ item.user }} user setup"
      content: |
        {{"%-8s%-16s%-16s%-24s%s" | format (
                item.type,
                item.database,
                item.user,
                item.address | default(''),
                item.auth_method
            )
        }}
    loop:
      - { type: 'host' , database: 'replication', user: "{{ pgpool_replication_user }}", auth_method: 'scram-sha-256', address: 'samenet' }
    notify: reload postgresql





[mroles]: https://www.postgresql.org/docs/10/default-roles.html
