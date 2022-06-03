KVM virtual machine mangement
=============================


VM status
---------

    virsh list --names
    virsh list --all
    virsh list --inactive
    virsh list --autostart
    virsh list --with-snapshot

Statistics

    virsh qemu-monitor-command <vm_name> --hmp "info block"


List all vms

    for vm in $(virsh list --name --all); do echo $vm; done

List all blockdevices of vm

    virsh domblklist $VM | awk '/\/dev\//{print $2}'

Set autostart for all vms

    for vm in $(virsh list --name --all); do virsh autostart $vm; done


CPU, Mem
--------

Offline resize

    virsh setvcpus <vm_name> <available_cpus> --config --maximum
    virsh setvcpus <vm_name> <active_cpus> --config
    virsh setmaxmem <vm_name> <available_mem KB> --config
    virsh setmem <vm_name> <active_mem kB> --config


Online resize is possible withing specified "maximum" boundaries (above)

    virsh setmem <vm_name> <active_mem kB> --current
    virsh setvcpus <vm_name> <active_cpus> --current



Block devices
-------------

Online resize - works with partitionless lvm volumes, only:

On vmhost:

    lvresize -L +10G /dev/vg0/<vm_name>_disk
    virsh blockresize <vm_name> /dev/vg0/<vm_name>_<disk> --size 32g

In guest, ext4, assuming there is no partition table on disk device:

    resize2fs /mountpoint 

In guest, adapt partition table (needs reboot before running `resize2fs /mountpoint`

    parted /dev/vde print free  # note partition number 
    umount /var/lib/mysql/
    parted /dev/vde resizepart 1 100%
    resize2fs /dev/vde1
    mount /var/lib/mysql
    systemctl restart mariadb

In guest, btrfs:

    btrfs filesystem resize max /srv
    btrfs filesystem resize +10g /mountpoint

In guest, xfs:

    xfs_growfs /srv

In guest, maximize last partition to use free space

    umount -l <mountpoint>
    parted /dev/vde print free  # note partitoin number
    parted -s /dev/vde "resizepart 2 -1" quit
    parted /dev/vde print free
    # grow filesystem ext4, xfs, btrfs like above

Limit IOPs and bandwith for operations on disks

    <disk type='block' device='disk'>
      <driver name='qemu' type='raw' cache='none' io='native'/>
      <source dev='/dev/vol1/dms.app.infra.gs.xtrav.de-opt'/>
      <target dev='vdf' bus='virtio'/>
      <iotune>
        <total_bytes_sec>52428800</total_bytes_sec>
        <total_iops_sec>1000</total_iops_sec>
      </iotune>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x0c' function='0x0'/>
    </disk>

Check disk throughput

    virsh qemu-monitor-command <GUEST> --hmp "info block"

Transfer KVM config to other host
---------------------------------

Transfer block devices

    VM=some-vm
    TARGET=remote-server
    virsh domblklist $VM | awk '/\/dev\//{print $2}' \
    | while read DEV; do
        echo "Transferring block device $DEV"	
        lv_name=$(LANG=C lvdisplay $DEV | awk '/LV Name/{print $3}')
        vg_name=$(LANG=C lvdisplay $DEV | awk '/VG Name/{print $3}')
        # create remote logical volume	
        size=$(LANG=C lvs --units k --noheadings --options lv_size $DEV)
        ssh -n $TARGET "lvcreate -Wn --size $size --name $lv_name $vg_name"		
        # transfer volume data
        pv $DEV | zstd -T0 --fast | ssh $TARGET "zstd -T0 -dcf > $DEV"
    done


Transfer vm config, start vm on target server

    TARGET=remote-server
    VM=some-vm
    virsh dumpxml $VM | pv | ssh $TARGET "cat - > /root/import-$VM.xml"
    ssh -n $TARGET "virsh define /root/import-$VM.xml"
    ssh -n $TARGET "virsh start $VM"


Remove machine on source server after checking that everything is fine

    VM=some-vm
    virsh destroy $VM
    lvremove -y $(virsh domblklist $VM | awk '/\/dev\//{print $2}')
    virsh undefine $VM



Disable kvm host swapping when vm mem is low
--------------------------------------------

in running vm

* vm.swappiness=0
* numad
* memory locking inder qemu.config

    <memoryBacking>
       <locked/>
    </memoryBacking>

* cpu placement auto

    <vcpu placement='auto'>1</vcpu>

* overcommit 2, overcommit_ratio 

KVM guest time sync
--------------------

Make sure `/sys/devices/system/clocksource/clocksource0/current_clocksource` is set to `kvm-clock` __and__ set up ntpd or chrony. See [Redhat recommendation][kvm_clock]:

> ... Interrupts cannot always be delivered simultaneously and instantaneously to all guest virtual machines. This is because interrupts in virtual machines are not true interrupts. Instead, they are injected into the guest virtual machine by the host machine.
...
To avoid the problems described above, the Network Time Protocol (NTP) should be configured on the host and the guest virtual machines ...

Security
-------

[BSI recommendations](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/Studien/Sicherheitsanalyse_KVM/Sicherheitsanalyse_KVM.pdf?__blob=publicationFile&v=3):

* activate selinux 
* deactivate KSM
* remove "default" nat-bridge
* run all bridges without host-ip
* deactivate ip_forward 
* enable reverse path filter




[kvm_clock]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_administration_guide/sect-virtualization-tips_and_tricks-libvirt_managed_timers]



