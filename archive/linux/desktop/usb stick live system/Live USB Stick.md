# USB Stick

# Hardware
USB Stick:

* langsam, durable: AData Elite S102 32GB (faster than 16GB)
* schnell, durable: Transcend Extreme-Speed JetFlash 780 32GB

* Partitions
* 12 GB NTFS Data transfer
* 8 GB System, Boot, Desktop
* 12 GB encrypted, persistent NTFS + Truecrypt container for Backup + Seafile data


# Create USB Stick from ISO

## macOS

```
diskutil list  # find usb by size
diskutil unmountDisk /dev/disk2
dd if=/Volumes/Daten/Users/Gunnar/Downloads/antix-17_x64-core.iso of=/dev/disk2 bs=10m
# Ctrl-T to watch process

diskutil eject /dev/disk2
```

OS: Alpine Linux mit Mate Desktop > Boot to RAM



https://rudd-o.com/linux-and-free-software/a-better-way-to-create-a-customized-ubuntu-live-usb-drive
