Linux network
=============


Sockets, ports, connections
--------------------------

Find process listening on tcp ipv4 port 80

    ss -4 -tlnp | grep -w :80
    ps -fp <PID>


Piping
------

Pipe-transfer of disks is handled under [filesystem](filesystem.md)


Transfer an file as-is (no compression)

    time ssh <source_host> "cat /srv/dump.pgsql.gz" | pv | ssh target "cat - > /mnt/dump.pgsql.gz"


Network config
--------------

CentOS network config for LACP with VLAN - main connection to host:

* `/etc/sysconfig/network-scripts/ifcfg-bond0`

```
DEVICE=bond0
DEVICETYPE=Bond
BONDING_OPTS="downdelay=0 lacp_rate=fast miimon=1 mode=802.3ad updelay=0 xmit_has_policy=layer3+4"
BONDING_MASTER=yes
ONBOOT=yes
IPV6INIT=no
```

* `/etc/sysconfig/network-scripts/ifcfg-eno1`

```
DEVICE=eno1
ONBOOT=yes
MASTER=bond0
SLAVE=yes
```

* `/etc/sysconfig/network-scripts/ifcfg-eno2`

```
DEVICE=eno2
ONBOOT=yes
MASTER=bond0
SLAVE=yes
```


* `/etc/sysconfig/network-scripts/ifcfg-vlan1212`

```
DEVICE=vlan1212
PHYSDEV=bond0
VLAN=yes
VLAN_ID=1212
ONBOOT=yes
IPV6INIT=no
IPADDR=10.12.12.13
PREFIX=24
GATEWAY=10.12.12.254
DNS1=10.12.13.240
```

Start the whole thing via `ifup vlan1212`.[Here][bonding] there is a summary of the bonding options and modes.


CentOS network config for LACP with VLAN - example VLAN bridge for connecting VMs:

* `/etc/sysconfig/network-scripts/ifcfg-vlan1220`

```
DEVICE=vlan1220
PHYSDEV=bond0
VLAN=yes
VLAN_ID=1220
BRIDGE=br1220
ONBOOT=yes
```

* `/etc/sysconfig/network-scripts/ifcfg-br1220`

```
DEVICE=br1220
TYPE=Bridge
ONBOOT=yes
```

Start the whole thing via `ifup br1220`


[bonding]: https://www.kernel.org/doc/Documentation/networking/bonding.txt


