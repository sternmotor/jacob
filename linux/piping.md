Pipe
----

Specifying a bs= parameter that aligns with the disks buffer memory will get the most performance from the disk.

    dd status=progress 



Transfer a lvm volume over network, handles sparse volume sections more efficiently

    pv /dev/vg0/<device> | pigz --fast | ssh <remote_server> "pigz -dc > <device> "


