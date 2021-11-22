IPSec
=====



Linux client config 
-------------------

Example: Fortigate Server, Debian client ([strongswan](https://www.strongswan.org))

* `/etc/ipsec.conf`:

        # ipsec.conf - strongSwan IPsec configuration file
        config setup
            uniqueids = yes
            charondebug="mgr 2,ike 2,chd 2,cfg 2,net 2,enc 2,imc 2,imv 2"

        # read: https://wiki.strongswan.org/projects/strongswan/wiki/connsection
        conn example.com

        # local
            left = 194.xx.144.127
            leftsubnet = 10.172.170.1/32

        # remote site
            right = 212.99.201.222
            rightsubnet = 212.99.201.209/32

        # general connection settings   
            installpolicy = yes
            auto = route # "start" = connect immediately, "route" = on demand
            type = tunnel
            fragmentation = yes
            dpdaction = clear
            dpddelay = 10s
            dpdtimeout = 60s

        # authentification phase 1
            keyexchange = ikev2
            ikelifetime = 24h
            authby = psk
            reauth = yes
            # <hash algorithm>-<dh key group>
            ike = aes256-sha384-modp2048!

        # encrpytion phase 2
            rekey = yes
            rekeymargin = 3m
            lifetime = 1h
            keylife = 1h
            # IKEv2 Supports Mobility and Multi-homing Protocol (MOBIKE) making it more stable.
            mobike = no
            # force encapsulation: https://wiki.strongswan.org/projects/strongswan/wiki/Fortinet
            forceencaps = yes
            # <hash algorithm>-<psf key group>
            esp = aes256gcm16!

* edit `/etc/ipsec.secrets`

        <left> <right> : PSK "xxxxxxxxxxxxxxxxxxxxxxxx"
