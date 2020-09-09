# sFTP

configure `/etc/ssh/sshd_config`, important section:
```
subsystem sftp internal-sftp
match group sftp
    PermitRootLogin no
    PasswordAuthentication yes
    ChrootDirectory /var/lib/sftp/%u # chmod 0750; chown 0:0
    X11Forwarding no
    AllowTcpForwarding no
    Banner none
    ForceCommand internal-sftp
```

create dir structure, home dirs for authorized keys file
```
install --mode 0750 --owner root --group root -d /var/lib/sftp
groupadd sftp 
useradd -G sftp -s /sbin/nologin -m -d /home/username  username
install --mode 0750 --owner root --group root -d /var/lib/sftp/username
touch /home/username/.ssh/authorized_keys
chmod 0600 /home/username/.ssh/authorized_keys
chown username:username /home/username/.ssh/authorized_keys
passwd username
```

create selinux exception (centos linux)
```
setsebool -P ssh_chroot_rw_homedirs on
systemctl restart sshd
```

bind mount system directories into sftp space
```
echo '/var/www/app/upload /var/lib/sftp/username/share1 none bind 0 0' >> /etc/fstab
mkdir /var/lib/sftp/username/share1
mount -a
```


