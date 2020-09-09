# Ansible facts and setup

Enable fact cache (yaml - easy debugging)
* edit `ansible.conf`:
    ```
    fact_caching = yaml
    fact_caching_connection = /var/cache/ansible/facts
    fact_caching_timeout = 86400
    ```


* prepare system:
    ```
    mkdir /var/cache/ansible/{facts,retry,ssh}
    mkdir /var/tmp/ansible
    ```

Pattern for retrieving facts with raw command, store to cache and check fact cache
```
---
- hosts: host.domain.tld
  gather_facts: no
  tasks:
    - name: Retrieve firewall status info
      raw: get system status        # firewall shell command
      register: firewall_status
      when: ansible_facts['firewall_version'] is not defined

    - name: Parse firewall status for version info, store in cache
      set_fact:
        # convert "FGT80C3911620250 $ Version: FortiGate-80C v5.2.9,build0..." to "v5.2.9"
        firewall_version: "{{item.split('Version:')[1].split()[1].split(',')[0]}}"
        cacheable: true
      with_items: "{{firewall_status.stdout_lines}}"
      when:
      # order is important here - at first check if firewall_status had been registered
      - ansible_facts['firewall_version'] is not defined
      - '" Version: " in item'

    - debug: msg="{{firewall_version}}"
```
