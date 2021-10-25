Network troubleshooting
=======================



ARP cache
---------

Show table - look out for `(incomplete)` entries

    arp -n


Reset complete table to get rid of  `(incomplete)` entries

    ip -s -s neigh flush all


