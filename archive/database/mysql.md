MySQL server operation
======================

Configuration
-------------

Calulations for automatic config generation

* MyISAM `key-buffer-size`: 500MB per 4GB

        awk '/MemTotal/{printf("%.0fM\n", $2 / 1024 / 8)}' /proc/meminfo

* `innodb-buffer-pool-size`: 80% of available RAM

        awk '/MemTotal/{printf("%.0fM\n", $2 / 1024 * 0.8)}' /proc/meminfo

* `innodb_buffer_pool_instances`: each buffer should have at least 1GB, max 64 buffers
 
        awk 'function min(a,b){ if(a<b) {return a} else {return b}}/MemTotal/{print min(64, int($2 / 1024 * 0.8 / (1024 + 1)))}' /proc/meminfo


Backup
------

Start dummy mysqld server for mysqldump after mariabackup - have `/srv/mariabackup` compressed btrfs

* create backup

        mariabackup --backup --target-dir=/srv/mariabackup
        mariabackup --prepare --target-dir=/srv/mariabackup

* start server in background

        mysqld \
            --datadir=/srv/mariabackup/ \
            --pid-file=/run/mariabackup.pid \
            --port=33306 \
            --socket=/run/mariabackup.sock \
            --user=root &

* pull backup - regular mysqldump

        mysqldump --socket=/var/run/mariabackup.sock --all-databases

* stop temporarily started server

        kill $(cat /var/run/mariabackup.pid)

