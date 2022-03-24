Fortigate configuration
=======================

Session timeout for mysql connections in firewall = 8h

    config system session-ttl
        config port
            edit 3306
                set protocol 6
                set timeout 28800
                set start-port 3306
                set end-port 3306
            next
        end
    end

Force Failover master > slave

* login via ssh, reboot or
* switch to slave [per cli](https://community.fortinet.com/t5/FortiGate/Technical-Tip-How-to-force-HA-failover/ta-p/196696):

    * set failover state

        execute ha failover set 1
        execute ha failover status
        get system ha status

    * reset normal state

        execute ha failover unset 1
        execute ha failover status

## IPSec VPN

Reset tunnel

    get vpn ipsec tunnel name <phase1 name>
    diagnose vpn tunnel flush <phase1 name>
    diagnose vpn tunnel reset <phase1 name>  # re-negotiate

Diagnose, troubleshooting

* see [community blog][vpn_trouble]

[vpn_trouble]: https://community.fortinet.com/t5/FortiGate/Technical-Tip-Troubleshooting-IPsec-VPNs/ta-p/195955
