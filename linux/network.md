# Linux specific network administration


## Sockets, ports, connections

Find process listening on tcp ipv4 port 80

    ss -4 -tlnp | grep -w :80
    ps -fp <PID>


## Piping

Pipe-transfer of disks is handled under [filesystem](filesystem.md)


Transfer an file as-is (no compression)

    time ssh <source_host> "cat /srv/dump.pgsql.gz" | pv | ssh target "cat - > /mnt/dump.pgsql.gz"


Fast rsync for initial sync: use scp -r or

    rsync -aW --size-only


## Network config

### Routing and address info

Show main address and netmask

    default_iface=$(ip route show default | cut -d ' ' -f5)
    ip addr show scope global | awk "/ scope global $default_iface$/{print \$2}"

Show real addresses

    ip addr show scope global | grep inet

Show real routes

    ip route show scope link


Show default route

    ip route show default

### CentOS8

Two tools: `nmtui`, `nmcli`

Usage 

    nmcli dev status # nmcli d s
    nmcli con show   # nmcli c s (-a = active only)

* create with static ip

        nmcli con add type vlan con-name vlan20 ifname vlan20 dev bond0 id 20\
        ip4 address gw4 address

* create as dhcp client

        nmcli con add type vlan con-name vlan20 ifname vlan20 dev bond0 id 20

* create with no ip (for passing through to docker containers) 

        nmcli con add type vlan con-name vlan20 ifname vlan20 dev bond0 id 20\
        ipv4.method disabled ipv6.method disabled

* remove connection, config and device

        nmcli con del vlan20

* add ip to interface

        nmcli con show || systemctl enable --now NetworkManager
        nmcli con mod eth1 +ipv4.addresses 10.21.25.163/24
        nmcli con up eth1


### CentOS7

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


## Bonding 

[bonding]: https://www.kernel.org/doc/Documentation/networking/bonding.txt

### Debian

Bridging two interfaces - requires package `bridge-utils`

edit `/etc/network/interfaces`

```
...

# enable and bridge network cards
auto eth0
iface eth0 inet manual
auto eth1
iface eth1 inet manual
auto  br0
iface br0 inet static
    bridge_ports eth0 eth1
    address 10.0.0.160
    netmask 255.255.252.0
    gateway 10.0.3.254
    dns-nameservers 141.1.1.1
    dns-search testv2.local
    dns-domain testv2.local
#   bridge_stp off       # disable Spanning Tree Protocol
#   bridge_waitport 0    # no delay before a port becomes available
#   bridge_fd 0          # no forwarding delay
#   bridge_ports none    # if you do not want to bind to any ports
#   bridge_ports regex eth* # use a regular expression to define ports
```
