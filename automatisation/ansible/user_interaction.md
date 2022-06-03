# Ansible operator interaction


Notify agent/user/operator about some condition

    - name: inform agent in case mariadb service is not installed
      pause:
        seconds: 3
        prompt: |
          ====================================================
          MariaDB service is not installed
          Skipping DB setup, please re-run this playbook later
          ====================================================
   
      when: ansible_facts.services["mariadb.service"] is not defined

Furthermore, there are slack/telegram/mail plugins available
