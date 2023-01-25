Bash command line interface scripting
=====================================

Help text: write as script header, grep out for help display

    #!/bin/sh -eu
    #: Usage: setup dev|test|prod
    #: (Re-)build / update images and initialize config for docker-compose project
    #:
    #: -d | --dev:  override with docker-compose.development.yml
    #: -t | --test: override with docker-compose.testing.yml
    #: -p | --prod : override with docker-compose.production.yml

    LAMG=C


    grep "^#:" "$0" | cut -d ' ' -f2- 1>&2

Wait for single key press

    read -p "Press any key to continue or CTRL-C to break ..." -n1 -s


Query password securely

    echo -n 'Enter user password: '
    prompt=''
    while IFS= read -p "$prompt" -r -s -n 1 char
    do
        # enter - accept password
        if [[ $char == $'\0' ]] ; then
            break
        fi
        # eackspace
        if [[ $char == $'\177' ]] ; then
            prompt=$'\b \b'
            password="${AdminPassword%?}"
        else
            prompt='*'
            password+="$char"
        fi
    done
    echo
