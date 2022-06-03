# VPN 


## IPSec

Linux client for Fortigate IpSec (Strongswan)

* edit `/etc/ipsec.conf`

        # ipsec.conf - strongSwan IPsec configuration file
        config setup
            uniqueids = yes
            #charondebug="dmn 1, mgr 1, ike 1, chd 1, job 1, cfg 1, knl 1, net 1, enc1, lib 1"
            #charondebug="dmn 2, mgr 2, ike 2, chd 2, job 2, cfg 2, knl 2, net 2, enc2, lib 2"
            #charondebug="mgr 4,ike 4,chd 4,cfg 4,net 4,enc 4,imc 4,imv 4"
            charondebug="mgr 2,ike 2,chd 2,cfg 2,net 2,enc 2,imc 2,imv 2"

        # read: https://wiki.strongswan.org/projects/strongswan/wiki/connsection
        conn traso

        # local
            #left = 10.172.170.1
            left = 194.36.144.127
            leftsubnet = 10.172.170.1/32
            #leftsourceip = 10.172.170.1

        # remote site
            right = 212.99.201.222
            rightsubnet = 212.99.201.209/32

* edit  `/etc/ipsec.secrets`

        # This file holds shared secrets or RSA private keys for authentication.

        # RSA private key for this host, authenticating it to any other host
        # which knows the public part.

        # this file is managed with debconf and will contain the automatically created private key
        include /var/lib/strongswan/ipsec.secrets.inc
        212.99.201.222 10.172.170.1 194.36.144.127 : PSK "some-strong-pw"


