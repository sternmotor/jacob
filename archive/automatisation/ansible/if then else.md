Ansible conditional structures
==============================


when
----

AND

    when:
    - item.fstype != 'swap'
    - item.fstype != 'btrfs'
    - item.device.startswith('/dev/')

OR

    when: >
      item.fstype != 'swap' or
      item.fstype != 'btrfs' or
      item.device.startswith('/dev/') 
