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

`dd` usage is not handled here, replaced by `nc`.


### Create disks with right size on target site

LVM example:

1. on source host - retrieve size of logical volume to create on remote hostlvdisplay --units k "/dev/$VGNAME/$LVNAME" | LANG=C awk '/LV Size/{print $3}'

        LANG=C lvs --units k --options lv_name,lv_size

2. on destination host:

        LV_NAME= # << put name fro step 1 here
        LV_SIZE= # << put value from step 1 here
        VG_NAME=$(vgs --noheadings --options vg_name | awk '{print $1}')

        LANG=C lvcreate -Wn --size ${LV_SIZE}kiB --name $LV_NAME $VG_NAME


### Transfer disk data

Required packages on both servers:  `zstd`, `pv`, `netcat`

Simple: use slower ssh connection from source to host 

    TARGET=target.example.com
    pv /dev/$VG_NAME/$LV_NAME | zstd -T0 --fast | ssh $TARGET "zstd -T0 -dcf > /dev/$VG_NAME/$LV_NAME"


Fast: using `nc` is faster than ssh but needs a listener to be run on TARGET
site.  Make sure target and source device have same size. There is no need to
have a ssh connection between both peers. On source and target, uncompressed
size is displayed: 

1. on destination host

        nc -l 7000| zstd -T0 --fast -dcf | pv > /dev/$VG_NAME/$LV_NAME

2. on source host

        TARGET=target.example.com
        LV_NAME= # << put name fro step 1 here
        VG_NAME=$(vgs --noheadings --options vg_name | awk '{print $1}')
        pv /dev/$VG_NAME/$LV_NAME | zstd -T0 | nc $TARGET  7000

Option: create and remove LVM snapshot before/after transfer

    lvcreate -L 20G -s -n diskname-snap /dev/vg0/diskname
    lvremove /dev/mapper/vg0-diskname-snap


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


    




