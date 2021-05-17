Postgres
========


CLI 
---

Run command, strip output

    psql -U postgres -qAtXc 'SELECT 1'



Databases and user maintenance
---------------------------------

Login

    sudo psql -U postgres

List all databases except template databases

    psql -U postgres -Atc "SELECT datname FROM pg_database WHERE datistemplate = false"

Enable password less login for root (remotely)
* edit `~/.pgpass`

	#hostname:port:database:username:password
	<address>:*:*:<user>:<pass>

* user and Host need to match when logging in

    psql -h <address> -U <user>




Create database and user with full access to it


    DB_NAME="some_database" 
    DB_PASS="$(pwgen -sync 20 1)"

    psql -U postgres -c "CREATE DATABASE $DB_NAME" \
    && psql -U postgres -c "CREATE USER $DB_NAME PASSWORD '$DB_PASS'" \
    && psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_NAME" 


Read-only user for all databases (including `template1`, thus new databases get the same permissions)

    USER='pgadmin'
    PASS='xxx'

    psql -U postgres -tc "CREATE ROLE $USER LOGIN PASSWORD '$PASS'"
    psql -U postgres -tc "SELECT datname from pg_database where datname not in ('template0', 'postgres')" \
    | while read db; do 
        [[ -z "$db" ]] && continue
        echo -n "* $db ... " \
        && psql -U postgres -d "$db" -c "GRANT USAGE ON SCHEMA public TO $USER" >/dev/null \
        && psql -U postgres -d "$db" -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO $USER" >/dev/null  \
        && psql -U postgres -d "$db" -c "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $USER" >/dev/null \
        && psql -U postgres -d "$db" -c "ALTER DEFAULT PRIVILEGES  GRANT SELECT ON TABLES TO $USER" >/dev/null  \
        && echo "ok" || echo 'ERROR !!'
    done

    


Config
------   

Show which config settings may be changed by reload and which need server restart

    SELECT name,context FROM pg_settings


Reload config settings

1. by sending `SIGHUP` to postgres "postmaster" process
2. `pg_ctl reload` as user "postgres"
2. `psql -U postgres -c 'SELECT pg_reload_conf()'`


Print postgres config settings

    SELECT name,context FROM pg_settings



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


Ressources, Tuning
------------------

IOPs

io_concurrency
* number of concurrent disk I/O operations that PostgreSQL expects can be
  executed simultaneously. Raising this value will increase the number of I/O
  operations that any individual PostgreSQL session attempts to initiate in
  parallel. The allowed range is 1 to 1000
* SSD: 100
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





