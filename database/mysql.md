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

Create user with full access to db

    CREATE USER 'seafile'@'%' IDENTIFIED BY 'xxxxx';
    GRANT ALL PRIVILEGES ON mysql_seafile.* TO 'seafile'@'%';
    FLUSH PRIVILEGES;

    CREATE USER 'root'@'%' IDENTIFIED BY 'xxxxx';
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';
    FLUSH PRIVILEGES;

Reset root password

    systemctl stop mariadb
    mysqld_safe --skip-grant-tables &
    mysql -e "UPDATE mysql.user SET Password=PASSWORD('new-password') WHERE User='root'"
    mysql -e "FLUSH PRIVILEGES"
    mysqladmin shutdown
    systemctl start mariadb

Drop all users without password or non-local root accounts

        mysql -e "
            DELETE FROM mysql.user 
                WHERE user='root' 
                AND host NOT IN ('localhost', '127.0.0.1', '::1');
            DELETE FROM mysql.user WHERE user='';
            DELETE FROM mysql.user WHERE password='';
            DROP DATABASE test;
            FLUSH PRIVILEGES;
        "

Change user password

    mysql -e "
        UPDATE mysql.user SET Password=PASSWORD('xxxxx') 
        WHERE user='jira' AND host='%'
    "

Create monitoring user, remove local accounts

    mysql -e "
    DELETE FROM mysql.user WHERE user = 'nagios' AND  host != '%';
    GRANT PROCESS,SHOW VIEW,REPLICATION CLIENT,SELECT,SHOW DATABASES ON *.* to nagios@'%' IDENTIFIED BY PASSWORD '*599FA96B9EF18A97585DE37CE9AA8B7CA751EAC7';
    FLUSH PRIVILEGES;
    "




Profiling, performance
----------------------


mytop -dmysql

* replication slave: 
    * "Waiting for work from SQL thread", "Not enough room": check `slave_parallel_max_queued`
    * row based binlog writing at master helps




Target: make all indexes fit into memory

innodb-buffer-pool-size = 0.8 * (All RAM - 2GB System - 20MB * max_connections)


Queries and processes

    > SHOW FULL PROCESSLIST

or

    mytop -dmysql


Validate memory overcommit - find out reserved memory, compare against
available mem

    top -n1 | awk '/mysqld/{print $5}'
    free -g


Single database size in MB
    mysql -Bse "
    SELECT SUM(ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024))
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = "<DATABASE>"
    "

All databases sizes in MB 

    mysql -e '
    SELECT table_schema AS "Database", 
    SUM(ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024)) 
    AS "Size [MB]"
    FROM INFORMATION_SCHEMA.TABLES
    GROUP BY table_schema
    '

Single table size in MB
    db=
    tb=
    mysql -Bse "
    SELECT table_name AS 'Table',
    round(((data_length + index_length) / 1024 / 1024)) 'Size in MB'
    FROM information_schema.TABLES
    WHERE table_schema = '$db'
    AND table_name = '$tb'
    "






Check tables with no primary key: may slow down replication

    mysql -e "
    SELECT tables.table_schema, 
           tables.table_name, 
           tables.table_rows 
    FROM   information_schema.tables 
           LEFT JOIN (SELECT table_schema, 
                             table_name 
                      FROM   information_schema.statistics 
                      GROUP  BY table_schema, 
                                table_name, 
                                index_name 
                      HAVING Sum(CASE 
                                   WHEN non_unique = 0 
                                        AND nullable != 'YES' THEN 1 
                                   ELSE 0 
                                 end) = Count(*)) puks 
                  ON tables.table_schema = puks.table_schema 
                     AND tables.table_name = puks.table_name 
    WHERE  puks.table_name IS NULL 
           AND tables.table_schema NOT IN ( 'mysql', 'information_schema', 
                                            'performance_schema' 
                                            , 'sys' ) 
           AND tables.table_type = 'BASE TABLE' 
           AND engine = 'InnoDB';
    "


Memory per connection - multiply by `max_connections`, most important
is `tmp_table_size=16MB`

    mysql -e "
    SELECT (
          @@read_buffer_size
        + @@read_rnd_buffer_size
        + @@sort_buffer_size
        + @@join_buffer_size
        + @@binlog_cache_size
        + @@thread_stack
        + @@tmp_table_size
        + 2*@@net_buffer_length
    ) / (1024 * 1024) AS MEMORY_PER_CON_MB
    "

System
------
Check maximum number of open files allowed for mysql service user:

    su - mysql -s /bin/sh -c "ulimit -n"

Authentification
----------------

Group mapping ldap-mariadb: [here][ldap]

Replication
-----------


Purge binlogs while under replication

* Slave: retrieve `Master_Log_File` binlog name

        mysql -e "SHOW SLAVE STATUS\G"

* Master: purge binary logs prior to `Master_Log_File`
    
        mysql -e "PURGE BINARY LOGS TO 'mysql-bin.000063'"


### Parameters

Master
    [mysqld]
    server_id = 1
    binlog-commit-wait-count=10

Slave
    [mysqld]
    server_id = 2
    innodb_flush_log_at_trx_commit = 2
	slave_parallel_max_queue= 8MB
	slave_parallel_mode	aggressive
	slave_parallel_threads = $(nproc)
	slave_parallel_workers = $(nproc)
	gtid_pos_auto_engines = InnoDB,MyISAM
    #slave-skip-errors=1062
    #replicate_ignore_db = some_dumb_db


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
        | zstd -1 \
        | ssh sqlslave.example.com "zstd -df | mysql"

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


Read Lock
---------

Put whole database to read only mode

    FLUSH TABLES WITH READ LOCK;
    SET GLOBAL read_only = 1;

Back to normal mode

    SET GLOBAL read_only = 0;
    UNLOCK TABLES;

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
