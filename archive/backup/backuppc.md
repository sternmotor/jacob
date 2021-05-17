BackupPC Usage


remove last backup run

* deaktivate backup session

        cd /var/lib/BackupPC/pc/<client>/
        mv <backup_number> delme

* edit `backups`, remove line with `<backup_number>`
* remove backup files (lengthy operation)

        rm -rf <backup_number>
