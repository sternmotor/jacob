# Ansible

## Summary

see [ACP](https://gist.github.com/andreicristianpetcu/b892338de279af9dac067891579cad7d)﻿


## Collection

hosts
[group1]
localhost

	playbook group1 > role app.git.client

roles
	app.git.client
		tasks
		templates


ansible Design


README.md
fellowtech GmbH systems automatisation for server and device configuration


Playbook = site.yml		# YAML - lists of "plays": mapping hostgroups to roles: plays do contain tasks
	roles
		domain_member
			files
			tasks		# Task = call ansible module (apt, template, service)
			templates	# j2 files, {{SomeValue}}
			handlers


	group_vars


Play:
---
- hosts: webservers
  roles:
	- domain_member
  remote_user: ansible
  become: yes
  become_method: sudo


Role:
	* self-contained, controlled by default variables overridden by host group or inventory variables (customization)
	* pulled from git server

  tasks:
    - service: name=nginx state=started
  roles:
     - { role: debian_stock_config, when: ansible_os_family == 'Debian' }


Role dependencies: meta/main.yml
	--
   dependencies:
   - common

Role Default Variables:
	defaults/main.yml


Tasks:
- name: run this command and ignore the result	# task
  shell: /usr/bin/somecommand		# shell module
  ignore_errors: True

- name: template configuration file	# task
  template: src=template.j2 dest=/etc/foo.conf	# template module
  notify:
     - restart memcached	# handler
     - restart apache		# handler
  - name: Create user.
    user: home={{ project_root }}/home/ name={{ project_name }} state=present

  - name: Update the project directory.
    file: group={{ project_name }} owner={{ project_name }} mode=755 state=directory path={{ project_root }}
  - name: Install required system packages.
    apt: pkg={{ item }} state=installed update-cache=yes
    with_items: {{ system_packages }}
   - name: Mount code folder.
    mount: fstype=vboxsf opts=uid={{ project_name }},gid={{ project_name }} name={{ project_root }}/code/ src={{ project_name }} state=mounted

Task include - use vars like {{ wp_user }}
   - include: wordpress.yml
    vars:
        wp_user: timmy
        ssh_keys:
          - keys/one.txt
          - keys/two.txt

Handlers:
* Lists of tasks with globally unique name
* notified by notifiers
* handlers run in the order they are defined, not called
* run once per play when all tasks have completed
* notify multiple handlers: (ansible 2.2+) and decouple handlers from their names
	handlers:
		...
		listen: "combined handler name which may be used in other handlers, too"

	tasks:
		...
		notify: "combined handler name which may be used in other handlers, too"

Variables:
   * Dictionary:
	dict1:
		key1: val1
		key2: val2
    {{dict1.key2}}
	* List: {{ foo[0] }}
	* Variables from other hosts
	  {{ hostvars['test.example.com']['ansible_distribution'] }}
	* plain:
	  template: src=foo.cfg.j2 dest={{ remote_install_path }}/foo.cfg
    * convert string > int
	  ansible_lsb.major_release|int >= 6
	* shell output to variable:
	  tasks:
      - shell: cat /etc/motd
        register: motd_contents
      - shell: echo "motd contains the word hi"
        when: motd_contents.stdout.find('hi') != -1

Host/Group variables:
	inventory file: /etc/ansible/hosts
	group variables: /etc/ansible/group_vars/<groupname>.yml or /etc/ansible/group_vars/<groupname>/topic1.yml
	host variables: /etc/ansible/host_vars/<groupname>.yml or /etc/ansible/host_vars/<hostname>/topic1.yml

Facts::
	ansible hostname -m setup
	...
	{{ ansible_devices.sda.model }}


	Turning Off Facts
	- hosts: whatever
		gather_facts: no



conditions
* when:
tasks:
  - name: "shut down Debian flavored systems"
    command: /sbin/shutdown -t now
    when: ansible_os_family == "Debian"
"OR"
    when: (ansible_distribution == "CentOS" and ansible_distribution_major_version == "6") or
          (ansible_distribution == "Debian" and ansible_distribution_major_version == "7")
"AND":
    when:
      - ansible_distribution == "CentOS"
      - ansible_distribution_major_version == "6"
Return values:
  - command: /bin/false
    register: result
    ignore_errors: True
	...
	when: result|succeeded		  
	....
	when: result|failed
Bool:
	vars:
		epic: true
	tasks:
		- shell: echo "This certainly is epic!"
			when: epic    # when: not epic
Defined/Undefined
	when: foo is defined
	- fail: msg="Bailing out. this play requires 'bar'"
	when: foo is undefined
Comparison
	when: my_custom_fact_just_retrieved_from_the_remote_system == '1234'
	when: "'reticulating splines' in output"


loops: http://docs.ansible.com/ansible/playbooks_loops.html
- name: add several users
  user: name={{ item }} state=present groups=wheel
  with_items:
     - testuser1
     - testuser2

   with_items: "{{ somelist }}"

- name: add several users   
  user: name={{ item.name }} state=present groups={{ item.groups }}
  with_items:
    - { name: 'testuser1', groups: 'wheel' }
    - { name: 'testuser2', groups: 'root' }


- name: Configs for etc files and tools under /usr/local/bin and /usr/local/sbin
  copy: src={{item.src}} dest={{item.dst}} mode={{item.mode}} owner=root group=root directory_mode='0755'
  with_items:
    - { src: bash.bashrc, dst: /etc, mode: '0644' }
    - { src: screenrc, dst: /etc, mode: '0644' }
    - { src: vim/, dst: /etc/vim, mode: '0644' }
    - { src: bin/, dst: /usr/local/bin, mode: '0755' }
    - { src: shellscript-lib.sh, dst: /usr/local/bin, mode: '0644' }
    - { src: sbin/, dst: /usr/local/sbin, mode: '0750' }







vars.yaml:
---
project_name: myproject
project_root: /var/projects/myproject
project_repo: git@bitbucket.org:myuser/myproject.git
system_packages:
  - build-essential
  - git
  - libevent-dev
  - nginx
  - postgresql
  - postgresql-server-dev-all
  - python-dev
  - python-setuptools
  - redis-server
  - postfix
python_packages:
  - pip
  - virtualenv
initfiles:
  - gunicorn


ftproxy: ansible pull for specific customer from git.fellowtech.com: ansible-pull
ansible push for customer servers

Design
roles:
	dc.zabbix.server
	dc.unifi
	srv.os
	svc.backup.qnap
	dc.zabbix.agent
	svc.mysql

plays = dns names
	adfp
	sip
	ftproxy
	web

debiggung: ansible-playbook  /srv/ansible/roles/srv.os.lin.sssd/main.yml -vvv


sudo
	user ansible, passwordless sudo







Path to failure

This is the way a typical postgres create extension task looks.

- name: ensure postgresql hstore extension is created
  sudo: yes
  sudo_user: postgres
  shell: "psql my_database -c 'CREATE EXTENSION IF NOT EXISTS hstore;'"
Every time you run it, it will be detected as “changed” even though nothing actually changes.

Path to success

Instead we can leverage Ansible’s register, changed_when and failed_when to make this task report ok, as it should. Take a look at this version.

- name: ensure postgresql hstore extension is created
  sudo: yes
  sudo_user: postgres
  shell: "psql my_database -c 'CREATE EXTENSION hstore;'"
  register: psql_result
  failed_when: >
    psql_result.rc != 0 and ("already exists" not in psql_result.stderr)
  changed_when: "psql_result.rc == 0"
