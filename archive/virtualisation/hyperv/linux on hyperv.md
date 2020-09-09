# Linux on HyperV

* Kommentare überprüfen, doku warum nicht debian (ergibt sicjh im Vergleich der unterstützten Funktionen): https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/supported-ubuntu-virtual-machines-on-hyper-v
* KVP Daemon integrieren: http://wiki.lenux.org/debian-jessie-hyper-v/, wichtig: Fcopy für setup-script
* Static IP Injection
* Grub Timeout: https://docs.microsoft.com/en-us/windows-server/virtualization/hyper-v/best-practices-for-running-linux-on-hyper-v

## Convert Generation2 VM to Generation1 VM

Backport a VM  from HyperV 2016 to HyperV 2008R2. The point is to remove the EFI boot installion (disabling secure boot) so the Generation1 boot loader can load this VM.

1. Export VM on HyperV 2016
2. Copy VHDx files from exported VM, convert to VHD file
```Powershell
Convert-VHD xxx.vhdx xxx.vhd
Remove-Item xxx.vhdx
```
3. Create new virtual VM
    * Type Generation 1
    * Start Medium: some rescue CD (Debian-based - e.g. [GRML](https://grml.org))
4. Edit VM:
    * add `root.vhd` and `data.vhd`
    * adjust VLAN, virtual processors, integration services, start and stop action
5. Boot rescue CD
6. Enable networking
7. Mount root drive to `/mnt`, enable networking (and ssh into rescue system)
```bash
fdisk -l # find root drive
mount /dev/sda2 /mnt
cp /mnt/etc/network/interfaces /etc/networking
/etc/init.d/networking restart
```
8. Prepare chroot system for adapting grub
```bash
mount -o rbind /dev  /mnt/dev
mount -t sysfs /sys  /mnt/sys
mount -t proc  /proc /mnt/proc
mount -o bind  /run  /mnt/run
cp /proc/mounts      /mnt/etc/mtab
```
9. Replace EFI grub by standard grub
```bash
chroot /mnt
apt-get remove grub-efi-amd64
apt-get install grub2  # ignore error when installing boot loader
grub-install /dev/sda --force
exit
systemctl poweroff
```
10. Configure VM: remove virtual CD, adjust bios
11. Export VM
