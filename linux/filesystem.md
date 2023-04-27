Linux file system manipulation
==============================

Copy files
----------

rsync directory structure, only:

    rsync -av --include='*/' --exclude='*' /path/to/src /path/to/dest/


Copy devices
------------

`dd` progress: specifying a bs= parameter that aligns with the disks buffer memory will get the most performance from the disk.

    dd status=progress ...


Pipe transfer of disk devices
-----------------------------

slow but convient via ssh 

    pv /dev/sdb | zstd -1 | ssh some_host.example.com 'zstd -dcf > /dev/sdb'

faster for big drives, no ssh, requires netcact-openbsd
    # target
    which firewall-cmd 2> /dev/null && firewall-cmd --add-port=7000/tcp
    netcat -l 7000 | pv | zstd -dcf > /dev/sdb

    # source
    pv /dev/sdb | zstd -1 | netcat -N target.example.com 7000


MBR partitions
-----------------

Re-read partition table - try:

    partprobe /dev/sdX 
    blockdev --rereadpt /dev/sdX

Expand last partition to maximum available space - without reboot

    yum install -y cloud-utils-growpart
    growpart /dev/sdb 3
    resize2fs /dev/sda3

`cfdisk` writes cleanest partition tables compared to `fdisk` oder MS_DOS tools

* start with new partition table

    cfdisk -z /dev/vdd


`sfdisk` allows dumping and cloning partition tables



GPT partitions
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

Make partition accessible directly - for example: mount lvm volumes sub-partitions:

    kpartx -av /dev/vg0/test
    mount /dev/vg0/test1 /mnt
    
Remove mount and mapping

    umount -l /mnt
    kaprtx -dv /dev/vg0/test


### LVM

Short but slower transport: use ssh in a loop

    TARGET=some-server.example.com
    VG=vg0
    lvs --noheadings --options lv_name,lv_size \
    | grep "data" \
    | while read device size; do
       ssh -n $TARGET "lvcreate -Wn --size $size --name $device $VG" \
       && pv /dev/vol1/$device \
          | zstd -1 \
          | ssh $TARGET "zstd -dcf > /dev/$VG/$device"
    done


Fastest transport, manually with no ssh - requires `pv`, `netcat`, `zstd`

1. source: list volumes and sizes

        lvs --noheadings --options lv_name,lv_size

2. target: create emtpy volume, enable listener, wait for data

        which firewall-cmd 2> /dev/null && firewall-cmd --add-port=7000/tcp
        lvcreate -Wn --size <vol_size> --name <vol_name> vg0 
        nc -l 7000 | pv | zstd -dcf  > /dev/vg0/<volname>

3. source: start transfer, requires netcat-openbsd pv zstd 

        pv /dev/vg0/$device | zstd -1 | nc -N <TARGET_HOST> 7000


Option: create and remove LVM snapshot before/after transfer

    lvcreate -L 20G -s -n diskname-snap /dev/vg0/diskname
    lvremove /dev/mapper/vg0-diskname-snap


Filesystem cache
------------------

May run into swapping while bigger (cp) operations, clear like

    echo 3 > /proc/sys/vm/drop_caches
    swapoff -a && swapon -a


EXT Filesystem
--------------

Expand partition or raw disk's file system to maximum available space

    sudo resize2fs /dev/somedisk


Shrink file system on partitionless lvm to 50GB

    e2fsck -f /dev/vg0/some_device
    resize2fs /dev/vg0/some_device 50G
    lvresize -L 50g /dev/some_device


BTRFS Filesystem
----------------

### Maintenance

TODO: https://github.com/kdave/btrfsmaintenance


Defragment

    sudo btrfs filesystem defrag -c /srv


Fix btrfs error "no space left on device" but du-csh looks good:

    # tmux + start
    btrfs balance start --full-balance /srv/ && exit

Status for rebalance

    btrfs fi balance status /srv

