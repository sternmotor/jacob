Test mail sending
=================



Oneshot authorized StartTLS test

    echo "This is the message body and contains the message" | mailx -v \
    -r "test@example.com" \
    -s "This is the subject" \
    -S smtp="mail.example.com:587" \
    -S smtp-use-starttls \
    -S smtp-auth=login \
    -S smtp-auth-user="login@example.com" \
    -S smtp-auth-password="QwefwBVCK6LeAefwfweoiM" \
    -S ssl-verify=ignore \
    -S nss-config-dir=/etc/pki/nssdb/ \
    testuser@example.com

Configuring user mail (package: "hairloom-mailx")

edit `/root/.mailrc`:
```
account 1und1 {
  set smtp-use-starttls
  set smtp=smtp://smtp.1und1.de:25
  set smtp-auth=login
  set smtp-auth-user='mailrelay@company.com'
  set smtp-auth-password='xxx'
  set from="sender@example.net"
}
```
Test:
```
echo "Test Text" | mailx -A "1und1" -s "Test01" receiver@example.net
```
