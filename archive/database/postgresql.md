PostgreSQL
==========


Create database and user with full access to it


    DB_NAME="some_database"
    DB_PASS="$(pwgen -sync 20 1)"

    echo "Setting password: $DB_PASS" \
    && psql -U postgres -c "CREATE DATABASE $DB_NAME" \
    && psql -U postgres -c "CREATE USER $DB_NAME PASSWORD '$DB_PASS'" \
    && psql -U postgres -c "GRANT ALL privileges on database $DB_NAME to $DB_NAME" \
    && echo 'ok' || echo 'ERROR !!'


Read-only user for all databases (including `template1`, thus new databases get the same permissions

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

    
Performance testing

* pgbench creates a test database using a scale-factor of 500

    pgbench -i -s 500

* Measure tps for select statements (`-S` parameter), excluding connections establishing

    pgbench -c 10 -S -T 600 -P 1 p gbench

