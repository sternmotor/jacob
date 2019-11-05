SSL certificate management
==========================

Check webseite certificate (do not rely on browser messages - caching!)


    curl -kv https://domain.tld

Show certificate's data

    openssl x509 -in domain.tld  -text -noout
