# PCD Tips for Ansible

Jinja functions and filters
https://github.com/lxhunter/ansible-filter-plugins/blob/master/docs/jinja_functions.md

Filters! https://docs.ansible.com/ansible/2.5/user_guide/playbooks_filters.html
See [PDC](https://github.com/iceburg-net/ansible-pcd/blob/master/README.md)

Run command locally on ansible server
```
tasks:
  - name: Create working directories for script placement
    local_action: file
    args:
      path: "some_path"
      state: directory
      recurse: yes
```


## Roles organization
Passt bereits
* system		= srv.os.xxx
* service		= svc.xxx
* application   = app.xxx
## Tags for Tasks:
* **bootstrap** tasks are ideally run once per host. They install packages, create directories, &c.
* **configure** tasks are run more often. They modify role to follow common best practice (permissions, cron jobs, timezone, config files)
* **customize** tasks are run more often. They adapt role configuration to customer (create user data bases, join ad, add users)
* **deploy** tasks are run most often, and limited to applications and sites. Run to deploy code changes and other immediate updates

## Anderes
* `private` Verzeichnis und GIT Repository dc.ansible.private einrichten:
   * winrm/ssh credentials
   * vault für Variablen


und ro Samba Freigaben:
	* roles
	* private
        * inventory



rw geht nur über GIT Checkin

* Info: Übersicht über Versionen siehe https

* grobe Doku: Variablen konfigurieren Rollen, playbooks ordnen Gruppen Rollen zu

* Default variables: uppercase (variables likely to be overriden/configured by users)
* OS families: Debian, RedHat, Windows

## Fact Caching
The absolute fastest way would be to make use of Ansible's fact caching that was introduced in version 1.8. It requires the use of a redis server to store fact

Collectfacts with a simple playbook like ansible ping

Imagine, for instance, a very large infrastructure with thousands of hosts. Fact caching could be configured to run nightly, but configuration of a small set of servers could run ad-hoc or periodically throughout the day. With fact-caching enabled, it would not be necessary to “hit” all servers to reference variables and information about them.


## Syntax
read https://github.com/leucos/ansible-percona/blob/master/tasks/percona.yml
