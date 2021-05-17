Linux network
=============


Sockets, ports, connections
--------------------------

Find process listening on tcp ipv4 port 80

    ss -4 -tlnp | grep -w :80
    ps -fp <PID>


Piping
------

Pipe-transfer of disks is handled under [filesystem](filesystem.md)


Transfer an file as-is (no compression)

    time ssh <source_host> "cat /srv/dump.pgsql.gz" | pv | ssh target "cat - > /mnt/dump.pgsql.gz"


