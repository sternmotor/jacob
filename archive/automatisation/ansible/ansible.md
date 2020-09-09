tasks/main.cfg


# debian/packages-php7.yml
- include: "{{ansible_os_family | lower}}/packages-php{{php_major_version}}.yml"

# debian/config.yml
- include: "{{ansible_os_family | lower}}/config.yml"


# start and wait for service:
- name: Start apache server if necessary, should be working at this point
  service: name=apache2 state=started enabled=yes

- name: Wait for apache to be available at port 80
  wait_for: port=80 host=localhost


## Compile software with ansible

See [redis ansible playbook](https://github.com/DavidWittman/ansible-redis)

