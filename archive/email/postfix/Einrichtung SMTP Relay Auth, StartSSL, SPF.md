# SMTP Mail relay (Ubuntu 16.04)

## Konfigurieren der Umgebung

* DNS Eintrag unter dc1systems.systems: _mailrelay.systems.fellowtech.com_
* [AutoDNS](https://login.autodns.com/#ZoneUpdate) Eintrag: `mailrelay.fellowtech.com` = `93.104.247.69`, SPF Eintrag: 
    * [AutoDNS](https://login.autodns.com/#ZoneUpdate) > Zusätzliche Nameserver-Einträge > "+" Name leer, RR-Type TXT, Wert:
        ```
        v=spf1 a mx ip4:93.104.247.69/32 -all
        ```

## Einrichtung Mailrelay Server
* run `sudo apt-get install postfix libsasl2-2 libsasl2-modules sasl2-bin -y`
    * Internet Site
    * mailrelay.fellowtech.com
* set sender name: echo  `mailrelay.fellowtech.com > /etc/mailname`    
  
* edit `/etc/postfix/main.cf`:
    ```
    # See /usr/share/postfix/main.cf.dist for a commented, more complete version

    # mail id and handling
    smtpd_banner = $myhostname ESMTP $mail_name (Ubuntu)
    myhostname = mailrelay.systems.fellowtech.com
    myorigin = /etc/mailname
    mydestination = $myhostname, localhost
    relayhost=
    append_dot_mydomain = no
    delay_warning_time = 4h
    readme_directory = no
    biff = no
    compatibility_level = 2


    # passwordless auth ip adresses
    mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128 172.31.252.12/32

    # password user auth, accounts and mailboxes
    smtpd_sasl_auth_enable = yes
    #smtpd_tls_auth_only = yes
    smtpd_sasl_security_options = noanonymous
    broken_sasl_auth_clients = yes
    alias_maps = hash:/etc/aliases
    alias_database = hash:/etc/aliases
    smtpd_delay_reject = yes
    recipient_delimiter = +
    smtpd_client_restrictions = permit_sasl_authenticated, reject


    # networking and tls
    inet_interfaces = all
    inet_protocols = all
    # allow encrypted sending only: encrypt, may
    smtp_tls_security_level = may
    smtpd_tls_cert_file=/etc/ssl/%.fellowtech.com/linux.pem
    smtpd_tls_key_file=/etc/ssl/%.fellowtech.com/linux.pem
    smtpd_use_tls=yes
    smtpd_tls_session_cache_database = btree:${data_directory}/smtpd_scache
    smtp_tls_session_cache_database = btree:${data_directory}/smtp_scache

    # mail queue
    maximal_queue_lifetime = 1h
    bounce_queue_lifetime = 1h
    maximal_backoff_time = 15m
    minimal_backoff_time = 5m
    queue_run_delay = 5m


    # sender address translation maps, enable like "postmap /etc/postfix/generic; service postfix reload"
    #sender_canonical_maps = hash:/etc/postfix/sender_canonical
    #smtp_generic_maps = hash:/etc/postfix/generic
    ```

* `/etc/postfix/%.fellowtech.com` Zertifikat vom reverseproxy kopiert nach  `/etc/ssl/%.fellowtech.com/`
    * dieses Zertifikat gilt nur für die im Internet verwendete Adresse _mailrelay.fellowtech.com_, nicht für die interne Adresse _mailrelay.systems.fellowtech.com_
* erlaube non-TLS smtp auf Port 25 (nur intern über mailrelay.systems.fellowtech.com):
    * check `master.cf`: `smtp      inet  n       -       y       -       -       smtpd`
    * Test: `echo "TestMail" | mailx -S smtp="mailrelay.systems.fellowtech.com:25"  -r "$(whoami)@$(hostname -f)" -s "Test: no-ssl" gunnar.mann@fellowtech.de`
* erlaube nur-TLS auf Port 587 (für externe Zugriffe über mailrelay.fellowtech.com)
    * edit `master.cf`: `submission inet n       -       y       -       -       smtpd -o smtpd_enforce_tls=yes`
    * Test: 
        ```
        echo "TestMail" | mailx -S smtp="mailrelay.fellowtech.com:25"  -r "$(whoami)@$(hostname -f)" -s "Test: no-startssl" gunnar.mann@fellowtech.de
        ```
        > smtp-server: 530 5.7.0 Must issue a STARTTLS command first
        
        ```
        echo "TestMail" | mailx -S smtp-use-starttls -S smtp="mailrelay.fellowtech.com:25"  -r "$(whoami)@$(hostname -f)" -s "Test: startssl" gunnar.mann@fellowtech.de
        ```
* Benutzer einrichten siehe [ft Zugangsdaten](https://wiki.fellowtech.de/Kunden/Zugangsdaten/ft)
    ```
    adduser jarvis
    passwd jarvis   # PW xxx  , full name J.A.R.V.I.S. 
    ```
* sasl auth installieren: siehe [Anleitung](https://www.df.eu/de/support/df-faq/cloudserver/anleitungen/smtp-authentifizierung-mit-postfix-debian). Vorsicht: postfix läuft in einem chroot, daher muss der sasl socket im Chroot `/var/spool/postfix` verfügbar sein

    ```
    apt-get install libsasl2-2 libsasl2-modules sasl2-bin
    gpasswd -a postfix sasl
    getent group sasl
    mkdir -p /var/spool/postfix/var/run/saslauthd
    sed -i 's|START=.*|START=yes|' /etc/default/saslauthd
    sed -i 's|MECHANISMS=.*|MECHANISMS="shadow"|' /etc/default/saslauthd
    sed -i 's|-m /var/run/saslauthd|-m /var/spool/postfix/var/run/saslauthd|' /etc/default/saslauthd
    
    cat << SASL_END > /etc/postfix/sasl/smtpd.conf
    pwcheck_method: saslauthd
    mech_list: PLAIN LOGIN
    SASL_END
    service saslauthd start
    ```
