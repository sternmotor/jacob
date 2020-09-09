# CentOS

# Linux command line

## less
less -N: line Numbers
less -S: no line breaks

/ = search
n = find next
N = find previous
qq = top of file
Q  = end of file
Shift-f = toggle follow mode (like tail -f)


zless, zcat ... show zipped logs

OS cleanup
----------


    yum clean all
    journalctl --vacuum-time=7d
    abrt-cli rm /var/spool/abrt/*

Update to mainline kernel

    sudo rpm --import https://www.elrepo.org/RPM-GPG-KEY-elrepo.org
    sudo rpm -Uvh http://www.elrepo.org/elrepo-release-7.0-3.el7.elrepo.noarch.rpm 
    sudo yum --enablerepo=elrepo-kernel install -y kernel-ml


Packages
--------
If you haven’t already done so, install the Remi and EPEL repositories
```
wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm && rpm -Uvh epel-release-latest-6.noarch.rpm
wget http://rpms.famillecollet.com/enterprise/remi-release-6.rpm && rpm -Uvh remi-release-6*.rpm
```

Fix bad mirror (example: `centos-gluster38`)

```
yum install -y yum-utils --disablerepo=centos-gluster38
yum-config-manager --save --setopt=centos-gluster38.skip_if_unavailable=true
```

Searching for a package with binary name
```
yum whatprovides */ls
```

Generate rpm file from source
-----------------------------

```
yum install -y rpm-build
mkdir --parents -- rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}
$DESC = grub 2.04 compilation for centos
cat << EOF > spec
# info for "rpm -qi [Package Name]"
Summary: $DESC
Name: grub
Packager: Traso GmbH
BuildRoot: $PWD/rpmbuild/

%description
$DESC

%prep


EOF

```


# Network Config

Server vmhost bridge for vm

* edit `/etc/sysconfig/network-scripts/ifcfg-br1217`

```
DEVICE=br1217
ONBOOT=yes
TYPE=Bridge
BOOTPROTO=static
NAME=br1217
```

* edit `/etc/sysconfig/network-scripts/ifcfg-vlan1217`
```
VLAN=yes
DEVICE=vlan1217
PHYSDEV=team0
VLAN_ID=1217
BOOTPROTO=none
ONBOOT=yes
BRIDGE=br1217
```

* load networking - do not restart "networking" service on vmhosts!
```
ifup vlan1217
ifup br1217
```

Server VM

* edit `/etc/sysconfig/network-scripts/ifcfg-eth0`
```
DEVICE=eth0
IPV6INIT=no
BOOTPROTO=static
ONBOOT=yes
IPADDR=192.168.103.27
PREFIX=24
GATEWAY=192.168.103.254
```

* reload networking
```
systemctl restart network
systemctl restart sshd
```

## Desktop VLAN

### Host Interface

* deactivate own ip and routing: edit `/etc/sysconfig/network-scripts/ifcfg-enp0s25` 
	```
	NAME=enp0s25
	DEVICE=enp0s25
	ONBOOT=yes
	NETBOOT=yes
	UUID=bf1886bf-56a4-44e4-b6d1-e44eddfd1ba6
	IPV6INIT=no
	BOOTPROTO=none
	TYPE=Ethernet
	PROXY_METHOD=none
	BROWSER_ONLY=no
	DEFROUTE=no
	```

### VLAN Interface

Example: CS network config
* edit `/etc/sysconfig/network-scripts/ifcfg-cs`
	```
	VLAN=yes
	TYPE=Vlan
	PHYSDEV=enp0s25
	VLAN_ID=103
	REORDER_HDR=yes
	GVRP=no
	MVRP=no
	PROXY_METHOD=none
	BROWSER_ONLY=no
	BOOTPROTO=dhcp
	DEFROUTE=yes
	IPV4_FAILURE_FATAL=no
	IPV6INIT=no
	NAME=cs
	UUID=362cfec2-bb18-4e1d-a6c5-c9a86b274beb
	DEVICE=cs
	ONBOOT=yes
	```
