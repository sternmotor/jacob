Building docker images
======================

Rules
-----

* unless building multistage images, remove tmp files, caches etc in the same line you created these to trim down layer size
* put things that may change more often during development as close to the dockerfile end as possible to make most out of docker build cache
* run all container main processes with UID/GID=1000 


Entrypoint
----------

Adapt main process user's UID and GID

    PUID="${PUID:-1000}"
    PGID="${PGID:-1000}"
    groupmod --gid $PGID www-data
    usermod  --uid $PUID --gid $PGID www-data
    install -o $PUID -g $PGID -m 0750 --directory "$(echo ~www-data)"


Run ssh client in container, use ssh persistence and forward key agent in
container - no need to copy ssh stuff into image

    docker run --rm \
        --volume $SSH_AUTH_SOCK:/ssh-agent \
        --env SSH_AUTH_SOCK=/ssh-agent \
        debian:slim ssh-add -l



Run main process with dropped privileges, pass all env variables

    exec sudo -Eu www-data php /var/www/myapp.php "$@"



In case container is executed with non-executable string as first parameter
(`CMD=`, `--command=`), pass command line options to main process. Otherwise
run `CMD=` or `--command=` directly


    #!/bin/sh -eu
    LANG=C
    TZ=${TZ:-Europe/Berlin}
    PUID="${PUID:-1000}"
    PGID="${PGID:-1000}"
    PUSER="haproxy"


    echo "* $0: setting up user \"$PUSER\" ($PUID:$PGID)"
        groupmod --gid $PGID $PUSER
        usermod  --uid $PUID --gid $PGID $PUSER
        install -o $PUID -g $PGID -m 0750 -d \
            "$(echo ~$PUSER)" \
            /var/run/haproxy


    echo "* $0: setting up timezone \"$TZ\""
        ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
        echo $TZ > /etc/timezone


    # $1 is executable, run it
    if which "${1:-}" >/dev/null 2>&1
    then

        # if the user wants "haproxy", let's add a couple useful flags
        #   -W  -- "master-worker mode" (similar to the old
        #          "haproxy-systemd-wrapper"; allows for reload via "SIGUSR2")
        #   -db -- disables background mode
        if [ "$1" = 'haproxy' ]
        then
            shift
            set -- haproxy -W -db "$@"

        # else some other command - just leave $@ as ist is
        fi

    # $1 is not executable, append as arguments to main process
    else
        set -- haproxy "$@"

    fi

    echo "* $0: Launching \"$@\""
    #exec sudo -Eu $PUSER "$@"
    exec "$@"


Other approach: specify `ENTRYPOINT` *and* default `CMD` in Dockerfile, have entrypoint follow this logic (example: sshd service is running `borg serve` on SSH client connect):


* Dockerfile:  `CMD = "sshd -e -D"`
* entrypoint script: `$@` cannot be empty since CMD is specified

        if $1 = "sshd":
            prepare-user-accounts
            exec $@

        elif $1 <> "sshd" but executable (e.g. `bash` or `sh` or `borg`)
            exec $@

        elif $1 not executable
            run borg with command/option $@ for adminsitration

        else ($1="", triggered by `--command=''`
            display borg version



Dockerfile snippets
-------------------

Retrieve version numbers of installed PHP

    php_version="$(php -r 'echo(PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION);')"

Install gosu

    ARG GOSU_VERSION=1.10
    RUN dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
     && curl -sSL "https://github.com/tianon/gosu/releases/download/${GOSU_VERSION}/gosu-${dpkgArch}" >/usr/bin/gosu \
     && chmod 755 /usr/bin/gosu \
     && gosu nobody true



Dockerignore
------------
See [Tutorial](https://codefresh.io/docker-tutorial/not-ignore-dockerignore-2)

### docker-compose usage pattern


Docker ignore pattern for including docker build stuff in code git repository -
having app and environment combined in single development strain

Example code repository directory structure:

    .dockerignore
    .env
    bin                 << php application stuff
    docker-compose.yml
    docker/README       << description of how this docker stack is build
    docker/env.example
    docker/php-cli
    docker/php-cli/Dockerfile
    docker/php-cli/bin
    docker/php-cli/conf
    docker/volumes
    vendor              << php application stuff

Configure `.dockerignore`:

    # exclude git/dev info and docker files from image
    .env*
    .git*
    docker*

    # re-include some dirs in docker build sub-directories
    !docker/php-cli/bin/*
    !docker/php-cli/conf/*


Configure `docker/php-cli/Dockerfile`, place all code stuff into `/app` in container

    ...
    COPY . /app  
    COPY --chown=www-data:www-data docker/php-cli/bin/* /usr/local/bin/
    ...

In `docker-compose.yml`, specify build like

    build:
      context: .
      dockerfile: docker/php-cli/Dockerfile
      args:
        ...


### Details

Patterns for `.dockerignore`

    { term }
    term:
    '*' matches any sequence of non-Separator characters
    '?' matches any single non-Separator character
    '[' [ '^' ] { character-range } ']'
    character class (must be non-empty)
    c matches character c (c != '*', '?', '\\', '[')
    '\\' c matches character c

    character-range:
    c matches character c (c != '\\', '-', ']')
    '\\' c matches character c
    lo '-' hi matches character c for lo &lt;= c &lt;= hi

    additions:
    '**' matches any number of directories (including zero)
    '!' lines starting with ! (exclamation mark) can be used to make exceptions to exclusions
    '#' lines starting with this character are ignored: use it for comments


Ignore, exclude in `.dockerignore` - docker uses the last rule that matches as
the "final" rule

    # Ignore everything
    *

    # Allow files and directories
    !/file.txt
    !/src/**

    # Ignore unnecessary files inside allowed directories
    # This should go after the allowed directories
    **/*~
    **/*.log
    **/.DS_Store
    **/Thumbs.db

