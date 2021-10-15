Mail Queue
==========

See all mails queued

    mailq

Get mail by id

	postcat -q 623301E0


Try resending all mails in queue

    postqueue -f # the same as
    sendmail -q -v # more portable , untestet

Clear mailq - remove all mails

	postsuper -d ALL

