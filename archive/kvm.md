KVM virtual machine mangement
=============================


List all vms

    virsh list
    virsh list --all
    virsh list --inactive
    virsh list --autostart
    virsh list --with-snapshot


Block devices
-------------

Online resize - works with partitionless lvm volumes, only:

On vmhost:

    lvresize -L +10G /dev/vg0/server_disk
    virsh blockresize server /dev/vg0/server_disk --size 32g

In guest, ext4, assuming there is no partition table on disk device:

    resize2fs /mountpoint 

In guest, btrfs:

    btrfs filesystem resize max /srv
    btrfs filesystem resize +10g /mountpoint

In guest, xfs:

    xfs_growfs /srv


Limit IOPS and Bbandwith for operations on disks

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

Security
-------

[BSI recommendations](https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Publikationen/Studien/Sicherheitsanalyse_KVM/Sicherheitsanalyse_KVM.pdf?__blob=publicationFile&v=3):

* Selinux an
* Deaktivierung KSM
* Entfernung "default" nat-bridge
* Alle Bridges ohne host-ip
* ip_forward aus
* reverse path filter an


Disable kvm host swappnig when vm mem is low
--------------------------------------------

In der vm
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


[kvm_clock]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_administration_guide/sect-virtualization-tips_and_tricks-libvirt_managed_timers]



