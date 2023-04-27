MySQL Administration and Usage
=============================

Check out: [Percona Toolkit][pttools]

[pttools]: https://www.percona.com/doc/percona-toolkit/LATEST/index.html

Config
------

Static and dynamic options

* System variables are set up as persistent options in `/etc/mysql/my.cnf` respectively '/etc/my.cnf.d/some_setting.cnf`. Using them requires tor restart mysqld.
* [A lot of system variables](https://dev.mysql.com/doc/refman/8.0/en/dynamic-system-variables.html) can be set dynamically and are applied instantly without restarting mysqld.

    SET GLOBAL max_connections = 1000;


Retrieve config named option in shell

    mysql -Bse "SELECT @@<option>"

Retrieve all config variables

    mysql -Bse "SHOW VARIABLES"


Initialize DB
-------------

Stop and remove old DB

    MYSQL_DIR="$(mysql -Bse "SELECT @@datadir" 2>/dev/null )" \
        || MYSQL_DIR=/var/lib/mysql
    mysqladmin ping && mysqladmin shutdown
    [ -z "${MYSQL_DIR}" ] || rm -rvf "$MYSQL_DIR"

Populate mysql

    install -o mysql -g mysql -d "$MYSQL_DIR"/{,tmp,binlog} /var/{log,lib}/mysql
    mysql_install_db
    chown -R mysql:mysql "$MYSQL_DIR" /var/{log,lib}/mysql

Set root password, clear user and test DB - see below

Start MySQL service

    systemctl enable mariadb
    systemctl start mariadb



Data queries
---------------------


Select databases

    DBS=$(mysql -Bse "
        SELECT DISTINCT table_schema FROM information_schema.tables
        WHERE table_schema REGEXP 'flight|^hot|^my'
    ")

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


System
------

Check maximum number of open files allowed for mysql service user:

    su - mysql -s /bin/sh -c "ulimit -n"


Flushing, Locks
---------------

Put whole database to read only mode

    FLUSH TABLES WITH READ LOCK;
    SET GLOBAL read_only = 1;

Back to normal mode

    SET GLOBAL read_only = 0;
    UNLOCK TABLES;

  
Decrease InnoDB shutdown times - clear dirty pages

    SET GLOBAL innodb_max_dirty_pages_pct = 0   # default 75.000000
    mysqladmin ext -i10 | grep dirty


Users
-----

Create user with full access to db `seafile_db`

    CREATE USER  IF NOT EXISTS 'seafile'@'%' IDENTIFIED BY 'xxxxx';
    GRANT ALL PRIVILEGES ON seafile_db.* TO 'seafile'@'%';
    FLUSH PRIVILEGES;


Create root user with full access to all dbs 
    CREATE USER  IF NOT EXISTS 'root'@'%' IDENTIFIED BY 'xxxxx';
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%';
    FLUSH PRIVILEGES;


Update new root password when login is still possible

    PW=$(tr -dc '[:alnum:]' < /dev/urandom | tr -d "'\"" | fold -w 32 | head -n 1)
    mysql -e "
        UPDATE mysql.user SET password=PASSWORD('$PW') WHERE user='root';
        FLUSH PRIVILEGES;
    "
    echo -e "[client]\nuser=root\npassword=$PW" > /root/.my.cnf


Reset root password when login is not possible - db is beeing restarted in the process!

    PW=$(tr -dc '[:alnum:]' < /dev/urandom | tr -d "'\"" | fold -w 32 | head -n 1) 
    mysqladmin shutdown
    mysqld_safe --skip-grant-tables &
    while ! mysqladmin ping > /dev/null 2>&1 ; do sleep 1; done
    mysql -e "UPDATE mysql.user SET Password=PASSWORD('$PW') WHERE user='root';"
    echo -e "[client]\nuser=root\npassword=$PW" > /root/.my.cnf 
    chmod 0600 /root/.my.cnf
    mysqladmin shutdown
    systemctl start mariadb
    mysql -e "
        GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' IDENTIFIED BY '$PW' WITH GRANT OPTION;
        GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '$PW' WITH GRANT OPTION;
        GRANT ALL PRIVILEGES ON *.* TO 'root'@'::1'       IDENTIFIED BY '$PW' WITH GRANT OPTION;
        FLUSH PRIVILEGES;
    "


Drop single user without and with pattern match
    mysql -e "
        DROP USER IF EXISTS 'someuser'@'10.10.2.%';
        DELETE FROM mysql.user WHERE user LIKE 'replication%';
        FLUSH PRIVILEGES;
    "

Drop test db, all users without password or non-local root accounts

    mysql -e "
        DELETE FROM mysql.user WHERE user='root' AND host NOT IN ('localhost', '127.0.0.1', '::1');
        DELETE FROM mysql.user WHERE user='' OR password='';
        DROP DATABASE IF EXISTS test;
        DELETE FROM mysql.db WHERE db='test' OR db='test\\_%';
        FLUSH PRIVILEGES;
    "

Change user password

    mysql -e "
        UPDATE mysql.user SET Password=PASSWORD('xxxxx') 
        WHERE user='jira' AND host='%'
    "

Grep password from `my.cnf`

    PW=$(awk -F= '/^password/{print $2; exit}' ~/.my.cnf | tr -d ' ')


Create monitoring user, remove local accounts

    mysql -e "
        DELETE FROM mysql.user WHERE user = 'nagios' AND  host != '%';
        GRANT PROCESS,SHOW VIEW,REPLICATION CLIENT,SELECT,SHOW DATABASES ON *.* to nagios@'%' 
          IDENTIFIED BY PASSWORD '*599FA96B9EF18A97585DE37CE9AA8B7CA751EAC7';
        FLUSH PRIVILEGES;
    "


LDAP group mapping [ldap-mariadb][ldap]

[ldap]: http://www.geoffmontee.com/configuring-ldap-authentication-and-group-mapping-with-mariadb/


## Profiling, performance

Show running queries (you may want to fiddle around with state

    mysql -e "
        SELECT
            session.ipaddr,
            COUNT(1) AS session_count,
            FLOOR( AVG( session.time ) ) AS duration_avg_s,
            MAX( session.time ) AS duration_max_s,
            session.state
        FROM (
            SELECT
                pl.id,
                pl.user,
                pl.host,
                pl.db,
                pl.command,
                pl.time,
                pl.state,
                pl.info,
                LEFT( pl.host, ( LOCATE( ':', pl.host ) - 1 ) ) AS ipaddr
                FROM information_schema.processlist pl
        )
        AS session
        GROUP BY session.ipaddr
        ORDER BY session_count DESC
    "



MariaDB memory allocation: [Official documentation](https://mariadb.com/kb/en/mariadb-memory-allocation)

Queries and processes

    SHOW FULL PROCESSLIST

or

    mytop -dmysql


Validate memory overcommit - find out reserved memory, compare against
available mem

    top -n1 | awk '/mysqld/{print $5}'
    free -g


Check tables with no primary key: may slow down replication

    mysql -e "
    SELECT tables.table_schema, 
           tables.table_name, 
           tables.table_rows 
    FROM   information_schema.tables 
           LEFT JOIN (
                SELECT table_schema, table_name 
                FROM   information_schema.statistics 
                GROUP  BY table_schema, table_name, index_name 
                HAVING SUM(
                    CASE 
                    WHEN non_unique = 0 
                    AND nullable != 'YES' THEN 1 
                    ELSE 0 
                end) = Count(*)) puks 
           ON tables.table_schema = puks.table_schema 
           AND tables.table_name = puks.table_name 
    WHERE  puks.table_name IS NULL 
           AND tables.table_schema NOT IN ( 
                'mysql', 'information_schema', 'performance_schema' , 'sys' 
           ) 
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

## Database size 

Single database size in MB

    mysql -Bse "
        SELECT SUM(ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024))
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = "<DATABASE>"
    "

All databases sizes in MB 

    mysql -e "
        SELECT 
            table_schema AS 'Database', 
            SUM(ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024)) AS 'Size in MB'
        FROM INFORMATION_SCHEMA.TABLES
        GROUP BY table_schema
    "

Single table size in MB

    mysql -e "
        SELECT DISTINCT 
            table_schema AS 'Database', 
            table_name AS 'Table',
            round(((data_length + index_length) / 1024 )) AS 'Size in kB'
        FROM information_schema.tables
        WHERE table_schema NOT IN (
            'mysql', 'information_schema', 'performance_schema' , 'sys'
        ) 
    "

All databases size [MB] on disk (roughly equivalent to `DATA_LENGTH + INDEX_LENGTH` but faster)

    data_dir=$(mysql -Bse 'SELECT @@datadir') || datadir=/var/lib/mysql     
    find "$data_dir" -type f -printf "%s %p\n" \
    | awk '/ibd$|frm$|MYI$|MYD$|ibdata[0-9]/{s+=$1} END {print s/1024/1024}'


## Binlogs

Binlogs are used for recovering from server crash or for replication. Retention
period of 1 day is sufficient in most cases (covering short repairs).

Get binlog retention time [days]

    mysql -Bse "SELECT @@expire_logs_days"

Get binlog file size [MB]

    mysql -Bse "SELECT CEILING(@@max_binlog_size /1024 / 1024)"


Purge binlogs while under replication

* Slave: retrieve `Master_Log_File` binlog name

        mysql -e "SHOW SLAVE STATUS\G"  | grep -w Master_Log_File

* Master: purge binary logs prior to `Master_Log_File`
    
        mysql -e "PURGE BINARY LOGS TO 'mysql-bin.000063'"


## Transfer mysql data

In case zstd is not available, replace 

* `zstd -dcf` by `pigz -dc`
* `zstd -1` by `pigz -c --fast`

### Fast, lock free, binary   

Needs packages zstd (or pigz), netcat-openbsd, pv, xtrabackup (or MariaDB-backup) on both source and target

Prepare target - shut down, reset data

    NETCAT_PORT=3306
    MYSQL_DIR="$(mysql -Bse "SELECT @@datadir" 2>/dev/null )" || MYSQL_DIR=/var/lib/mysql
    IMPORT_DIR=${MYSQL_DIR%/}-import
    mysqladmin ping > /dev/null 2>&1 && mysqladmin shutdown
    which firewall-cmd 2> /dev/null && firewall-cmd --add-port=$NETCAT_PORT/tcp
    [ -z "${MYSQL_DIR}" ] || rm -rvf "$MYSQL_DIR"/*
    [ -z "${IMPORT_DIR}" ] || rm -rvf "$IMPORT_DIR"/*
    mkdir -pv "${MYSQL_DIR}" "${IMPORT_DIR}"

Run target listener
    netcat -l $NETCAT_PORT \
      | pv \
      | zstd -dcf \
      | xbstream --directory="$IMPORT_DIR" -x \
    && time xtrabackup --prepare --target-dir="$IMPORT_DIR" \
    && mv "$IMPORT_DIR/ib_data1" "$IMPORT_DIR/ibdata1" \
    && xtrabackup --move-back --target-dir="$IMPORT_DIR" \
    && mv "$IMPORT_DIR/xtrabackup_binlog_info" "$MYSQL_DIR" \
    && rm -rf "$IMPORT_DIR" \
    && install -o mysql -g mysql -d "$MYSQL_DIR"/{,tmp,binlog} /var/{log,lib}/mysql \
    && chown -R mysql:mysql "$MYSQL_DIR" /var/{log,lib}/mysql \
    && systemctl start mysql

Prepare source export

    TARGET=some.server.tld
    NETCAT_PORT=3306
    MYSQL_DIR=$(mysql -Bse 'SELECT @@datadir')
    DB_SIZE_MB=$(
        find "$MYSQL_DIR" -type f -printf "%s %p\n" \
        | awk '/ibd$|frm$|MYI$|MYD$|ibdata[0-9]/{s+=$1} END {print s / 1024 / 1024}'
    )

Run source export. `-parallel=$(nproc)` does not work out well on systems with
a lot of cpu cores - too many connections. Parameter -kill-long-queries-timeout
prevents long READ LOCK (RO-mode of whole databases) - prepare yourselfs

    mariabackup --backup --stream=xbstream --parallel=2 --kill-long-queries-timeout=5 2> mariabackup.log \
      | pv -s ${DB_SIZE_MB}m\
      | zstd -1 \
      | netcat -N $TARGET $NETCAT_PORT \
    && tail mariabackup.log


### Simple, fast, dirty

Rsync binary copy with short read lock on source db - no logical data copy but
fast. `mysql` database is not overriden here, so replicationuser setup may
still be intact.

Target: remove all data

    MYSQL_DIR=$(mysql -Bse 'SELECT @@datadir') || MYSQL_DIR= /var/lib/mysql
    mysqladmin ping > /dev/null 2>&1 && mysqladmin shutdown

Source: copy bulk of data to target, ignore errors

    TARGET=some_server.company.tld
    MYSQL_DIR=$(mysql -Bse 'SELECT @@datadir') || MYSQL_DIR= /var/lib/mysql
    rsync -a --sparse --progress --delete $MYSQL_DIR/ $TARGET:$MYSQL_DIR/ \
    --exclude=mastername* --exclude=master.info --exclude=relay-log.info --exclude=mysql

Source: lock server, read log positions, do final data sync, un-lock

    mysql -e "FLUSH TABLES WITH READ LOCK"
    mysql -e "show master status\G" | awk '/File:/{print "LOG_FILE="$2}' 
    mysql -e "show master status\G" | awk '/Position:/{print "LOG_POS="$2}'
    rsync -a --sparse --progress --delete $MYSQL_DIR/ $TARGET:$MYSQL_DIR/ \
    --exclude=mastername* --exclude=master.info --exclude=relay-log.info --exclude=mysql
    mysql -e "UNLOCK TABLES"


Target: start db with disabled slave operation, configure replication, restart with replication (without auth setup)

    mysqld_safe --skip-slave-start &
    MASTER_LOG_FILE=... 
    MASTER_LOG_POS=...
    mysql -e "
        CHANGE MASTER TO
            MASTER_LOG_FILE='$LOG_FILE',
            MASTER_LOG_POS=$LOG_POS;
        START SLAVE;
    "
    mysqladmin shutdown
    systemctl start mariadb


### Slow without lock - mysqldump

Takes ages due to slow mysqldump import process but is meant to work on 
all platforms. Clean, logical export (opposed to rsync method).

Source: 

    MYSQL_DIR=$(mysql -Bse 'SELECT @@datadir')
    TARGET=some_server.company.tld
    mysqldump --hex-blob --routines --triggers --master-data=1 \
    --add-drop-database --single-transaction --databases db1 db2 db5 \
    | gzip -3 > "$MYSQL_DIR/full_dump.sql.gz"

Source: scp `full_dump.sql.zstd` to target

Target: import database data

    mysql -e "STOP SLAVE"
    zcat full_backup.sql.gz | mysql

Target: retrieve master binlog file and position, optionally 

    zcat full_backup.sql.gz | head -n 30 | grep "^CHANGE MASTER TO" \
    | cut -d ' ' -f4- | tr ',' ';'


### Option: transfer nodata databases

Drop data in target databases, re-create structure for databases which are for example ignored in replication but should be there, somehow (as structure). Run on target (or source, if `NODATA_DBS` have not been transferred at all)


    # see "Select databases" for REGEXP usage
    NODATA_DBS="db1 db3 db7"
    mysqldump --add-drop-database --routines --triggers --no-data --databases $NODATA_DBS \
    | pigz -c > nodata.sql.gz

Import on target, overriding old db content:

    pigz -dc nodata.sql.gz | mysql



## Replication

Requirements for master-slave replication

1. master has binlogs enabled `log-bin = mysql-bin`, validate: `SHOW BINARY LOGS`
2. master has `server-id = 1`, validate: `SELECT @@server_id`
3. slave has minimum `server-id = 2`, validate: `SELECT @@server_id` 
5. schemas which need to be excluded from replication are configured like
   `replicate_ignore_db = temp_db`

### Operations

Stop and unconfigure replication info from slave

    mysql -e "
        STOP SLAVE;
        RESET SLAVE ALL;
    "


Skip one replication error - run on slave:

    mysql -e "
        STOP SLAVE;
        SET GLOBAL sql_slave_skip_counter = 1;
        START SLAVE;
    "


Check slave status continuously

     watch -n 10 "
         mysql -Bse 'SHOW SLAVE STATUS\G' | grep -E \
         'Slave_IO_Running:|Slave_SQL_Running:|Seconds_Behind_Master:|Last_SQL_Error'
     "

### Config

Master
    [mysqld]
    server_id = 1

Slave
    [mysqld]
    server_id = 2
    innodb_flush_log_at_trx_commit = 2
	slave_parallel_max_queue= 8MB
	slave_parallel_mode	aggressive
	slave_parallel_threads = $(nproc)
	slave_parallel_workers = $(nproc)
	gtid_pos_auto_engines = InnoDB,MyISAM
    #replicate_ignore_db = some_db

### Set up 

Re-initialize replication user and connection

Master: set up replication user

    REPL_USER=replication02 \
    && REPL_PASS="$(tr -dc '[:alnum:]' < /dev/urandom | head -c 32 && echo)" \
    && mysql -Bse "
      DELETE FROM mysql.user WHERE user='$REPL_USER';
      GRANT REPLICATION SLAVE ON *.* TO $REPL_USER@'%'
      IDENTIFIED BY '$REPL_PASS';
      FLUSH PRIVILEGES;
    " 
    echo -e "RUN ON SLAVE:\n"
    cat << SLAVE_END
    #LOG_FILE=?
    #LOG_POS=? 
    mysql -e "
        STOP SLAVE;
        CHANGE MASTER TO
            MASTER_HOST='$MASTER',
            MASTER_PORT=3306,
            MASTER_USER='$REPL_USER',
            MASTER_PASSWORD='$REPL_PASS',
            MASTER_LOG_FILE='\$LOG_FILE',
            MASTER_LOG_POS=\$LOG_POS;
        START SLAVE;
    "
    fi
    SLAVE_END

Paste RUN ON SLAVE: output above and check replication state:

    mysql -Bse "SHOW SLAVE STATUS\G"


Dump, backup
------------


Export dump - all databases. Prepare rebuilding replication from this dump

    mysqldump --add-drop-database --all-databases --events --hex-blob \
    --ignore-table=mysql.events --master-data=1 --master-data=1 \
    --routines --single-transaction --triggers | pigz -cR > all-databases.sql.gz


Import dump

    pigz -dc all-databases.sql.gz | mysql

    
Export dump like above but with progress meter - estimate max db size from db file
size, depending on db fragmentation the estimation may be too large

    MYSQL_DIR=$(mysql -Bse 'SELECT @@datadir') \ 
    && DB_SIZE_MB=$(
        find "$MYSQL_DIR" -type f -printf "%s %p\n" \
        | awk '/ibd$|frm$|MYI$|MYD$|ibdata[0-9]/{s+=$1} END {printf "%.0f", s/1024/1024}'
    ) \
    && mysqldump --add-drop-database --all-databases --events --hex-blob \
       --ignore-table=mysql.events --master-data=1 --master-data=1 \
       --routines --single-transaction --triggers \
    | pv -s "${DB_SIZE_MB}m" | pigz -cR > "$MYSQL_DIR/.all-databases.sql.gz"


Import dump like above but with progress meter

    pv all-databases.sql.gz | pigz -dc | mysql


Dump specific databases, only - filter by mysql filter expressions

    # EXCLUDE patterns override INCLUDE patterns
    INCLUDE='%'
    EXCLUDE='%xerces% %ota% mysql information_schema performance_schema'

    include_expr="table_schema LIKE \"${INCLUDE// /\" OR table_schema LIKE \"}\""
    exclude_expr="table_schema LIKE \"${EXCLUDE// /\" OR table_schema LIKE \"}\""
    DATABASES=$( mysql -Bse "
        SELECT DISTINCT table_schema AS db
        FROM information_schema.tables
        WHERE ($include_expr) AND NOT ($exclude_expr)
        GROUP BY table_schema
    ")

    mysqldump ... --databases $DATABASES ...


