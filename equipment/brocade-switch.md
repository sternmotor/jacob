# Brocade switch CLI administration

SSH

sshpass -p 'xxx' -o PubkeyAuthentication=no root@brocade.example.com

* Enter Privileged mode: `enable` 
* Terminal config mode: `conf t`
* show all lags: `show lag brief`
* rename lag
```
lag <old name>
update-lag-name <new name>
write mem
```

* create lag
```
lag host01 dynamic id 262
ports ethernet 3/1/23 ethernet 4/1/23
primary-port 3/1/23
deploy
```

* add vlan to lag
```
show lag brief host01
show vlan brief e 1/1/29
vlan 1212
tagged e 1/1/29
write mem
```


* make changes permanently: `write mem`
* secure switch config: `copy running-config tftp 10.12.10.12 brocade.cfg`
* MAC Adresse suchen: `show mac-address | include 848f.69fd`

