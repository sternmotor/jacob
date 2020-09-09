# File system handling

Find directories by pattern and remove it

```yaml
- name: find lock files to be removed
  find:
    paths: '/var/lock'
    patterns: "backup-*"
    file_type: directory
  register: lock_dirs
  tags:
    - clear

- name: remove lock files
  file:
    path: "{{ item.path }}"
    state: absent
  with_items: "{{ lock_dirs.files }}"
  tags:
    - clear
```


