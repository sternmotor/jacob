# Ansible filesystem setup

Create directory
```
 - name: Set up temp dir
   file:
     name: "{{percona_tmpdir}}"
     owner: mysql
     group: mysql
     mode: u=rwX,g=rX,o=
     recurse: Yes
     state: directory
```


Sync directories (via rsync)

```
- name: Copy global vim config to /etc/vim
  synchronize:
    src: /srv/ansible/roles/tools.vim/files/vim
    dest: /etc/
    delete: True
    links: True
    recursive: True
    rsync_opts:
       - "--exclude=.git"
       - "--exclude=.gitmodules"
       - "--chmod=u=rwX,g=rX,o=rX"
       - "--chown=root:root"
    mode: push
```

Replace line in text file:

```
- name: Configure zabbix init daemon
  lineinfile:
    dest: /etc/default/zabbix-agent
    backup: yes
    state: present
    regexp: '^CONFIG_FILE='
    line: 'CONFIG_FILE="/etc/zabbix/agentd.conf"'
  notify: Restart zabbix agent
```
