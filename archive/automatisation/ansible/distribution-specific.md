# Distribution-specific playbooks

In order to have different tasks or variables (depending on host os) in ansible role definitions, following pattern is used:

Windows and Debian-derivates are distinguished, releases and versions only if necessary.

Directory structure

    <role_dir>
        handlers
            main.yml
        tasks
            config.yml
            main.yml
            pkg.yml
            setup.yml
        vars
            debian.yml
            main.yml
            ubuntu19.yml
            windows.yml

In `tasks/main.yml`, all the magic happens:

    # load static variables, search centos7 > centos > redhat > linux
    - name: Load os specific variables
      include_vars: "{{item}}"                                                                                                                
      with_first_found:
        - "{{ansible_distribution|lower}}{{ansible_distribution_major_version}}.yml"
        - "{{ansible_distribution|lower}}.yml"
        - "{{ansible_os_family|lower}}.yml"
        - "{{ansible_system|lower}}.yml"

    # package installation
    - import_tasks: pkg.yml
    - import_tasks: setup.yml
    - import_tasks: config.yml

    # vim: ts=2:sw=2
