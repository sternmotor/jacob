MySQL Administration and Usage
=============================

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


System variables
----------------

System variables are set up as persistent options in ''/etc/mysql/my.cnf'' respectively '/etc/my.cnf.d/some_setting.cnf''. Using them requires tor restart mysqld.

[A lot of system variables](https://dev.mysql.com/doc/refman/8.0/en/dynamic-system-variables.html) can be set dynamically and are applied instantly without restarting mysqld.

    SET GLOBAL max_connections = 1000;




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


Powershell
----------

Access mysql database via powershell: see  [CodePlex Article](http://mysqlpslib.codeplex.com/)
