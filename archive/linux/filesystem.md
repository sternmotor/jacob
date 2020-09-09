# Linux Filesystem

## SMART

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


### Links

* [Thomas Krenn](https://www.thomas-krenn.com/de/wiki/SMART_Tests_mit_smartctl) - short and useful



## Partitionen

Print partition UUID
```
blkid /dev/sdb  -o value -s UUID
```

Retrieve all local file systems, sorted by mount point, mounted fs only
* GOOD - `df` shows first mountpoint for devices
    ```
    sudo df \
    --local \
    --output=source,fstype,target \
    --exclude-type devtmpfs \
    --exclude-type tmpfs \
    | tail -n +2
    ```
* BAD - show last mount only in case there are multiple mountpoints
    ```
    sudo lsblk \
        --sort MOUNTPOINT \
        --list \
        --noheadings \
        --paths \
        --output NAME,FSTYPE,MOUNTPOINT
    ```
* check `findmnt` command

Find and all mount points below directory in reverse order
* split output on " type " to fetch mount points with whitespace
* grep "on /mnt" and " on /mnt/xxx"
* print mount points in reverse order

    ```
    MOUNT_POINT='/mnt'
    sudo mount \
    | awk -F ' type ' '{print $1" "}' \
    | grep -E "on $MOUNT_POINT[/ ]" \
    | awk -F ' on ' '{print $2}' \
    | sort -r
    ```
Unmount all mountpoints, use code above to fill pipe
    ```
    ... | while read mp; do
        while umount $mp -l 2>/dev/null; do
            echo "un-mounting $mp ... "
        done
    done
    ```

### Change UUID of file systems

```bash
sudo apt-get install -y uuid-runtime
```

Find all ext4 partitions, change UUID, update fstab
```bash
Ext4Partis=$(sudo blkid -t TYPE="ext4" | cut -d ':' -f1)
for partition in $Ext4Partis; do
    OldUUID=$(sudo blkid $partition -o value -s UUID)
    NewUUID=$(sudo blkid $partition -o value -s UUID)
    sudo tune2fs -O ^uninit_bg $partition
    sudo tune2fs $partition -U $(uuidgen)
    sudo tune2fs -O +uninit_bg $partition
    sudo sed -i "s|$OldUUID|$NewUUID|g" '/etc/fstab'
    if grep -q "$NewUUID" '/etc/fstab'
    then
        echo "$partition: $OldUUID > $NewUUID"
    else
        echo "ERROR: could not update fstab for partition UUID update $OldUUID > $NewUUID"
    fi
done
```
Change UUID of swap partitions, update fstab
```bash
# update uuid for swap partitions
SwapPartis=$(sudo blkid -t TYPE="swap" | cut -d ':' -f1)
for partition in $SwapPartis; do
    OldUUID=$(sudo blkid $partition -o value -s UUID)
    NewUUID=$(sudo blkid $partition -o value -s UUID)
    swaplabel --uuid $NewUUID $partition
    sudo sed -i "s|$OldUUID|$NewUUID|g" '/etc/fstab'
    if grep -q "$NewUUID" '/etc/fstab'
    then
        echo "$partition: $OldUUID > $NewUUID"
    else
        echo "ERROR: could not update fstab for partition UUID update $OldUUID > $NewUUID"
    fi
done

Update grub bootloader und initrd

```bash
update-initramfs -u -k all
update-grub
```

### GPT partition handling

Show GPT partitions
```bash
DRIVE=/dev/sda
parted --script $DRIVE print free
```


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
```bash
MemKB=$(cat /proc/meminfo | grep MemTotal: | awk '{print $2}')
SWAP_SIZE=$(( $MemKB / 1024 / 2 ))      # swap size in MB
```

Disk drive size in bytes
```bash
DRIVE=sda
lsblk --raw --bytes | grep -w "^$DRIVE" | cut -d ' ' -f 4
```


Re-create last partition in table (data loss!) - fetch UUID after proecudre and update `/etc/fstab`!
```bash
DRIVE='/dev/sda'
PARTITION=3
swapoff $DRIVE$PARTITION
parted $DRIVE rm $PARTITION
Start=$(parted $DRIVE print free --machine | tail -n 1 | grep ':free;' | cut -d ':' -f 2)
parted --align optimal $DRIVE unit MB mkpart "swap" linux-swap $Start 100%
mkswap --label "$(hostname)_swap" $DRIVE$PARTITION
swapon $DRIVE$PARTITION
```


Workflow for expanding virtual drive in the middle of partition table (data loss on last partition!)

* stop VM
* expand VHD/ Drive to wanted size
* start VM, login via SSH
    ```bash
    apt-get install --yes parted
    parted /dev/sda print free
    ```
* resize `/dev/sda2` (system), re-create `/dev/sda3` (e.g. swap)
    * disable swap
    ```bash
    DRIVE='/dev/sda'
    PARTITION=3
    swapoff $DRIVE$PARTITION
    parted $DRIVE rm $PARTITION
    parted $DRIVE print
    ```

    * expand partition2
    ```bash
    DRIVE='/dev/sda'
    PARTITION=2
    ADD_ROOT_SIZE=100MB
    CURRENT_END=$(parted $DRIVE print --machine | grep "^${PARTITION}:" | cut -d ':' -f 3)
    NEW_END="$(( ${ADD_ROOT_SIZE/MB/} + ${CURRENT_END/MB/} ))MB"
    echo "Moving end of partition $DRIVE${PARTITION} from $CURRENT_END to $NEW_END"
    parted $DRIVE resizepart ${PARTITION} Yes $NEW_END
    resize2fs $DRIVE$PARTITION
    ```

    * re-create swap
    ```bash
    DRIVE='/dev/sda'
    PARTITION=3
    Start=$(parted $DRIVE print free --machine | tail -n 1 | grep ':free;' | cut -d ':' -f 2)
    parted --align optimal $DRIVE unit MB mkpart "swap" linux-swap $Start 100%
    mkswap --label "$(hostname)_swap" $DRIVE$PARTITION
    swapon $DRIVE$PARTITION
    ```
