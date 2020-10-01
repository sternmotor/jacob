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


