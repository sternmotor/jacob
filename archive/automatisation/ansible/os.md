# Ansible OS control


## Services

Make sure a service has been started
```yaml
tasks:
  - service: name=nginx state=started
```
(Re)Start service after running config test (`apache2ctl configtest`, `nginx -t`)
```yaml
- name: reload nginx
  debug: msg="Reloading nginx"
  changed_when: True
  notify:
    - check nginx configuration
    - reload nginx really

- name: check nginx configuration
  command: nginx -t
  register: result
  changed_when: "result.rc != 0"
  always_run: yes

- name: reload nginx really
  service: name=nginx state=reloaded
```

## Cron jobs
Task for runnning mysqlcheck periodically
```yaml
- name: 'Install task for runnning mysqlcheck periodically'
  cron:
    name: 'Check and optimize mysql databases periodically'
    user: 'root'
    cron_file: 'mysqlcheck'
    state: present
    job: '/usr/bin/mysqlcheck --defaults-extra-file=/etc/mysql/debian.cnf --optimize --all-databases'
    minute: "{{percona_mysqlcheck_schedule.minute}}"
    hour:  "{{percona_mysqlcheck_schedule.hour}}"
    day: "{{percona_mysqlcheck_schedule.day}}"
- cron:
    env: yes
    name: PATH
    value: '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    user: 'root'
    cron_file: 'mysqlcheck'
- cron:
    env: yes
    name: MAILTO
    value: 'root'
    user: 'root'
    cron_file: 'mysqlcheck'
```

## Software installation, Upgrade, Reboots

see [Packages](packages.md)
