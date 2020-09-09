# Ansible general

See also: [Ansible linux configuration](../linux/ansible/os.md)

* playbooks map group and host definitions to roles
* variables configure roles (overriding role defaults)
* inventory: hosts, groups, customers, sites, role config variables

## Links

* [Very good syntax overview](https://gist.github.com/andreicristianpetcu/b892338de279af9dac067891579cad7d)

## CLI Usage

ssh/ winrm connectivity check
```
ansible <host> -m ping
```
ansible playbook anwenden

```
ansible-playbook site.yml --verbose
```
facts auslesen

```
ansible <host> -m setup # -a 'gather_subset=!all'
```
dry run, show diffs

```
ansible <host> -CD
```
list selected hosts

```
ansible <host/group> --list-hosts
```


## Possible role scheme for ansible administration

Es sind fünf Rollen für den Zugriff auf Automatisierungs-Ressourcen nötig

Guest = Beobachter

* read-only Zugriff auf auf für Interessierte veröffentlichbare Ressourcen (z.B. User-Ressourcen)
    * Beispiel Ansible: Inventory, Rollen

User = Anwender

* read-write Zugriff auf Ressourcen, welche zur Benutzung der Anwendung veränderbar sein müssen
    * Beispiel Ansible: Inventory, File-Ordner in Rollen
* read-only Zugriff auf Dev-Ressourcen  
    * Beispiel Ansible: Rollen, Credentials

Dev = Entwickler

* read-write Zugriff auf User-Ressourcen
* read-write Zugriff auf die Programmierung
    * Beispiel Ansible: Rollen (Tasks, Defaults, Templates, Plugins)
* read-only Zugriff auf Verwaltung von Zugriffsrechten und System-Konfiguration
    * Beispiel Ansible: private-Daten (siehe Admin) und ansible.cfg

Admin = Systemverwaltung, Wartung

* read-write Zugriff auf User/Dev-Ressourcen
* read-write Zugriff auf System-Konfiguration und Verwaltung von Zugriffsrechten
    * Beispiel Ansible: Zugriff auf private-Daten (Windows Domain-Admin- und Linux SSH-Credentials) oder ansible.cfg
