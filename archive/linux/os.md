Linux OS topics
===============


system performance, bottlenecks
-------------------------------


iotop

    iotop -Po

Kernel messages (with proper timestamp)

    dmesg -T




process performance, load
-------------------------


Check if command is running, alread

    if pidof -x rclone >/dev/null; then
        echo "Process already running"
        exit
    fi


process logs
------------

    journalctl -fu mariadb

