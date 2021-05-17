Linux file system manipulation
==============================

Copy files
----------

rsync directory structure, only:

    rsync -av --include='*/' --exclude='*' /path/to/src /path/to/dest/



Copy devices
------------

`dd` progress: specifying a bs= parameter that aligns with the disks buffer memory will get the most performance from the disk.

    dd status=progress 



Pipe transfer of disk devices
-----------------------------

See "LVM" section for another example. `dd` usage is not handled here, replaced by `nc`.


### nc

Required packages on both servers:  `zstd`, `pv`, `netcat`

Simple: use slower ssh connection from source to host 

    pv /dev/<device> | zstd -T0 | ssh target.example.com "zstd -T0 -dcf > /dev/<device>"


Fast: using `nc` is faster than ssh but needs a listener to be run on TARGET site.
Make sure target and source device have same size. 

* on destination host (show compressed size):

        nc -l 7000| pv | zstd -T0 -dcf > /dev/<device>  

* on source host (show raw data size)

        pv /dev/<device> | zstd -T0 | nc target.example.com 7000


LVM
---

Create and remove snapshot

    lvcreate -L 20G -s -n diskname-snap /dev/vg0/diskname
    lvremove /dev/mapper/vg0-diskname-snap

Pipe transfer of multiple disks with snapshot, lv creation and remote operation
from source on destination host, requires "pv", "zstd" and "netcat" an
exchanged ssh keys:

    yum install -y zstd pv nc

Run

    TARGET=remote_server.example.com
    LVS="server1.example.com_root server1.example.com_srv"
    SNAP_SIZE=10G
    VG=vg0

    for lv_name in $LVS; do
        lv_path="/dev/$VG/$lv_name"
        lv_size=$(lvdisplay --units k $lv_path | awk '/LV Size/{print $3}')

        ssh -n $TARGET "lvcreate -Wn --size ${lv_size}kiB --name $lv_name $VG"
        lvcreate --snapshot --name ${lv_name}_transfersnap --size $SNAP_SIZE $lv_path
        ssh -n $TARGET "nc -l 7000| pv | zstd -T0 -dcf > $lv_path" &
        time pv $lv_path | zstd -T0 --fast | nc $TARGET 7000
        fg 1
        lvremove --yes ${lv_path}_transfersnap
    done


MBR Partitionen
-----------------

`cfdisk` writes cleanest partition tables compared to `fdisk` oder MS_DOS tools

* start with new partition table

    cfdisk -z /dev/vdd


`sfdisk` allows dumping and cloning partition tables

Expand last partition to maximum available space

    yum install -y cloud-utils-growpart
    growpart /dev/sdb 4



GPT Partitionen
----------------

Create GPT partition scheme

* reset partition layout and mbr

    ROOT_DRIVE=/dev/sdb
    dd if=/dev/zero of=$ROOT_DRIVE bs=512 count=2 status=none \
    && seek_block=$(($(blockdev --getsz $ROOT_DRIVE) - 2)) \
    && dd if=/dev/zero of=$ROOT_DRIVE bs=512 count=2 seek=$seek_block status=none

* write new partitions

    parted    --align optimal --script $ROOT_DRIVE -- mklabel gpt \
    && parted --align optimal --script $ROOT_DRIVE -- mkpart ${HOST}_BIOS fat32 2048s 4095s \
    && parted                 --script $ROOT_DRIVE -- set 1 bios_grub on \
    && parted --align optimal --script $ROOT_DRIVE -- mkpart BOOT ext4 4095s 512MiB \
    && parted --align optimal --script $ROOT_DRIVE -- mkpart RESCUE ext4 512Mib 10GiB \
    && parted --align optimal --script $ROOT_DRIVE -- mkpart LIVE btrfs 10GiB 100% \
    && parted $ROOT_DRIVE print

* format drives (boot, rescue)

    sleep 1 \
    && mkfs.ext4 -q -G 4096 -qF -m 0 -L "LIVE_BOOT" ${ROOT_DRIVE}2 \
    && mkfs.ext4 -q -G 4096 -qF -m 5 -L "RESCUE" ${ROOT_DRIVE}3


EXT Filesystem
--------------

Expand partition or raw disk's file system to maximum available space

    sudo resize2fs /dev/somedisk


BTRFS Filesystem
----------------

Expand partition or raw disk's file system to maximum available space

    sudo btrfs filesystem resize max /dev/some-disk

Get compressed ("used") and compressed + reserved ("total") space

    sudo btrfs filesystem df /srv

Re-compress MySQL partitions (inndob with DirectIO circumventing compression):

    sudo btrfs defragment  -rcf <path>
    sudo btrfs filesystem df <path>

Create compressed file system 

    mkfs.btrfs -L SRV /dev/vol1/srv
    echo '/dev/mapper/bg0-srv /srv btrfs defaults,noatime,acl,nodev,nosuid,compress=zstd 0 0' >> /etc/fstab
    mount /srv


Permissions
-----------

Quick way to set (override) ACLs and linux permissions, enabling inheritance
via default acls

                                                                        
    TARGET=/etc/logrotate.d /etc/filebeat/conf.d
    sudo chown -R root:root $TARGET
    sudo setfacl -R --set u:r.kuehle:rwX,u:48:rwX,u::rwX,g::rX,o::- $TARGET
    for t in $TARGET; do getfacl -p --access $t | sudo setfacl -dRM - $t; done 

Remove `executable` permissions from file (e.g. in webroot)

    find /srv/tokenizer -type f -exec chmod a-x {} \;


    




