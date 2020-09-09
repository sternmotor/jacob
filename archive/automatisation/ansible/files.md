# Ansible file handling


Mkdir
```yaml
 - name: Set up temp dir
   file:
     name: "{{percona_tmpdir}}"
     owner: mysql
     group: mysql
     mode: u=rwX,g=rX,o=
     recurse: Yes
     state: directory
```


Rsync: synchronize folders, set permissions, `rsync --delete`
```yaml
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



Make sure a symlink exists

```yml
- name: Check if gmp.h is already in a location accessible to gcc.
  stat: path=/usr/include/gmp.h
  register: gmp_file

- name: Ensure gmp.h is symlinked into a location accessible to gcc.
  file:
    src: "{{ php_source_install_gmp_path }}"
    dest: /usr/include/gmp.h
    state: link
  when: gmp_file.stat.exists == false
```

Replace line in textfile
```yaml
- name: Configure zabbix init daemon
  lineinfile:
    dest: /etc/default/zabbix-agent
    backup: yes
    state: present
    regexp: '^CONFIG_FILE='
    line: 'CONFIG_FILE="/etc/zabbix/agentd.conf"'
  notify: Restart zabbix agent
```
