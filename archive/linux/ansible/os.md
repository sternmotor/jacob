# Ansible OS configuration

## Services

Make sure service has been started
```
tasks:
  - service: name=nginx state=started
```

Start service after successful config validation
```
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

## Scheduled Tasks

Run mysqlcheck periodically

```
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

## APT package manager

Setup repository
```
- name: Setup zabbix apt repository
  apt_repository: filename=zabbix state=present update_cache=yes
    repo: "deb http://repo.zabbix.com/zabbix/{{zabbix_version}}/ubuntu {{ansible_distribution_release}} main"
  when: ansible_os_family == "Debian"
```

PPA
```
- name: Install zabbix APT key
  apt_key: keyserver=keyserver.ubuntu.com id=C407E17D5F76A32B
```
