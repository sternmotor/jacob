Postgres
========


CLI 
---

Run command, strip output

    psql -U postgres -qAtXc 'SELECT 1'

Config
------

Get postgres config settings

    psql -U postgres -c "
        SELECT name,setting,unit FROM pg_settings
        WHERE name LIKE '%connection%'
    "


Set system config - check which context the settings is:

    psql -U postgres -c "SELECT name,context FROM pg_settings ORDER BY context,name"

According to context, do

* "postmaster": edit postgresql.conf, restart server

* "sighup", "backend", "superuser-backend": edit postgresql.conf, reload server by 
    * sending `SIGHUP` to postgres "postmaster" process
    * `pg_ctl reload` as user "postgres"
    * `psql -U postgres -c 'SELECT pg_reload_conf()'`

* "superuser", "user": system config in live instance:

    psql -U postgres -c "ALTER SYSTEM SET work_mem='50MB'"

Databases and user maintenance
---------------------------------

Initialise database

    postgresql-12-setup initdb

Login

    sudo psql -U postgres

List all databases except template databases

    psql -U postgres -Atc "SELECT datname FROM pg_database WHERE datistemplate = false"

Enable password less login for root (remotely)
* edit `~/.pgpass`

	#hostname:port:database:username:password
	<address>:*:*:<user>:<pass>

* user and host need to match when logging in

    psql -h <address> -U <user>

* retrieve data dir

    psql -U postgres -Atc 'SHOW data_directory'


Create database and user with full access to it

    DB_NAME='some_database' 
    DB_USER="$DB_NAME"
    DB_PASS="$(pwgen -sync 20 1)" 
    psql -U postgres -c "CREATE DATABASE $DB_NAME" 
    psql -U postgres -c "CREATE ROLE $DB_USER PASSWORD '$DB_PASS'" \
    && psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER" \
    && psql -U postgres -c "ALTER ROLE $DB_USER WITH LOGIN" \
    && psql -U postgres -c "ALTER DEFAULT PRIVILEGES FOR ROLE $DB_USER GRANT ALL ON TABLES TO $DB_USER" \
    && echo "PASSWORD: $DB_PASS"



Read-only user for all databases (including `template1`, thus new databases get the same permissions) - do  not forget to adjust `pg_hba.conf`

```
USER=remote_user
PASS='xxxxxx2Faiv)ai(Xeva'


psql -U postgres -tc "CREATE ROLE $USER LOGIN PASSWORD '$PASS' VALID UNTIL 'infinity'"
psql -U postgres -tc "ALTER ROLE $USER NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION"
psql -U postgres -tc "SELECT datname from pg_database where datname not in ('template0', 'postgres')" \
| while read db; do
    [[ -z "$db" ]] && continue
    echo -n "* $db ... " \
    && psql -U postgres -c "GRANT CONNECT ON DATABASE $db TO $USER" >/dev/null \
    && psql -U postgres -d "$db" -c "GRANT USAGE ON SCHEMA public TO $USER" >/dev/null \
    && psql -U postgres -d "$db" -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO $USER" >/dev/null  \
    && psql -U postgres -d "$db" -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $USER" >/dev/null \
    && psql -U postgres -d "$db" -c "ALTER DEFAULT PRIVILEGES  GRANT SELECT ON TABLES TO $USER" >/dev/null  \
    && echo "ok" || echo 'ERROR !!'
done
```

next, edit `pg_hba.conf` and reload like

    psql -U postgres -tc 'SELECT pg_reload_conf()'


Alternatively: create db via `postgres` user from shell

    su - postgres
    createuser -s repmgr
    createdb repmgr -O repmgr


Replication
-----------

Check [repmgr]https://severalnines.com/database-blog/integrating-tools-manage-postgresql-production() tool which dows all the heavy lifting (STONITH, replication setup)


Initiate replication: 

* master: 

        psql -U postgres -c "SELECT pg_drop_replication_slot('replicator')"
        REPLICATION_PASSWORD="$(
            tr -dc '[:alnum:]' < /dev/urandom | tr -d "'\"" | fold -w 32 | head -n 1
        )" \
        && psql -U postgres -c "
            DROP ROLE IF EXISTS replicator;
            CREATE ROLE replicator LOGIN REPLICATION ENCRYPTED PASSWORD '$REPLICATION_PASSWORD';
            SELECT pg_create_physical_replication_slot('replicator');
        " \
        && echo "REPLICATION_PASSWORD='$REPLICATION_PASSWORD'" || echo "ERROR!"

