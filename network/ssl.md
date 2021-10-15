SSL certificate management
==========================

Check webseite certificate (do not rely on browser messages - caching!)


    curl -kv https://domain.tld

Show certificate's data

    openssl x509 -in domain.tld  -text -noout

Create certificate signing request (CSR) `<domain>.csr`

    KEY_SIZE=2048                # key size for private key 
    DOMAIN="sternmotor.net"      # *.domain.tld oder domain.tld (CN)
    STAAT="DE"                   # DE
    LAND="Saxonia"               # Bavaria oder Preussen
    STADT="Leipzig"              # Stadt / Ort
    FIRMA="Sternmotor"           # Unternehmen, Organisation (O)
    ABTEILUNG="Web Services"     # Abteilung (OU)
    EMAIL="admin@sternmotor.net" # Support eMail Adresse
    openssl genrsa -out $DOMAIN.key $KEY_SIZE
    openssl req -new \
        -key $DOMAIN.key \
        -out $DOMAIN.csr \
        -subj "/C=$STAAT/ST=$LAND/L=$STADT/O=$FIRMA/OU=$ABTEILUNG/CN=$DOMAIN/emailAddress=$EMAIL"

