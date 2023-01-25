Shell textfile handling
=======================


Filter single parameter from ini style file: filter `PARAM` line, remove
comments, remove surrounding  whitespaces and quotes:

    sed -e "/^\s*$PARAM\s*=/!d"                         \
        -e 's/#.*$//'                                     \
        -e 's/[^=]*=\s*\(.*\)\s*$/\1/' -e 's/\s*$//'    \
        -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//" \
        "$FILE"

Strip trailing newline from docekr secrets file etc.

    PW="$(printf '%s' $(cat $PASSWORD_FILE))"
