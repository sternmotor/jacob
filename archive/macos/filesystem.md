Create USB Stick from ISO

    diskutil list  # find usb by size
    diskutil unmountDisk /dev/disk2
    dd if=/Volumes/Daten/Users/Gunnar/Downloads/antix-17_x64-core.iso of=/dev/disk2 bs=10m
    # Ctrl-T to watch process
    diskutil eject /dev/disk2


Find  local timemachine snapshots

    tmutil listlocalsnapshots /


Clear harddrive space from unused local timemachine backups

    sudo tmutil thinLocalSnapshots / 10000000000 4



