FreeIPA
=======

Users
-----

Set user password to not-expire

    ipa user-mod rollout --setattr=krbPasswordExpiration=20440506103757Z


Hosts
-----


Create dns zone and reverse zone
    kinit
    ipa dnszone-add zone.example.net --allow-sync-ptr=TRUE
    ipa dnszone-add 19.21.10.in-addr.arpa.

Create host and reverse dns

	kinit
    ipa dnsrecord-add zone.example.net hostname --a-rec 10.21.19.10
    ipa dnsrecord-add 10.19.21.10.in-addr.arpa 46 --ptr-rec host.zone.example.net.
	nslookup 10.21.19.10
