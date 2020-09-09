# Ansible functions, execution

Execute task only when other task has been executed
```
-name:registerwithspacewalkbase-channel
  rhn_register:server_url=http://{{spacewalk_server}}/XMLRPCactivationkey={{spacewalk_key}}
  register:spacewalkregistration
-name:cleanupYum
  command:yumcleanall
  when:spacewalkregistration.changed
```
