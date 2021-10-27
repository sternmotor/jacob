sudo permission setup
=====================

  - name: set up nrpe sudo check permissions
    copy:
      dest: "/etc/sudoers.d/{{ item.filename }}"
      mode: 0640
      owner: root
      group: root
      content: "{{ item.content }}"
    loop:
      - filename: nrpe-postgresql-connections
        content: "nrpe {{ ansible_hostname }} = NOPASSWD: /usr/local/bin/check_postgresql_connections\n"
      - filename: nrpe-postgresql-slave
        content: "nrpe {{ ansible_hostname }} = NOPASSWD: /usr/local/bin/check_postgresql_slave\n"
      - filename: nrpe-postgresql-backup
        content: "nrpe {{ ansible_hostname }} = NOPASSWD: /usr/local/bin/check_postgresql_backup\n"
