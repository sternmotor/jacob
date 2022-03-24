# Linux user management


Generate secure password, 32 characters

    tr -dc '[:graph:]' < /dev/urandom | tr -d "\"'" | head -c 32 && echo
    pwgen -sync 32 1

Generate 5 readable passwords to select from

    tr -dc '[:alnum:]' < /dev/urandom | tr -d 'iIjJ' | fold -w 16 | head -n 5
    pwgen -nc 16 5
