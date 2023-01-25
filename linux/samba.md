# Samba fileserver

## AD joined samba server

edit `/etc/samba/smb.conf`
```
# Configuration file for the Samba suite for Debian GNU/Linux,
# maintaining AD join

#======================= Global Settings =======================

[global]
# identification and network
    workgroup = EXAMPLE
    realm = DOMAIN.EXAMPLE.COM
    smb ports = 445

# security options
    client signing = yes
    client use spnego = yes
    kerberos method = secrets and keytab
    security = ads

# fileserver options
    log file = "/var/log/samba/TO_%L_%i_FROM_%I.log
    interfaces = lo 127.0.0.1 some-ip
    bind interfaces only = yes
    strict allocate = yes
    vfs objects = acl_xattr
    map acl inherit = yes
    store dos attributes = yes
    follow symlinks = yes
    wide links = yes
    unix extensions = no
    unix charset = UTF-8

[backup]
    path = /media/USBFixed/backup
    read only = no
```

## Authentification

### Local

Loop for creating (unix)  accounts on server and in samba database

    USERS='user1 user2 user3'
    for ID in $USERS; do
        PW=$(pwgen -Bnc 10 1)
        useradd -s /sbin/nologin $ID
        echo "$ID : $PW"
        echo -n "\n$PW\n$PW" | smbpasswd -s -a $ID
    done


### LDAP

### FreeIPA


## SystemD client: samba automounter

edit `/etc/systemd/system/media-example.mount`

```
[Unit]
  Description=example mount definition
  Requires=network-online.target
  After=network-online.service

[Mount]
  What=//10.1.0.150/repository
  Where=/media/example
  Options=ro,iocharset=utf8,guest
  Type=cifs

[Install]
  WantedBy=multi-user.target
```

edit `/etc/systemd/system/media-example.automount`

```
[Unit]
  Description=automatic example mounter
  Requires=network-online.target
  After=network-online.service

[Automount]
  Where=/media/example
  TimeoutIdleSec=10

[Install]
  WantedBy=multi-user.target
```

activate
```
install --mode 0750 --owner root --group root --directory /media/example
systemctl daemon-reload
systemctl enable media-example.automount
systemctl restart media-example.automount
```

## Windows interaction

install WSDD on my samba machine so Windows can find them more easily

    sudo apt install -y wsdd

## Simple debugging

Debug and foreground start commands for samba server

    testparm
    smbd --foreground --log-stdout --no-process-group --configfile=/etc/samba/smb.conf

High logging verbosity in `smb.conf`:    

    [global]
    log level    = 3 passdb:5 auth:10 winbind:2


Debug smb connection - most verbose option

    smbclient -d 10 -U johndoe //file-server-address/Share-Name.
    

## Connect to LDAP
