# Ansible Data and Variables

## Variables
Set Variable in task:
```yaml
-name: useSpacewalkinDMZwhenneeded
  set_fact: spacewalk_server={{dmz_spacewalk_server}}
  when: dmz
```

Default Values:

```yaml
     line="PermitTunnel {{ssh_permittunnel_value|default('no')}}"
```



## Arrays, lists
Extend list

```yaml
{{ list1 + list2 }}
```


Append to list
```yaml
{{ list1 + [element] }}
```

## Dictionaries

Iterate over dictionary

```yaml
- file: src=/tmp/{{ item.src }} dest={{ item.dest }} state=link
  loop:
    - { src: 'x', dest: 'y' }
    - { src: 'z', dest: 'k' }
```

Nested iteration over dictionary

* `outer.yml`
```yaml
- name: Set up catalina working directories dir for tomcat instance(s)
  include: inner.yml basedir={{instance.basedir}}
  loop: "{{tomcat_instances}}"
  loop_control:
    loop_var: instance
```

* `inner.yml`

```yaml
- file:
    path: "{{basedir}}/{{inner_item}}"
    owner: tomcat
    group: tomcat
    mode: "u=rwX,g=rX,o="
    state: directory
  loop:
    - logs
    - temp
    - work
```
