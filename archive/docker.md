Docker handling
===============

* Consider [DRY](https://hackernoon.com/docker-cli-alternative-dry-5e0b0839b3b8) framework



Run containers
--------------

Stop and remove all containers

    docker rm $(docker ps -a -q)

Remove all images 

    docker rmi $(docker images -q)


Dockerfile
----------

    FROM debian:buster-slim

    RUN set -x \
     && savedAptMark="$(apt-mark showmanual)" \
     && apt-get update && apt-get install -y --no-install-recommends \
           iproute2 \
     && rm -rf /var/lib/apt/lists/*


    COPY docker-entrypoint.sh /
    ENTRYPOINT ["/docker-entrypoint.sh"]
    CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]



Entrypoint, CMD, run options
----------------------------

### Run container forever

Simple:

    docker run [-d] <image:tag> tail -f /dev/null

* Alternatively, put `CMD = ['tail', '-f', '/dev/null']` in `Dockerfile`
* Stop container like `docker stop ansible`

Better: use an entrypoint script which reacts on SIGTERM send to container:

    #!/bin/sh
    echo "Container is sleeping ..."
    # Spin until we receive a SIGTERM (e.g. from `docker stop`)
    trap 'exit 143' SIGTERM # exit = 128 + 15 (SIGTERM)
    tail -f /dev/null & wait ${!}

### Run as root

Dockerfile:

    ENTRYPOINT ["/docker-entrypoint.sh"]
    CMD ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]

Entrypoint script:

    #!/bin/sh
    set -eux

    # first arg is "-f" or "--some-option" - insert "haproxy" command
    if [ "${1#-}" != "$1" ]; then
        set -- haproxy "$@"
    fi

    # set necessary options for "haproxy" command
    if [ "$1" = 'haproxy' ]; then

        shift
        # ... put prep code here
        exec haproxy -W -db "$@"
        
    fi

    # start other command
    exec "$@"


### Run as user

Dockerfile:

    ENTRYPOINT ["docker-entrypoint.sh"]
    CMD ["postgres"]

Entrypoint script:

    #!/bin/sh
    # run as root to fix things, drop to user asap

    set -eux

    POSTGRES_USER=postgres

    if [ "$1" = 'postgres' ]; then

        chown -R $POSTGRES_USER "$PGDATA"
        if [ -z "$(ls -A "$PGDATA")" ]; then
             gosu $POSTGRES_USER initdb
        fi

        shift
        exec gosu $POSTGRES_USER postgres "$@"

    fi

    # start other command - as root
    exec "$@"

