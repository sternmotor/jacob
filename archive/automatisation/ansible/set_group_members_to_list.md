---
- hosts: sample-host
  gather_facts: no
  vars:
    managed_group: docker
    valid_users:
      - deploy
      - telegraf
  tasks:
    - getent:
        database: group
      # 'getent_group' fact is registered by this module

    - command: "gpasswd -d {{ item | quote }} {{ managed_group | quote }}"
      become: yes
      loop: "{{ actual_users | difference(valid_users) }}"
      vars:
        actual_users: "{{ getent_group[managed_group][2].split(',') }}"