Show subvolumes

    sudo sync
    sudo btrfs subvolume list /srv
    echo -e "subvol\tqgroup\ttotal\tunshared"
    while read g r e; do
        group=${g##*/}
        name="${volName[group]:--}"
        echo $name $g \
             $(numfmt --to=iec --round=nearest $r) \
             $(numfmt --to=iec --round=nearest $e)
    done < <(sudo btrfs qgroup show --raw /srv | tail -n+3) | column -t
    

Expand partition or raw disk's file system to maximum available space

    sudo btrfs filesystem resize max /dev/some-disk

Get compressed ("used") and compressed + reserved ("total") space

    sudo btrfs filesystem df /srv

Re-compress MySQL partitions (inndob with DirectIO circumventing compression):

    sudo btrfs defragment  -rcf <path>
    sudo btrfs filesystem df <path>

Create compressed file system, mount options

    mkfs.btrfs -L SRV /dev/vol1/srv
    echo '/dev/vg0/srv /srv btrfs defaults,noatime,nofail,acl,nodev,nosuid,compress-force=zstd:1 0 0' >> /etc/fstab
    mount /srv

Troubleshooting "btrfs_replay_log:2288: errno=-22 unknown (Failed to recover log tree)"

    btrfs check /dev/vdb
    btrfs rescue zero-log /dev/vdb
    btrfs scrub start /dev/vdb  # healthcheck
    watch -n 10 btrfs scrub status /dev/vdb


Install and use compsize for checking btrfs uncompressed size


    yum install -y git gcc-c++ btrfs-progs-devel \
    && git clone https://github.com/kilobyte/compsize compsize-git \
    && cd compsize-git \
    && make \
    && make install \
    && cd .. \
    && rm -rf compsize-git

    yum remove -y git gcc-c++ btrfs-progs-devel
    yum autoremove

    compsize -x /srv
    

Permissions
-----------

Quick way to set (override) ACLs and linux permissions, enabling inheritance
via default acls

                                                                        
    TARGET=/etc/logrotate.d /etc/filebeat/conf.d
    sudo chown -R root:root $TARGET
    sudo setfacl -R --set u:r.kuehle:rwX,u:48:rwX,u::rwX,g::rX,o::- $TARGET
    for t in $TARGET; do getfacl -p --access $t | sudo setfacl -dRM - $t; done 

Remove `executable` permissions from file (e.g. in webroot)

    find /srv/tokenizer -type f -exec chmod a-x {} +

Speed test
----------
Primary tests:

1. throughput/bandwitdh [MB/sec]: large, sequential r/w measurement
2. latency [ms]: seek time for mechanical disks
3. IOPS [1]: number of random read/write disk operations can be serviced, 
   tested at 4K block size  usually

Easy Peasy -make sure to provide 2xRAM free disk space for testing

    curl -o gobonniego -L https://github.com/cunnie/gobonniego/releases/download/1.0.9/gobonniego-linux-amd64
    chmod +x gobonniego
    ./gobonniego -dir /mnt/ -size 10


FIO

Split read and write test, Direct IO (no system buffers), 4K/1MB blocksize:

    lvcreate -L 10G vol1 -n fiotest

    TIME=60
    FS=/dev/vol1/fiotest
    PARALLEL=3
    for bs in 4k 1m; do
        for rw in read write; do
            fio --rw=$rw --name="$rw $bs $FS" --bs=$bs --direct=1 \
            --filename=$FS --numjobs=$PARALLEL --ioengine=libaio --iodepth=32 \
            --refill_buffers --group_reporting --runtime=$TIME --time_based
        done
    done


Speed test for etcd - see [etcd use case][fio_etcd]: "99th percentile of this metric should be less than 10ms for storage to be considered fast enough"

* start 

        fio --rw=write --ioengine=sync --fdatasync=1 --directory=test-data \
        --size=22m --bs=2300 --name=mytest

* output: analyse `fdatasync` (fio 3.5+)

        fsync/fdatasync/sync_file_range:
            sync (usec): min=534, max=15766, avg=1273.08, stdev=1084.70
            sync percentiles (usec):
            | 1.00th=[ 553], 5.00th=[ 578], 10.00th=[ 594], 20.00th=[ 627],
            | 30.00th=[ 709], 40.00th=[ 750], 50.00th=[ 783], 60.00th=[ 1549],
            | 70.00th=[ 1729], 80.00th=[ 1991], 90.00th=[ 2180], 95.00th=[ 2278],
            | 99.00th=[ 2376], 99.50th=[ 9634], 99.90th=[15795], 99.95th=[15795],
            | 99.99th=[15795]

* result: `99.00th=[ 2376]` = 2.4ms - this is rather close to 10ms considering
  other I/O activities


[fio_etcd]: https://www.ibm.com/cloud/blog/using-fio-to-tell-whether-your-storage-is-fast-enough-for-etcd


## mounted filesystems

fetch total size of all local disks - size GB, types are limited

    df -BG --total --output=size,target --type=ext4 --type=btrfs --type=xfs
