# Create USB Stick from ISO

```
diskutil list  # find usb by size
diskutil unmountDisk /dev/disk2
dd if=/Volumes/Daten/Users/Gunnar/Downloads/antix-17_x64-core.iso of=/dev/disk2 bs=10m
# Ctrl-T to watch process

diskutil eject /dev/disk2
```