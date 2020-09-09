# Ansible User Configuration

Run play per `sudo`
```yaml
remote_user: ansible
become: yes
become_method: sudo
```

Create user with ssh authorized keys
```yaml
- name: create and/or change {{ username}}'s password
  user:
    name: "{{ username }}"
    password: << some password hash>
- name: copy ssh keys
  authorized_key:
    key: "{{ item }}"
    user: "{{ username }}"
    state: present
    exclusive: False
  with_file:
    - ../files/user1_ssh_key.pub
    - ../files/user2_ssh_key.pub
```