* slave: pull database - when asked, enter password from source server, here:

        SOURCE_HOST=db01.example.com
        DATA_DIR="$(psql -U postgres -Atc 'SHOW data_directory')" \
        || DATA_DIR=/var/lib/postgresql/data
        systemctl stop postgresql-12
        # [ -z "${DATA_DIR:-}" ] || rm -rf "$DATA_DIR"/*
        pg_basebackup -h $SOURCE_HOST -U replicator --slot replicator \
        --checkpoint=fast -D "$DATA_DIR" -Fp -Xs -P -R
        chown -R postgres:postgres "$DATA_DIR"
        chmod 0700 "$DATA_DIR"
        systemctl start postgresql-12


Get replication state

master overview:

    psql -U postgres -Axc "
        SELECT usename,application_name,client_addr,backend_start,state,sync_state,replay_lag 
        FROM pg_stat_replication
    " 

master: get wal files currently used by slave replication slots

    psql -U postgres -c "
        SELECT slot_name,
           lpad((pg_control_checkpoint()).timeline_id::text, 8, '0') ||
           lpad(split_part(restart_lsn::text, '/', 1), 8, '0') ||
           lpad(substr(split_part(restart_lsn::text, '/', 2), 1, 2), 8, '0')
           AS wal_file
        FROM pg_replication_slots;
    "

slave:

     psql -U postgres -Axc 'SELECT * FROM pg_stat_wal_receiver' \
    | column -ts '|'


slave: age of last synced data entry from master (not exactly lag) in seconds

    SELECT (EXTRACT(EPOCH FROM now()) - EXTRACT(EPOCH FROM pg_last_xact_replay_timestamp()))::int


slave: age of last synced data entry from master (not exactly lag) in HH:MM:SS

    SELECT now()::timestamp(0) - pg_last_xact_replay_timestamp()::timestamp(0)


Start/stop slave replication

    psql -U postgres -c 'SELECT pg_wal_replay_pause()'
    psql -U postgres -c 'SELECT pg_wal_replay_resume()'


Check replication health on slave, see [here][pg_repli_check]

1. General checks

```
psql -U postgres -Axc '
    SELECT pg_is_in_recovery(),pg_is_wal_replay_paused()
'
```

2. Determine lag in case wal locations are out of sync

```
psql -U postgres -Axc '
    SELECT CASE WHEN pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn()
    THEN 0
    ELSE EXTRACT (EPOCH FROM now() - pg_last_xact_replay_timestamp())
    END AS last_update_sec
'
```

3. Show how much data is missing on slave

```
psql -U postgres -Axc '
    SELECT round(
        pg_wal_lsn_diff(
            pg_last_wal_receive_lsn(),
            pg_last_wal_replay_lsn()
        )/1024/1024, 0
    )
    AS missing_lsn_mb
'
```

Turn slave to master - move replication file out of the way

    DATA_DIR="$(psql -U postgres -Atc 'SHOW data_directory')" 
    rm -f $DATA_DIR/{standby.signal,backup_label.*,recovery.conf}


[pg_repli_check]: https://severalnines.com/database-blog/what-look-if-your-postgresql-replication-lagging

DB transfer
-----------

Pull data from source to target and enable replication, check out: https://www.postgresql.org/docs/10/app-pgbasebackup.html

Source: install replication user on source server

    #ERROR:  replication slot "rep_slot" is active for PID 162564
    # select pg_terminate_backend(162564);

    psql -U postgres -c "SELECT pg_drop_replication_slot('replicator')"
    REPLICATION_PASSWORD="$(
        tr -dc '[:alnum:]' < /dev/urandom | tr -d "'\"" | fold -w 32 | head -n 1
    )" \
    && psql -U postgres -c "
        DROP ROLE IF EXISTS replicator;
        CREATE ROLE replicator LOGIN REPLICATION ENCRYPTED PASSWORD '$REPLICATION_PASSWORD';
        SELECT pg_create_physical_replication_slot('replicator');
    " \
    && echo "REPLICATION_PASSWORD='$REPLICATION_PASSWORD'" \
    || echo "ERROR!"


Source: enable `replication` user login to this server

* edit postgres `pg_hba.conf`

    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    ...
    host    replication     replicator      10.25.1.109/24          trust

* activate

    psql -U postgres -c "SELECT pg_reload_conf()"

