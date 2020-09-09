# Ansible Syntax

Unterscheiden: Ansible Roles und IT Service Roles = Inventory Roles

## Rules

Tags: 
- Role name (nscd, java)
- install
- packages
- config
- logrotate
- certificates 
`` 

## TODO

Gleichziehen Jira Komponenten und IT-Services für Tickets

### Ansible Arbeitsweise: 
* CS Team DGO, CKO, GMA arbeitet mit eigenen Ansible clones und eigenem SSH Schlüssel auf dem Ansible Server
* SSHD auf allen Servern anpassen ansible Gruppe erlauben von Ansible-IP
* Ansible Gruppe:
    * ansible@ansible.app.infra.rz
    * DGO, CKO, GMA
* SSH Schlüssel für ansible, DGO, CKO, GMA auf Ansible erzeugen (extra), per Ansible verteilen und per ssh config für root-logins auf Kundensysteme nutzen? Eigenen Schlüssel verwenden!
* Skripte rein in Ansible
* Monitoring rein, eigene Rolle 
* Variablen aus Rollen raus
* Dokumentation rein, Tags [never, doc], write to localhost in wiki/markdown


* Login mit root als Passwort nur Console und login -l
* Neues root-passwort: länger aber schreibbar
* Ansible-Einschränkung: SSH nur von Ansible Server, FreeIPA Gruppe "Admin"
* Fallback wenn FreeIPA down: public key von uns auf ansible hintelegem, von da gehts weiter auf alle Server 

### Ansible Aufbau
* ordentlich: VariablenNamen, Wartung/Templates Dateien
* geht besser:
    * Aufruf `ansible-playbook -l` anstelle von `ansible-playbook -e target=`
    * `Template` dir ist eigentlich `Inventory`, darin Roles 
    * ziemlich einfach gehalten, keine Vererbung
    * Variablen sowohl in Group/hostvars als auch in Templates und Rollen-Dateien und setup.yml
    * seltsames HostTags <> Target Konstrukt, falschherum aufgezogen siehe ansible/setup.yml
    * Addierung von Variablen abschalten

* Ansible Verzeichnis:
```
ansible.cfg
facts
group_vars
hosts
hostsGS
hostsIDM
hostsRZ1
host_vars
roles
setup.yml
templates
wartung
xmid
xmid.yml
```


### Inventory Vorschlag

Erklärung

* Inventory Rollen und Ansible Rollen, dazwischen Wartung yml Dateien und setup yml Dateien 

Details

* Inventory komplett bei jedem Lauf einlesen als "Dynamic Inventory"
* Inventar Host Daten:
	* `dns_name`
	* `dns_alias`
	* `device_name` 
	* `host_serial` 
	* `host_comment`
	* `upstream`

* Inventar Host Gruppen:
	* `customer`
		* `jt`
		* `dev` 
	* `site`
		* `gs`, `rz1`, `wd` ...
	* `role_os`
		* `linux`, `centos`, `debian`
	* `role_hw`
		* `kvm`, `dell_pe`
	* `role_inventory`
	        * `freeipa`
		* `kibana`
		* `lamp`
		* `logstash`
		* `tomcat`
		* `vmhost`
		* `xibe_web`
		* `xmid_app`
		* `xmid_import`
		* `xmid_db`
		* `xmid_web`
		* `xres_app`
		* `xres_cache`
		* `xres_cachedb`
		* `xres_data`
		* `xres_db`
		* `xres_db_sharding`
		* `xres_ftp`
		* `xres_import`
		* `xres_mongodb`
		* `xres_redis`
		* `xres_service`
		* `xres_test`
		* `xtrav_portal`
	
* Jeder host steht in einer "hostgroup" und zieht darüber 
    * hw
    * os
    * customer
    * services
  Inventar Rollen.

