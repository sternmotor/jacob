FTP 
====


Download from FTPs site (without SSL verification) to local /tmp dir

```
lftp <<LFTP_END
set ftps:initial-prot ""
set ftp:ssl-force true
set ftp:ssl-protect-data true
set ssl:verify-certificate no
open ftps://example-server.example.com
user <USERNAME> <PASSWORD>
lcd /tmp
cd <REMOTE SUBDIR>
get <FILE>
exit
LFTP_END
```

