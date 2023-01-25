FreeIPA
=======

Users
-----

Set user password to not-expire

    ipa user-mod f.lastname --setattr=krbPasswordExpiration=20440506103757Z
    ipa user-mod f.lastname --password-expiration='2099-12-31 23:59:59Z'

Show user details 

    ipa user-show f.lastname --all


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