Override and set up role variables, define inventory services
* `ansible/inventory/parser`             # dynamic parsing yml => ansible json
* `ansible/inventory/10-system.yml`      # general hardware, os setup
* `ansible/inventory/20-services.yml`    # inventory roles like firewall, xres_data, elastic_node
* `ansible/inventory/30-customers.yml`   # consumer variables

Mapping hosts to inventory services, set up hosts

* `ansible/inventory/40-hostgroups.yml`

Mapping hostgroups and services to ansible roles

* `ansible/wartung/update_servers.yml` 
* `ansible/desktop.yml` 
* `ansible/xres_cachedb.yml` 
* `ansible/vmhost.yml` 
* `ansible/roles`

Beispiele

* `ansible/inventory/10-system.yml`   
    ```
    linux       # ssh options, update interval, collectd options
    centos      # yum options, freeipa setup, parent: linux
    centos5
    centos7
    debian      # apt options, parent: linux
    x86         # hardware tools (lshw, lsusb)
    dell        # omsa
       parent: hw_x86
    vm          # kvm vm, tuned settings, haveged
    container   # docker container
    ```

* `ansible/inventory/20-services.yml` 
    ```
    kvm_host
    docker_host
    xres_data
    xres_service
    xres_db
    elasticsearch
    logstash
    kibana
    xres_mongodb
    server
    desktop
    ```

* `ansible/inventory/30-customers.yml`
    ```
    fer
    fer_rz1
    jt
    jt_rz1
    traso
    traso_gs
    traso_gs_wn
    traso_gs_vw
    traso_rz1
    traso_walter
    xtrav
    xtrav_gs
    xtrav_rz1
    ```

* `ansible/inventory/40-hostgroups.yml`
    ```
    - standard_desktop
        parents:
            - desktop
            - centos7
            - x86

    - standard_server
        parents:
            - server
            - centos7
            - kvm_guest

    - standard_debian
        parents:
            - server
            - debian
            - kvm_guest

    - elastic_stack_dev
        parents:
            - xtrav_rz1
            - standard
            - logstash
            - kibana
            - elasticsearch
        hosts:
            - elastic201
            - elastic202
            - elastic203

     - vmhosts
        parents:
            - server
            - kvm_host
            - centos7
            - dell
            - docker_host
     - vmhosts_rz1
        parents:
            - xtrav_vmhosts
            - xtrav_rz1
        hosts:
            - vmhost06
            - vmhost07
    ```

* `ansible/base.yml` 
    ```
    hosts: server
    roles:
        - sshd
        - collectd_client
        - sysctl
        - admin_users
        - backuppc

    hosts: centos
    roles:
        - freeipa_client
        - yum_updates
        - tuned
    hosts: debian
    roles:
        - apt_updates

    hosts: standard_desktop
    roles:
        - admin_users
        - backuppc
        - collectd_client
        - freeipa_client
        - sshd
        - sysctl
        - tuned
        - yum_updates
    ```

* `ansible/vmhosts.yml` 
    ```
    hosts: vmhosts_rz1 vmhosts_gs
    roles:
        - kvm
        - docker
    ```

Start: 
    ```
    ansible-playbook base.yml -l centos-clients
    ```


## Devel

Handle bool variables in jinja files
```
{{ 'yes' if nscd_netgroup_enable_cache|bool else 'no' }}
```

special tags:
* `['never', 'debug']` : run only when 'debug' tag is specified
* `['always', 'debug']` : run unless `--skip-tags always` is specified 

## OS

Get main ip address (where default gw is specified)
```
hostvars[inventory_hostname]['ansible_default_ipv4']['address']
```

Set environment variable

* Template

```
# set JAVA_HOME for redhat java installations
# {{ansible_managed}}
export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::")
```

* Task

```
- name: Ensure java profile
  template:
    src: java_home.j2
    dest: /etc/profile.d/java_home.sh
    mode: 0644
    tags: config
```

# Traso Ansible

Befehle auf allen vmhosts absetzen:

``` 
sudo ansible hv_infra_rz1 -i hostsRZ1 -m shell -a 'systemctl restart collectd'
`
