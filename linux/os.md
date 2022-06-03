Linux OS
========


View kernel messages with readable timestamp

    dmesg -T

Performance 
-----------

Show top 10 cpu consumers

    ps auxf | (sed -u 1q; sort -nr -k 3) | head -11

Show top 10 memory consumers

    ps auxf | (sed -u 1q; sort -nr -k 4) | head -11

SystemD
-------

### System control


Shutdown without acpi hang up at end of shutdown process (`halt` problem)

    systemctl poweroff

Parseable list of installed services

    systemctl --type=service --plain --no-legend

### Logging

List all services with state

    systemctl

View single service log, tail -f mode

    journalctl -fu <service>


Enable persistent journald log (to compare boot process messages)

* prepare

    mkdir -p /var/log/journald
    systemd-tmpfiles --create --prefix /var/log/journald

* edit `/etc/systemd/journald.conf`:

    [Journal]
    Storage=Persistent
    RateLimitBurst=0
    RateLimitIntervalSec=0

* enable changes

    systemctl restart journald


### Unit design

Links:
* [Systemd Introduction]( https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units)
* [Systemd Units]( https://www.freedesktop.org/software/systemd/man/systemd.service.html)
* Systemd Exec options: (e.g. LimitNOFile): `man systemd.exec`
* [Systemd python inotify](https://pypi.python.org/pypi/sdnotify) and [SD Notify](https://www.freedesktop.org/software/systemd/man/sd_notify.html#)


Unit file
`Type`

* `simple`: ExecStart process is main process, running in foreground, not exiting
* `forking`: child daemonizes, use PIDFILE= option
* `oneshot`: start main process which may stop shortly after but stay active in case `RemainAfterExit=True`


`ExecStart`

* 1 command except for oneshot type
* prefix by `-` to avoid break on bad exit code

`ExecStartPre=, ExecStartPost`

* multiple commmand lines, specify multiple times for multiple commands

`ExecStop`

* Commands to stop service, workig only after successful start

`ExecStopPost`

* Cleanup Commands

`ExecReload`

* Commands to execute to trigger a configuration reload in the service. Evaluates `$MAINPID`
* Command(s) shall wait until reload is finished


Load, CPU usage
---------------

Calculate overall CPU usage per cpu

    awk '/cpu /{print "Avg CPU usage: "($2+$4)*100/($2+$4+$5)}' /proc/stat



Sensible multipliers for monitoring load limits

| | 1min | 5min | 15min |
|----|----|----|----|
|warning |4|3|2|
|critical|4.5|3.5|3|


Kernel parameters
-----------------
load and display kernel variables defined permanently in system config

	sysctl -p

set kernel variables temporarily, check for errors

	sysctl -w variable=value

set kernel variables permanently, set instantly

	echo "variable = value" >> /etc/sysctl.conf
	sysctl -p



Memory and Swap
---------------

Retrieve total memory (scripting) in MB (example below)

	awk '/MemTotal:/{print $2/1024}' /proc/meminfo


### Troubleshooting memory issues

Trouble:

* sysctl: `setting key "kernel.msgmni": Invalid argument`
* httpd: `No space left on device: AH00023: Couldn't create the ssl-cache mutex`

Shot:

* see [IBM documentation](https://www.ibm.com/support/knowledgecenter/SSEPGG_11.5.0/com.ibm.db2.luw.qb.server.doc/doc/t0008238.html)
* rules for sysctl settings
	* max shared mem segments: `kernel.shmmni` to 256 times the size of RAM (in GB)
	* max message queues: `kernel.msgmni` to 1024 times the size of RAM (in GB)
	* semaphore limits: `kernel.sem = 250 256000 32 1024` (max semaphores per array, max semaphores system wide, max ops per semop call, max number of arrays)
		
* do it 

        awk '/MemTotal:/{print "kernel.shmmni = "int($2/1024/1024*256)}' \
        /proc/meminfo >> /etc/sysctl.conf
        awk '/MemTotal:/{print "kernel.msgmni = "int($2/1024/1024*1024)}' \
        /proc/meminfo >> /etc/sysctl.conf
        echo 'kernel.sem = 250 256000 32 1024' >> /etc/sysctl.conf
        sysctl -p

* validate (e.g. after reboot)

        ipcs -l

* note: for Redhat systems > 32GB: Centos 7.8 limit for kernel.msgmni, kernel.semmni, and kernel.shmmni is 32768 - fix by adding `ipcmni_extend` option to `GRUB_CMDLINE_LINUX`.


### Swap setup

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
    {} +



### Shared Memory

Read [here][shm_intro] - good overview

* available total shared memory

    cat /proc/sys/kernel/shmall

* max bytes for a shared memory segment

    cat /proc/sys/kernel/shmmax

* max number of shared mem segments

    cat /proc/sys/kernel/shmmni

* list all shared memory segments

    ipcs -m

* show processes using segments, cpid= createor pid, lpid = last detached process

    ipcs -pm



[shm_intro]: https://datacadamia.com/os/linux/shared_memory

Hardening
---------

Security analysis: see [Lsat Tool](http://usat.sourceforge.net)


Packages, Software, Distributions
---------------------------------

Show distribution info

    lsb_release --all


### Redhat/Centos package management (yum)

Find package containing command

    yum provides */archivemount

Clear cache

    yum clean all

Remove old kernel packages

    yum install yum-utils
    package-cleanup --oldkernels --count=1


### System libs

Show  glibc dependencies

    lsof | grep libc | awk '{print $1}' | sort | uniq

Show  glibc version

    ldd --version


Cron jobs
---------

    SHELL=/bin/bash
    PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin
    MAILTO=root
    # Example of job definition:
    # .---------------- minute (0 - 59)
    # |  .------------- hour (0 - 23)
    # |  |  .---------- day of month (1 - 31)
    # |  |  |  .------- month (1 - 12) OR jan,feb,mar,apr ...
    # |  |  |  |  .---- day of week (0 - 6) (Sunday=0 or 7) OR sun,mon,tue,wed,thu,fri,sat
    # |  |  |  |  |
    # *  *  *  *  * user-name  command to be executed


Logrotation
-----------

Edit `/etc/logrotate.d/somelog` - needs `pigz` parallel compressor tool

    /var/log/somelog
    {
        compress
        delaycompress
        compresscmd /usr/bin/pigz
        copytruncate
        daily
        missingok
        notifempty
        rotate 5
        size 64M
    }


NTP
---

Update ntp time at dns server

    ntpdate -u $(awk '/nameserver/{print $2}' /etc/resolv.conf)

Resetting linux server identity
-------------------------------
When cloning an os, it may be nececcary to convert the copied system to a new identity.

Adapt to new network card MACs

    rm /etc/udev/rules.d/70-persistent-net.rules -vf

Manually update network configuration
* `/etc/hosts`
* `/etc/hostname`
* `/etc/network/interfaces` # IP siehe oben
* `/etc/ssh/sshd_config`


Re-generate moduli for ssh (optinally)

    rm /etc/ssh/moduli /etc/ssh/ssh_host*
    tmpfile=$(tempfile)
    ssh-keygen -G $tmpfile -b 2048  # 1024 bits was shipped
    sudo ssh-keygen -T /etc/ssh/moduli -f $tmpfile

Replace SSH host keys and those of user "root"

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

    sudo su - --command "{
        mv -v ~/.ssh/id_rsa{,.bak_$date
        mv -v ~/.ssh/id_rsa.pub{,.bak_$date
        ssh-keygen -C root@$(hostname -f) -b 4096 -t ed25519 -N '' -f ~/.ssh/id_ed25519
    }"

Create new harddrive UUIDs 
    apt-get install uuid-runtime
    tune2fs /dev/sda -U $(uuidgen)
    tune2fs /dev/sdb -U $(uuidgen)


Insert new harddrive UUIDs in `/etc/fstab` for *manual editing*

    blkid /dev/sd* >> /etc/fstab
    vim /etc/fstab

Recreate Grub config and initrd:

    update-initramfs -u -k all
    update-grub

    
Bootstrap, LiveUSB
------------------


Bootstrapping Debian: see [ReduceDebian](https://wiki.debian.org/ReduceDebian)

LiveCD, Live USB, best by far: https://willhaley.com/blog/custom-debian-live-environment/

Troubleshooting
---------------



kernel:NMI watchdog: BUG: soft lockup - CPU#1 stuck for 44s! 
    * read [this blog entry](https://blog.seibert-media.net/blog/2017/10/05/it-tagebuch-linux-was-sind-cpu-lockups/) - in short:
	* soft lockup: kernel task does not release cpu time to other processes 
	* reasons: high load or very high levels of cpu time overcommit
    * this is clearly a kernel process hangup (no process in user space can cause a soft lockup)
    * try updating kernel, play with cpu overcommit on virtualized systems and watch load
