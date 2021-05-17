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


