Test mail sending
=================



Authorized StartTLS test

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





