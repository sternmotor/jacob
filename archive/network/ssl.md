# SSL certificate handling


## Validation

Standard website on port 443 (interactive connection, exit via CTRL-C):

    openssl s_client -showcerts -connect some.domain.de:443


Imap Server (StartTLS)

    openssl s_client -showcerts -starttls imap -connect mail.domain.com:139
