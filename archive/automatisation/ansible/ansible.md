


# start and wait for service:

    - name: Start apache server if necessary, should be working at this point
      service: name=apache2 state=started enabled=yes

    - name: Wait for apache to be available at port 80
      wait_for: port=80 host=localhost


## Compile software with ansible

See [redis ansible playbook](https://github.com/DavidWittman/ansible-redis)



## validate ansible version

    name: Check Ansible version
      assert:
        that: '(ansible_version.major, ansible_version.minor, ansible_version.revision) >= (2, 2, 1)'
        msg: 'Please install the recommended version 2.2.1+. You have Ansible {{ ansible_version.string }}.'
      run_once: yes


