# Linux OS

## Hardening
Security analysis: see [Lsat Tool](http://usat.sourceforge.net)

## Bootstrap, footprint

see [ReduceDebian](https://wiki.debian.org/ReduceDebian)

## SystemD and Units

Links:
* [Systemd Introduction]( https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units)
* [Systemd Units]( https://www.freedesktop.org/software/systemd/man/systemd.service.html)
* [Systemd python inotify](https://pypi.python.org/pypi/sdnotify) and [SD Notify](https://www.freedesktop.org/software/systemd/man/sd_notify.html#)

Unit file

`Type`:
* simple: ExecStart process is main process, running in foreground, not exiting (see oneshot)
* forking: child daemonizes, use PIDFILE= option
* oneshot: start main process which may stop shortly after but stay active in case RemainAfterExit=True
`ExecStart`:
* 1 command except for oneshot type
* prefix by "-" to avoid break on bad exit code
`ExecStartPre=, ExecStartPost`:
* multiple commmand lines, specify multiple times for multiple commands
`ExecStop
* Commands to stop service, workig only after successful start
`ExecStopPost`:
* Cleanup Commands,
`ExecReload`:
* Commands to execute to trigger a configuration reload in the service. Evaluates $MAINPID
* Command(s) shall wait until reload is finished

## SWAP

Linux kernel swappiness parameter values, see [ZFS Article](https://pve.proxmox.com/wiki/ZFS_on_Linux)

| Value|Strategy |
|---|---|
|`vm.swappiness = 0` | The kernel will swap only to avoid an out of memory condition|
|`vm.swappiness = 1` | Minimum amount of swapping without disabling it entirely.|
|`vm.swappiness = 10` | This value is sometimes recommended to improve performance when sufficient memory exists in a system.|
|`vm.swappiness = 60` | The default value.|
|`vm.swappiness = 100` | The kernel will swap aggressively.|

Kernel memory overcommit: set 2

Show which processes use swap

    find /proc -maxdepth 2 -path "/proc/[0-9]*/status" -readable -exec \
        awk -v FS=':' '{
            process[$1]=$2
            sub(/^[ \t]+/,"",process[$1])
        } 
        END {
            if(process["VmSwap"] && process["VmSwap"] != "0 kB") 
                printf "%10s %-30s %20s\n",process["Pid"],process["Name"],process["VmSwap"]
        }' \
    {} \;


## Packages
Show  glibc dependecies

```
lsof | grep libc | awk '{print $1}' | sort | uniq
```
Show  glibc version

```
ldd --version
```

### Centos package management (yum)

Find package containing command

```
yum provides */archivemount
```

Clear cache
```
yum clean packages
yum clean all # reset completely
```

Remove old kernel packages
```
yum install yum-utils
package-cleanup --oldkernels --count=1
```

### Ubuntu package management (apt)

Show Ubuntu Distributions ID
```
lsb_release --short --release
```


Upgrade Ubuntu LTS versions:
```
mount -o remount,exec  /tmp
apt-get update
apt-get dist-upgrade -y
apt-get install --yes update-manager-core ppa-purge
apt-get --purge --yes autoremove
apt-get clean all
# remove package configurations left over from packages that have been removed (but not purged).
sudo apt-get purge $(dpkg -l | awk '/^rc/ { print $2 }')
do-release-upgrade
# y
# Enter
# Enter
# y  # takes several hours
# no, do not restart services
# Reboot: no
apt-get purge -y update-manager-core ppa-purge
apt-get --yes --purge autoremove
apt-get clean all
reboot
```

### Replace distribution
This is not a distribution upgrade but a fresh install of operating system parallel to running OS. It may be necessary to do a manual reset of the computer at the end of this procedure (in case reboot does not work - this depends on OS).
First, the  new operating system is bootstrapped to a temporary dir `/srv/os_new`. This is then copied to a working dir `/srv/os_work` (where os commands are still available). From this working dir, the old operating system is replaced by the new copy.

Filesystem config(`/etc/fstab`) and network config(`/etc/network/interfaces`) are simply copied to new system but may need modifications, depending on os versions.

After rebooting, the old file system is still available under `/srv/os_old`

Example: Upgrade Ubuntu 14.04 > 18.04:

```
for service in rsyslog, mysql, zabbix-proxy1, zabbix-agent1, zabbix-autossh1; do
        /etc/init.d/$service stop
done
```

## Resetting linux server identity
When cloning an os, it may be nececcary to convert the copied system to a new identity.

Adapt to new network card MACs
```
rm /etc/udev/rules.d/70-persistent-net.rules -vf
```

Manually update network configuration
* `/etc/hosts`
* `/etc/hostname`
* `/etc/network/interfaces` # IP siehe oben
* `/etc/ssh/sshd_config`



Optional: re-generate moduli for ssh
```
rm /etc/ssh/moduli /etc/ssh/ssh_host*
tmpfile=$(tempfile)
ssh-keygen -G $tmpfile -b 2048  # 1024 bits was shipped
sudo ssh-keygen -T /etc/ssh/moduli -f $tmpfile
rm $tmpfile
```

replace SSH host keys and those of user "root"
```
host=$(dnsdomainname --fqdn)
date=$(date -Iseconds)}    
mv -v /etc/ssh/ssh_host_rsa_key{,.bak_$date}
mv -v /etc/ssh/ssh_host_ed25519_key{,.bak_$date}
mv -v /etc/ssh/ssh_host_dsa_key{,.bak_$date}
mv -v /etc/ssh/ssh_host_ecdsa_key{,.bak_$date}
sudo ssh-keygen -t rsa     -b 4096 -C $host -N '' -f /etc/ssh/ssh_host_rsa_key
sudo ssh-keygen -t ed25519 -C $host -N '' -f /etc/ssh/ssh_host_ed25519_key
sudo ssh-keygen -t dsa     -C $host -N '' -f /etc/ssh/ssh_host_dsa_key
sudo ssh-keygen -t ecdsa   -C $host -N '' -f /etc/ssh/ssh_host_ecdsa_key

for user in root; do
    echo "Re-creating key for \"$user\""
    sudo su --login $user --command "{
        mv -v ~/.ssh/id_rsa{,.bak_$date
        mv -v ~/.ssh/id_rsa.pub{,.bak_$date
        ssh-keygen -C $user@$host -b 4096 -N '' -f ~/.ssh/id_rsa
    }
    "
done
```

Create new harddrive UUIDs 
```
apt-get install uuid-runtime
tune2fs /dev/sda -U $(uuidgen)
tune2fs /dev/sdb -U $(uuidgen)
```

Festplatten UUIDs in fstab eintragen (manuell!)

Insert new harddrive UUIDs in `/etc/fstab` for *manual editing*
```
blkid /dev/sd* >> /etc/fstab
vim /etc/fstab
```

Recreate Grub config and initrd:

```
update-initramfs -u -k all
update-grub
```

## Load

Caclulate overall CPU usage
```
grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}'
```


multipliers for monitoring load limits (nagios, warning and critical):

| | 1min | 5min | 15min |
|----|----|----|----|
|warning |4|3|2|
|critical|4.5|3.5|3|
    


# LiveCD, Live USB

Best by far: https://willhaley.com/blog/custom-debian-live-environment/