Target: pull database - when asked, enter password from source server, here:

    SOURCE_HOST=db01.example.com
    DATA_DIR="$(psql -U postgres -Atc 'SHOW data_directory')" \
    || DATA_DIR=/var/lib/postgresql/data
    systemctl stop postgresl-12
    # [ -z "${DATA_DIR:-}" ] || rm -rf "$DATA_DIR"/*
    pg_basebackup -h $SOURCE_HOST -U replicator --slot replicator \
    --checkpoint=fast -D "$DATA_DIR" -Fp -Xs -P -R
    chown -R postgres:postgres "$DATA_DIR"
    chmod 0700 "$DATA_DIR"
    systemctl start postgresl-12



Target: Optionally stop and disable replication

* from postgres data dir, remove or clear `postgresql.auto.conf`
* restart postgres


Check slave status

     psql -U postgres -Axc 'SELECT * FROM pg_stat_wal_receiver' \
    | column -ts '|'


Estimate replication delay

    psql -U postgres -txc '
    SELECT
      pg_is_in_recovery() AS is_slave,
      pg_last_wal_receive_lsn() AS receive,
      pg_last_wal_replay_lsn() AS replay,
      pg_last_wal_receive_lsn() = pg_last_wal_replay_lsn() AS synced,
      (
       EXTRACT(EPOCH FROM now()) -
       EXTRACT(EPOCH FROM pg_last_xact_replay_timestamp())
      )::int AS lag;
    '

In case there is no output for "lag", the replication is not working. Check logs, then.

Check if replication ist running on system:

* master: display latest wal file (end of listing)

    DATA_DIR="$(psql -U postgres -Atc 'SHOW data_directory')"
    ls "$DATA_DIR/pg_wal" -ltr

* slave: validate there are  lines like 
  `startup   recovering 000000010000003D00000087` and 
  `walreceiver   streaming 3D/XXXXXXXX  ...` in process list:

      ps -aef | grep ^postgres



Plugins, Extensions, Modules
----------------------------

Update = drop recusively and reinstall extension - needs to be run for each
database, last line shows that extension is there

    DROP EXTENSION plv8 CASCADE;
    CREATE EXTENSION plv8;
    SELECT plv8_version();



Status, Performance
-------------------

Overview running queries

    SELECT
        usename,
        client_addr,
        backend_start,
        now() - pg_stat_activity.query_start AS duration,
        state
    FROM pg_stat_activity
    ORDER BY backend_start

Query what locks are granted and what processes are waiting for locks to be acquired


    SELECT relation::regclass, * FROM pg_locks WHERE NOT GRANTED;


Performance testing

* pgbench creates a test database using a scale-factor of 500

    pgbench -i -s 500

* Measure tps for select statements (`-S` parameter), excluding connections establishing

    pgbench -c 10 -S -T 600 -P 1 p gbench


Number of connections

    psql -U postgres -c "select count(*) from pg_stat_activity"

Show connections    

    psql -U postgres -c '
        SELECT
            usename,
            client_addr,
            backend_start,
            now() - pg_stat_activity.query_start AS duration,
            state
        FROM pg_stat_activity
        ORDER BY backend_start
    '

Check maximum number of open files allowed for postgresql service user:

    su - postgres -s /bin/sh -c "ulimit -n"

IOPs

io_concurrency
* number of concurrent disk I/O operations that PostgreSQL expects can be
  executed simultaneously. Raising this value will increase the number of I/O
  operations that any individual PostgreSQL session attempts to initiate in
  parallel. The allowed range is 1 to 1000
* SSD: 200
* SAS Raid: 50




Memory allocation
* set `shared_buffers` to around 25% of RAM
* actual memory usage is roughly `shared_buffers + max_connections * work_mem * N` 
* simple selects: `N=1`
* sorted subqueries and complex multi-table joins: `N=4-10`. 


See [Tuning tips](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)

Hugepages support (allow 1GB):

* [kernel parameters](https://www.percona.com/blog/2018/08/29/tune-linux-kernel-parameters-for-postgresql-optimization/)
* [hugepages benchmark](https://www.percona.com/blog/2018/12/20/benchmark-postgresql-with-linux-hugepages/ benchmark results)

Binlog/ write-aehead log
* [Checkpoint Tuning](https://www.2ndquadrant.com/en/blog/basics-of-tuning-checkpoints)


Vacuuming

"You should start by making sure autovacuum is working properly, that you are collecting enough statistics, and that you have correctly sized the memory parameters "

* [percona blog](https://www.percona.com/blog/2018/08/10/tuning-autovacuum-in-postgresql-and-autovacuum-internals)
* [postgres.org](https://www.postgresql.org/docs/11/routine-vacuuming.html)






