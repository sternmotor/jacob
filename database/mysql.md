MySQL Administration and Usage
=============================

Config
------

Static and dynamic options

* System variables are set up as persistent options in `/etc/mysql/my.cnf` respectively '/etc/my.cnf.d/some_setting.cnf`. Using them requires tor restart mysqld.
* [A lot of system variables](https://dev.mysql.com/doc/refman/8.0/en/dynamic-system-variables.html) can be set dynamically and are applied instantly without restarting mysqld.

    SET GLOBAL max_connections = 1000;


Retrieve config options in shell

    mysqld --verbose --help --log-bin-index="$(mktemp -u)" 2>/dev/null \
    | awk '/^datadir/{print $2}'



Users
-----

Reset root password

    systemctl stop mariadb
    mysqld_safe --skip-grant-tables &
    mysql -e "UPDATE mysql.user SET Password=PASSWORD('new-password') WHERE User='root'"
    mysql -e "FLUSH PRIVILEGES"
    mysqladmin shutdown
    systemctl start mariadb

Drop all users with bad host specification

    mysql -Bse "select user,host from mysql.user WHERE user = 'nagios' AND  host != '%'" \
    | while read u h; do 
        echo "removing ${u}@$h"
        mysql -e "DROP USER '${u}'@'$h'"
    done
    mysql -e "FLUSH PRIVILEGES"

Create monitoring user

    mysql -e "
    GRANT PROCESS,SHOW VIEW,REPLICATION CLIENT,SELECT,SHOW DATABASES ON *.* to nagios@'%' IDENTIFIED BY PASSWORD '*599FA96B9EF18A97585DE37CE9AA8B7CA751EAC7';
    FLUSH PRIVILEGES;
    "

Profiling, performance
----------------------

Queries and processes

    SHOW FULL PROCESSLIST

Single database size

    SELECT SUM(ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024))
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = "<DATABASE>"


Authentification
----------------

Group mapping ldap-mariadb: [here][ldap]

Replication
-----------

### General

Switch slave to master - adapt `/etc/my.cnf` (server_id, binlogs)  and restart
mysql/mariadb after these steps:

    STOP SLAVE;
    RESET SLAVE ALL;

Skip one replication error - run on slave:

    STOP SLAVE;
    SET GLOBAL sql_slave_skip_counter = 1;
    START SLAVE;


Show mysql slave status

    mysql -Bse 'SHOW SLAVE STATUS\G' \
    | grep -wE '(Last_SQL_Error|Seconds_Behind_Master|Slave_IO_Running|Slave_SQL_Running)'


### Re-initialise replication


Preparation

INCLUDE_DBs=
NO_DATA_DBs=
EXCLUDE_DBs=


Master: set up replication user

Master: dump no-data databases

Master: dump data with binlog position 

    mysqldump \
    --add-drop-database \
    --hex-blob \
    --routines \
    --single-transaction \
    --triggers \
    --databases 








Requirements for master-slave replication

1. master has binlogs enabled `log-bin = mysql-bin`, validate: `SHOW BINARY LOGS`
2. master has `server-id = 1`, validate: `SELECT @@server_id`
3. slave has minimum `server-id = 2`, validate: `SELECT @@server_id` 
5. schemas which need to be excluded from replication are configured like
   `replicate_ignore_db = temp_db`

(Re-) initiate master-slave replication

1. slave: `STOP SLAVE`
2. master: `FLUSH HOSTS`    (reset dns resolve)
3. master: set up replication user `repli_user` with password `repli_pass`

        CREATE USER IF NOT EXISTS repli_user;
        ALTER USER repli_user IDENTIFIED BY 'repli_pass';
        REVOKE ALL PRIVILEGES, GRANT OPTION FROM repli_user;
        GRANT REPLICATION SLAVE ON *.* TO repli_user;
        FLUSH PRIVILEGES;

4. master: check if there is more than 1 replication user entry 

        SELECT COUNT(*) from mysql.user where User = repli_user;

5. slave: define replication 

        RESET SLAVE;
        CHANGE MASTER TO
            MASTER_HOST="sqlmaster.example.com",
            MASTER_USER="repli_user",
            MASTER_PASSWORD="repli_pass",
            MASTER_PORT=3306,
            MASTER_CONNECT_RETRY=3;

6. optional: dump and transfer database table structure for schemas where no data shall
   be excluded (e.g. corresponding to `replicate_ignore_db` entries)

        mysql-dump --no-data --databases temp_db \
        --add-drop-database \
        --single-transaction \  
        | zstd -T0 \
        | ssh sqlslave.example.com "zstd -T0 -dcf | mysql"

7. optional: filter databases to be transferred fully from `SHOW DATABASES`,
   skipping non-mysql directories and system databases

        mysql -Bse "SELECT DISTINCT table_schema FROM information_schema.tables" \
        | grep -vwE "(information_schema|mysql|performance_schema)"

8. dump and transfer databases via ssh pipe, here: all databases
        
        #mysql-dump --databases db1 db2 \
        mysql-dump --all-databases \
        --add-drop-database \
        --hex-blob \
        --master-data=1 \
        --routines \
        --single-transaction \  
        --triggers \
        | zstd -T0 \
        | ssh sqlslave.example.com "zstd -T0 -dcf | mysql"

9. slave: start replication

        START SLAVE;

10. check slave status after some seconds

        watch "mysql -Bse 'SHOW SLAVE STATUS\G' \
        | grep -wE '(Last_SQL_Error|Seconds_Behind_Master|Slave_IO_Running|Slave_SQL_Running)'"


Backup
------

Create local copy of mysql data dir (consistently, without locking running database) - requires [percona xtrabackup](https://www.percona.com/doc/percona-xtrabackup/2.3/backup_scenarios/full_backup.html#preparing-a-backup) package to  be installed.


Short version:

    DUMPDIR='/srv/backup-dumps/percona'
    innobackupex --defaults-extra-file=/etc/mysql/debian.cnf --parallel=4 "$DUMPDIR"
    innobackupex --apply-log --parallel=4 --use-memory=1G "$DUMPDIR"


Robust version:

    DUMPDIR='/srv/backup-dumps/percona'
    OPTIONS='--defaults-extra-file=/etc/mysql/debian.cnf --parallel=4 --use-memory=1G'
    innobackupex $OPTIONS --no-timestamp "$DUMPDIR" | tee "$DUMPDIR/xtrabackup_export.log" \
    && grep -q "completed OK!" "$DUMPDIR/xtrabackup_export.log" \
    && innobackupex $OPTIONS --apply-log "$DUMPDIR" | tee "$DUMPDIR/xtrabackup_prepare.log" \
    && grep -q "completed OK" "$DUMPDIR/xtrabackup_prepare.log"




SQL queries
-----------

Histogram: count occurence of discrete values in a column (`history`) of table `items`:

    select count(*), history from items group by history;

Output:

    +----------+---------+
    | count(*) | history |
    +----------+---------+
    |       41 |       0 |
    |      992 |       1 |
    |        3 |       2 |
    |     3706 |       3 |
    |      622 |       5 |
    |    43861 |       7 |
    |     1059 |      10 |
    |      212 |      14 |
    |       30 |      30 |
    |      109 |      31 |
    |    11184 |      90 |
    |      265 |     365 |
    |       83 |    1095 |
    |       24 |    3650 |
    +----------+---------+
    14 rows in set (0.04 sec)

[ldap]: http://www.geoffmontee.com/configuring-ldap-authentication-and-group-mapping-with-mariadb/
