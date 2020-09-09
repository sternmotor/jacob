# Automatisation
## General structure

* Customer > Site > Host > Service
* Customer > Service

## Service:
* Ansible Role + organisational configuration

Role:    
* pure technical module implementation with reasonable default variables to be controlled in Service / Group definitions
* no organsational setup in roles, shareable content (Github, Gitlab)  

## Automatisation Tag
* `backup`: configure backup dumps
* `config`: configure system and apps
* `deploy`: rollout of bare system, packages and tools/ scripts
* `doc`: export markdown documentation
* `monitor`: configure monitoring
* `test`: test deployed system and apps  
* `update`: package update


## Component
* Applying components allows for structuring of e.g. knowledge base (jacob, library), git repository, file system
* Components have uniq names an uniq content even if under different directories/categories
* Components are ordered in tow ways: a main simple alphabetic structure +  links to a two level strcuture  below
* no whitespace or utf8 in component names

### Component Overview
How to organize README.md for component:

* Usage (Features, Logging, Monitoring, Backup)
* Installation and Updates
* Troubleshooting
* Design Guide (Features, Logging, Monitoring, Backup)

### Simple alphabetic list

Alphabetic list
```
ad          
ansible
apache
atom
backup-rotation
ca
ceph
chrome
collaboration
dell-poweredge
dfs
dhcp
direct-radio
dns
docker
drac
editors
elk
excel
exchange
filezilla   
firewall
gpo
graphana
http
https
hyperv
iis
ipv6
jira
kerberos
kms
kvm
ldap
lin-backup
lin-console
lin-desktop
lin-desktop-alpine
lin-desktop-fluxbox
lin-desktop-ubuntu
lin-files
lin-filesystem
lin-logging
lin-network
lin-os
lin-time-date-units
lin-tools
lin-users
linux-dell
linux-x86
mac-backup
mac-desktop
mac-files
mac-filesystem
mac-network
mac-os
mac-tools
mac-users
macos-hackintosh
mailstore
mssql
mysql
netcat
nginx
ninite
nmap        
nps
postgresql
powershell
printer
puppet
putty       
python
rbac
rdg
rds
rds
riemann
routing
samba
screen
seafile
siw         
snmp
ssh
ssl
switch
tabs-windows-spaces
tcpdump
tmux
uml
ups
vim
vpn
wget
win-backup
win-console
win-desktop
win-eventlog
win-files
win-filesystem
win-network
win-os  
win-tools
win-users
windows-dell
xen
zabbix-agent
zabbix-proxy
zabbix-server
```



### Component list with categories
```
Tag/Category
    Component
```

This resolves to
```
app/    # tools and applications
    atom
    chrome
    excel
    filezilla   
    jira
    putty       
    screen
    siw         
    tmux
    vim
automatisation/
    ansible
    puppet
    ninite
backup/     # only general backup stuff - backup itself is included in components
    backup-rotation
database/   
    mssql
    mysql
    postgresql
desktop/
    tabs-windows-spaces.md
devel/
    python
    powershell
directory/
    ldap
    kerberos
    ad
    rbac
email/
    exchange
    mailstore
equipment/
    firewall
    printer
    switch
    ups
    drac
    dell-hardware
filesharing/
    seafile
    samba
    dfs
    ceph
hardware
    linux-dell
    linux-x86
    windows-dell
    macos-hackintosh
linux/
    lin-backup
    lin-console
    lin-desktop
    lin-desktop-alpine
    lin-desktop-fluxbox
    lin-desktop-ubuntu
    lin-files
    lin-filesystem
    lin-logging
    lin-network
    lin-os  # services, install, upgrade, kernel, hardening, chroot
    lin-time-date-units
    lin-tools   # os-specific scripts
    lin-users
macos/
    mac-backup
    mac-desktop
    mac-files
    mac-filesystem
    mac-network
    mac-os  # services, install, upgrade
    mac-tools   # os-specific scripts
    mac-users   # settings, permissions, config sync
monitoring/
    elk
    graphana
    riemann
    zabbix-agent
    zabbix-proxy
    zabbix-server
network/
    vpn
    routing
    direct-radio
    ipv6
    nmap        
    netcat
    tcpdump
    wget
    rds
productivity/
    collaboration.md
    editors.md
windows-systems
    ad          
    ca          = web/ca
    dhcp
    dns
    exchange    = email/exchange
    gpo
    iis         = web/iis
    kms
    nps
    rdg
    rds         = network/rds
virt/
    xen
    uml
    kvm
    docker
    hyperv
web/
    apache
    iis
    nginx
    ssl
    ca
windows/
    win-backup
    win-console
    win-desktop
    win-files
    win-filesystem
    win-eventlog
    win-network
    win-os  	# services, install, upgrade, activation
    win-tools   	# os-specific scripts
    win-users
```
