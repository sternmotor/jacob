Linux Filesystem Operations
===========================

Info
----

Disk drive size in bytes

    lsblk -rnbo size /dev/sda

Display mounted file systems

    mount | column -t

Display only physical filesystems (no swap)

    mount -t btrfs,ext4,ext2,xfs | column -t

Partition UUID

    blkid -o value -s UUID /dev/sda

Show ext4 filesystems

    blkid -t TYPE=ext4 



Smart Checks
------------

* [Thomas Krenn](https://www.thomas-krenn.com/de/wiki/SMART_Tests_mit_smartctl) - short and useful

Show harddrive info
```
sudo smartctl -i /dev/sda
```

Run background check

```
sudo smartctl -t short /dev/sda
```

Retrieve results of background check

```
sudo smartctl -l selftest /dev/sda
```


Partitions
----------

Find and all mount points below directory in reverse order
* split output on " type " to fetch mount points with whitespace
* grep "on /mnt" and " on /mnt/xxx"
* print mount points in reverse order

    MOUNT_POINT='/mnt'
    sudo mount \
    | awk -F ' type ' '{print $1" "}' \
    | grep -E "on $MOUNT_POINT[/ ]" \
    | awk -F ' on ' '{print $2}' \
    | sort -r


Unmount all mountpoints, use code above to fill pipe

    ... | while read mp; do
        while umount $mp -l 2>/dev/null; do
            echo "un-mounting $mp ... "
        done
    done

### GPT partition handling

Show GPT partitions
    DRIVE=/dev/sda
    parted --script $DRIVE print free


Remove GPT partition scheme (at begin and end of DRIVE)
```bash
DRIVE=/dev/sda
# find end of disk in blocks, remove table entries there
dd if=/dev/zero of=$DRIVE bs=512 count=2 status=none \
&& seek_block=$(($(blockdev --getsz $DRIVE) - 2)) \
&& dd if=/dev/zero of=$DRIVE bs=512 count=2 seek=$seek_block status=none
```

Create UEFI partition scheme
```bash
DRIVE=/dev/sda
MACHINE_NAME=web1
UEFI_SIZE=250           # MB
SIZE=$((5 * 1024)) # MB
SWAP_SIZE=$((1 * 1024)) # MB
parted --align optimal --script $DRIVE -- mklabel gpt \
&& parted --align optimal --script $DRIVE -- mkpart primary fat32 2MB ${UEFI_SIZE}MB \
&& parted                 --script $DRIVE -- name 1 "${MACHINE_NAME}_UEFI" \
&& parted                 --script $DRIVE -- set 1 boot on \
&& END=$(( $UEFI_SIZE + $SIZE )) \
&& parted --align optimal --script $DRIVE -- mkpart primary ext4 ${UEFI_SIZE}MB ${END}MB \
&& parted                 --script $DRIVE -- name 2 "${MACHINE_NAME}_ROOT"  \
&& SWAP_END=$(( $END + $SWAP_SIZE )) \
&& run_debug parted --align optimal --script $DRIVE -- mkpart primary linux-swap ${END}MB ${SWAP_END}MB \
&& run_debug parted                 --script $DRIVE -- name 3 "${MACHINE_NAME}_swap"  
```

Add data partition to UEFI partition scheme
```bash
DRIVE=/dev/sda
SIZE=$((50 * 1025)) # MB
START=$( parted $DRIVE unit MB print free | grep "Free Space" | tail -n -1 | awk '{print $1}')
END=$((${START/MB/} + $SIZE))
parted --align optimal --script $DRIVE -- mkpart primary linux-swap ${START}MB ${END}MB  
```

Calculate swap partition size from memory footprint

    MemKB=$(cat /proc/meminfo | grep MemTotal: | awk '{print $2}')
    SWAP_SIZE=$(( $MemKB / 1024 / 2 ))      # swap size in MB


Maximize last partition, do not forget to fetch new UUID after procedure and
update `/etc/fstab`!

    DRIVE='/dev/sda'
    PARTITION=3
    parted $DRIVE rm $PARTITION
    START=$(parted $DRIVE print free --machine | tail -n 1 | grep ':free;' | cut -d ':' -f 2)
    parted --align optimal $DRIVE unit MB mkpart 'data' ext2 $START 100%


Workflow for expanding virtual drive in the middle of partition table (data
loss on last partition!)

* stop VM
* expand VHD/ Drive to wanted size
* start VM, login via SSH

        apt-get install --yes parted
        parted /dev/sda print free

* resize `/dev/sda2` (system), re-create `/dev/sda3` (e.g. swap)
    * disable swap

            DRIVE='/dev/sda'
            PARTITION=3
            swapoff $DRIVE$PARTITION
            parted $DRIVE rm $PARTITION
            parted $DRIVE print

    * expand partition2

            DRIVE='/dev/sda'
            PARTITION=2
            ADD_ROOT_SIZE=100MB
            CURRENT_END=$(parted $DRIVE print --machine | grep "^${PARTITION}:" | cut -d ':' -f 3)
            NEW_END="$(( ${ADD_ROOT_SIZE/MB/} + ${CURRENT_END/MB/} ))MB"
            echo "Moving end of partition $DRIVE${PARTITION} from $CURRENT_END to $NEW_END"
            parted $DRIVE resizepart ${PARTITION} Yes $NEW_END
            resize2fs $DRIVE$PARTITION

    * re-create swap

            DRIVE='/dev/sda'
            PARTITION=3
            Start=$(parted $DRIVE print free --machine | tail -n 1 | grep ':free;' | cut -d ':' -f 2)
            parted --align optimal $DRIVE unit MB mkpart "swap" linux-swap $Start 100%
            mkswap --label "$(hostname)_swap" $DRIVE$PARTITION
            swapon $DRIVE$PARTITION
