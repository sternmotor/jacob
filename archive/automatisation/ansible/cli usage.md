# Using ansible console

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
