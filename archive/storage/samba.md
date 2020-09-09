# Samba configuration and usage


Create samba user (virtual, no linux login)
```
USER="new-user"
sudo adduser --no-create-home --disabled-password --gecos "" --disabled-login $USER
sudo smbpasswd -a $USER
```


Create log dir, enable log rotation
```
mkdir -p /var/log/samba/sessions
cat << SMB_LOGR > /etc/logrotate.d/samba_sessions
/var/log/samba/sessions/* {
    dayly
    missingok
    rotate 7
    postrotate
        [ ! -f /var/run/samba/nmbd.pid ] || kill -HUP \$(cat /var/run/samba/smbd.pid)
    endscript
    compress
    notifempty
}
SMB_LOGR
```

Samba public share
```
[global]

# AUTH
    workgroup = PUBLIC
    security = user
    map to guest = Bad Password

# NETWORK
    smb ports = 445
    wins support = no
    dns proxy =yes
    # allow Samba to notice (reasonably soon) that a client as disappeared (unlock)
    socket options = TCP_NODELAY SO_KEEPALIVE TCP_KEEPIDLE=30 TCP_KEEPCNT=3 TCP_KEEPINTVL=3

# FILE SERVING OPTIONS
    strict allocate = yes
    vfs objects = acl_xattr
    map acl inherit = yes
    store dos attributes = yes
    follow symlinks = yes
    wide links = yes
    unix extensions = no
    unix charset = UTF-8

# SHARES

[public]
    path = /srv/public
    force user = root
    public = yes
    writable = yes
    comment = public smb share
    printable = no
    guest ok = yes
```

Samba domain member
```
[global]

# AUTH
    realm = SOMEDOMAIN.TLD
    client signing = yes
    client use spnego = yes
    kerberos method = secrets and keytab
    security = ads

# NETWORK
    ...
```

Samba share for macos timemachine backup
* See [Wa Rwick Blog](http://wa.rwick.com/2018/04/08/minimal-ubuntu-time-machine-backup-service/)

```
cd /usr/src
wget https://download.samba.org/pub/samba/stable/samba-4.9.0.tar.gz
tar -xzvf samba-*.tar.gz
cd samba-*
apt-get install -y libreadline-dev git build-essential \
libattr1-dev libblkid-dev autoconf python-dev \
python-dnspython libacl1-dev gdb pkg-config libpopt-dev \
libldap2-dev dnsutils acl attr libbsd-dev docbook-xsl \
libcups2-dev libgnutls28-dev tracker libtracker-sparql-1.0-dev \
libpam0g-dev libavahi-client-dev libavahi-common-dev \
bison flex avahi-daemon avahi-discover avahi-utils libnss-mdns \
mdns-scan
apt-get install --yes libjansson-dev libgpgme11-dev liblmdb-dev libarchive-dev
```

* Starten von samba auf der Konsole
```
smbd --foreground --log-stdout --no-process-group --configfile=/etc/samba/smb.conf
```
