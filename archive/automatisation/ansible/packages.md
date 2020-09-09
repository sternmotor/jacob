# Ansible package management

## General

check if executable can be found, create condition

```yml
- name: Check if PHP is installed.
  command: which php
  changed_when: false
  failed_when: false
  register: php_installed

- name: Ensure PHP installation path exists.
  file:
    path: "{{php_source_install_path}}"
    state: directory
    mode: 0755
  when: php_installed.rc != 0
```


## Aptitude package and cache handling


For obtaining e.g. `ansible_os_family` variable, `gather_subset: !all,!any,facter`

Install packages

```yml
- name: install build chain packages
  apt:
    cache_valid_time: 259200 # accept 3 days old cache
    state: installed
    name:
    - autoconf
    - automake
    - bison
  when: ansible_os_family == 'Debian'
```

Remove packages
```yml
- name: install build chain packages
  rpm:
    state: absent
    autoremove: yes
    purge: yes
    name:
    - autoconf
    - automake
    - bison
  when: ansible_os_family == 'Debian'
```

Safe-Upgrade packages
```yml
- hosts: linux-servers
  gather_facts: yes
  tasks:
  - name: safe-upgrade packages
    apt:
      upgrade:safe
      cache_valid_time: 259200 # accept 3 days old cache
      name: *
    when: ansible_os_family == 'Debian'
```

Pattern for loading gpg keys

* Problem: server behind firewall/Proxy may not be allowed to access ppa key servers
* download gpg key anywhere, anyway (or install manually) and copy from `/etc/apt/trusted.gpg.d` to ansible role,
handle there like

```yml
# downloaded from/as 'https://dl.ondrej-phppkg.com/debian/pubkey.gpg'
- name: repository | copy ondrej php key
  copy:
    src: ondrej-php.gpg
    dest: /etc/apt/ondrej-php.gpg
    owner: root
    mode: 400

- name: repository | install ondrej-php key
  apt_key:
    file: /etc/apt/ondrej-php.gpg
    state: present

- name: repository | add php7 repository
  become: true
  apt_repository:
    repo: 'deb http://ppa.launchpad.net/ondrej/php/ubuntu xenial main'
    filename: 'php7-onderej'
    update_cache: yes
    validate_certs: yes
    state: present
```

Upgrade and reboot servers
```yaml
- hosts: amazon-linux-servers
  sudo: true
  tasks:
    - name: upgrade all packages
      yum: name=* state=latest

    - name: Check for reboot hint.
      shell: LAST_KERNEL=$(rpm -q --last kernel | awk 'NR==1{sub(/kernel-/,""); print $1}'); CURRENT_KERNEL=$(uname -r); if [ $LAST_KERNEL != $CURRENT_KERNEL ]; then echo 'reboot'; else echo 'no'; fi
      ignore_errors: true
      register: reboot_hint

    - name: Rebooting ...
      command: shutdown -r now "Reboot required for updated kernel"
      async: 0
      poll: 0
      sudo: true
      ignore_errors: true
      when: reboot_hint.stdout.find("reboot") != -1
      register: rebooting

    - name: Wait for thing to reboot...
      pause: seconds=45
      when: rebooting|changed
```

## Compile packages from source
see [ansible php github project](https://github.com/geerlingguy/ansible-role-php), `/tasks/install-from-source.yml`

Complete process:


```yml
- name: Check if PHP is installed.
  command: which php
  changed_when: false
  failed_when: false
  register: php_installed

- name: Ensure dependencies for building from source are installed (Debian).
  apt:
    cache_valid_time = 259200   # 3 days
    state: installed
    name:
    - autoconf
    - automake
    - bison
    - build-essential
    - libbz2-dev
    - libcurl4-openssl-dev
    - libfreetype6-dev
    - libgmp3-dev
    - libjpeg-dev
    - libmcrypt-dev
    - libmysqlclient-dev
    - libpng12-dev
    - libpspell-dev
    - librecode-dev
    - libssl-dev
    - libtool
    - libxml2-dev
    - libxpm-dev
    - pkg-config
    - re2c
  when:
    - ansible_os_family == 'Debian'
    - php_installed.rc != 0


- name: Clone the PHP repository.
  git:
    repo: "{{ php_source_repo }}"
    dest: "{{ php_source_clone_dir }}"
    version: "{{ php_source_version }}"
    accept_hostkey: yes
    depth: "{{ php_source_clone_depth }}"
  when: php_installed.rc != 0

- name: Ensure PHP installation path exists.
  file:
    path: "{{ php_source_install_path }}"
    state: directory
    mode: 0755
  when: php_installed.rc != 0

- name: Build configure script.
  shell: >
    ./buildconf --force
    chdir={{ php_source_clone_dir }}
  when: php_installed.rc != 0

- name: Run configure script.
  shell: >
    {{ php_source_configure_command }}
    chdir={{ php_source_clone_dir }}
  when: php_installed.rc != 0

- name: Make and install PHP.
  shell: >
    {{ item }}
    chdir={{ php_source_clone_dir }}
  with_items:
    - "{{ php_source_make_command }}"
    - make install
  when: php_installed.rc != 0

- name: Ensure php executable is symlinked into a standard path.
  file:
    src: "{{ php_source_install_path }}/bin/php"
    dest: /usr/bin/php
    state: link


- name: Ensure dependencies for building from source are removed again
  apt:
    state: absent
    autoremove: yes
    purge: yes
    name: {{php_build_packages}}

    php_build_packages:
    - autoconf
    - automake
    - bison
    - build-essential
    - libbz2-dev
    - libcurl4-openssl-dev
    - libfreetype6-dev
    - libgmp3-dev
    - libjpeg-dev
    - libmcrypt-dev
    - libmysqlclient-dev
    - libpng12-dev
    - libpspell-dev
    - librecode-dev
    - libssl-dev
    - libtool
    - libxml2-dev
    - libxpm-dev
    - pkg-config
    - re2c
  when:
    - ansible_os_family == 'Debian'
    - php_installed.rc == 0
```
