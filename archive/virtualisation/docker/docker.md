# Docker virtualization

Debugging, profiling
--------------------

Your friend:

    docker stats


## Dockerfile

```

```





### SystemD init script for docker images
```bash
[Unit]
Description=My Advanced Service
After=docker.service

[Service]
TimeoutStartSec=0
ExecStartPre=-/usr/bin/docker kill apache1
ExecStartPre=-/usr/bin/docker rm apache1
ExecStartPre=/usr/bin/docker pull coreos/apache
ExecStart=/usr/bin/docker run --name apache1 -p 8081:80 coreos/apache /usr/sbin/apache2ctl -D FOREGROUND
ExecStop=/usr/bin/docker stop apache1
ExecReload=/usr/bin/docker exec -t TEMPLATE /usr/sbin/httpd $OPTIONS -k graceful

[Install]
WantedBy=multi-user.target
```

Docker compose
---------------

template


`docker-compose.yml` example for building an image with tags applied:

    # docker-compose file for jira application
    ---

    version: '3'

    services:
      jira:
        container_name: jira
        hostname: jira01
        image: jira_keystorefix:7.3
        build: ./build/jira_keystorefix
        depends_on:
          - postgres
        ports:
          - '80:8080'
        volumes:
          - jiradata:/var/atlassian/jira:rw
        environment:
          JIRA_DATABASE_URL: 'postgresql://jira@postgres/jira'
          JIRA_DB_PASSWORD: '2WI(ZZwefewsnln.^G\@c'
          SETENV_JVM_MINIMUM_MEMORY: 2000m
          SETENV_JVM_MAXIMUM_MEMORY: 12000m
          # enable osgi plugin purge on startup and restarts
          JIRA_PURGE_PLUGINS_ONSTART: 'false'
          JVM_XX_OPTS: >
            -XX:+UnlockExperimentalVMOptions
            -XX:+UseG1GC
            -XX:G1NewSizePercent=20
            -XX:MaxGCPauseMillis=50
            -XX:G1HeapRegionSize=32M
          TZ: 'Europe/Berlin'
        logging:
          driver: json-file
          options:  # max 128MB
            max-size: '16m'
            max-file: '8'
        deploy:
          resources:
            limits:
              cpus: '3.0'
              memory: '6G'
        restart: unless-stopped

    volumes:
      jiradata:
      postgres:
        driver: lvmxfs
        driver_opts:
            size: "300G"

    # vim:ts=2:sw=2:et



ENV file tempate

# user-specific setup for docker-compose, copy to ".env" and edit

    # this directories are mounted ro into container as in home directory
    INVENTORY_DIR=./inventory
    PNAM=${USER}

    # vim:ft=dosini

entrypoint script


'ls' is not a Traefik command: assuming shell execution.
