# Ansible error handling

Grep command output
```yaml
- name: this command prints FAILED when it fails
  command: /usr/bin/example-command -x -y -z
  register: command_result
  failed_when: "'FAILED'incommand_result.stderr"
```
