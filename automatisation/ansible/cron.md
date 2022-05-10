# Ansible cron job setup


Weekly cron job - use symlink to make script itself available in PATH


  - name: install yum cache cleanup cron job
    block:

    - name: install script
      copy:
        dest: /usr/local/bin/yum-flush
        mode: 0750
        owner: root
        group: root
        content: |
          #!/bin/sh -eu
          # flush yum package repository

          /usr/bin/yum clean all | /usr/bin/logger -t FLUSH_YUM

    - name: install weekly cron job
      file:
        src: /usr/local/bin/yum-flush
        dest: /etc/cron.weekly/yum-flush
        state: link

    when: (ansible_distribution|lower) == 'centos'


Some cron job with PATH variable

    - name: install cronjob for nscd restart
      cron:
        name: nscd.restart
        cron_file: /etc/cron.d/nscd_restart
        minute: '4'
        hour: '5'
        weekday: '6'
        user: root
        job: >
          nscd -i passwd -i group -i hosts -i services -i netgroup 2>&1
          | logger -t FLUSH_NSCD
        state: present
    
    - name: install cronjob for nscd restart
      cron:
        name: PATH
        job: /usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin
        cron_file: /etc/cron.d/nscd-restart
        user: root
        env: yes
        state: present

