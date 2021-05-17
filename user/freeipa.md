FreeIPA
=======

Users
-----

Set user password to not-expire

    ipa user-mod rollout --setattr=krbPasswordExpiration=20440506103757Z


Hosts
-----

Create host and reverse dns

	kinit
	ipa dnsrecord-add app.infra.gs.xtrav.de otrs --a-rec 192.168.106.46
	ipa dnsrecord-add 106.168.192.in-addr.arpa 46 --ptr-rec otrs.app.infra.gs.xtrav.de.
	nslookup 192.168.106.46
