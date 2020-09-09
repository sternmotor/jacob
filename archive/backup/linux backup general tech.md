# Tech Sammlung

Ausnahmen
- /dev/**
**/lost+found/**
- /media/**
- /mnt/**
- /proc/**
- /run/**
- /sys/**
- /tmp/**
- /var/lib/php5/sessions/**
+ *

*tildea

/home/*/.thumbnails
/home/*/.cache
/home/*/.mozilla/firefox/*.default/Cache
/home/*/.mozilla/firefox/*.default/OfflineCache
/home/*/.local/share/Trash
/home/*/.gvfs/

/var/tmp
/var/backup
/var/cache/man
/var/cache/apt/archives
/var/cache/davfs2
/var/cache/apt/archives
/var/lock/*


sync
flush tables
    * nur xtrabackup dump, prepared

backup-system
backup-databases
    * dump single db's, NOT tables
    * myisam --opt  --flush-privileges ("mysql db"
    * inndob --opt --skip-lock-tables --single-transaction 
backup-full
    * sync
    * flush tables
    * exclude  /srv/backup  (system and database dump dir)
    * ich würde in /proc/mounts nach sehen wo festplatten /dev/sd* /dev/hd* eingebunden sind und die einzeln archivieren (ausser swap), alle anderen mounts mit 
     --one-file-system
           stay in local file system when creating archive
        einpacken (name des mountpoints im ArchivNamen)

----

tar - gzip options
	tar --gzip --sparse --preserve-permissions --acls --xattrs --directory '/' --wildcards --exclude="/etc/ssl" --exclude="/etc/alternatives" --create --file test.gz --  /usr/local/sbin /usr/local/bin /etc
 
 
	--to-stdout
 
local operation: verify
	
mysqldump gzip options
    -6
	--rsyncable
	--to-stdout
	--recursive  

Mysql: flush tables via SIGHUP signal to MySQL server
