HaProxy Administration
======================



* MAINT: do not forward requests immediately, do not send health checks
* DRAIN: do not forward new requests, send health checks


Status
------

better than webgui (no page scrolll on update): start `hatop`, head over to "5-CLI"

    hatop -s /var/lib/haproxy/stats -i 1



API commands
------------

Socket API invocation - communicate via stats socket

* setup in /etc/haproxy/haproxy.cfg

        stats socket /var/run/haproxy.sock level admin


* examples - script

        echo "disable server yourbackendname/yourservername" | socat stdio /etc/haproxy/haproxysock
        echo "set server backend/serv state drain" | sudo socat stdio /run/haproxy/haproxysock

* example usage - interactive

        socat readline /var/run/haproxy.sock
        prompt
        set timeout cli 1d
        help

Alternative API: start `hatop`, head over to "5-CLI"

    hatop -s /var/lib/haproxy/stats -i 1



