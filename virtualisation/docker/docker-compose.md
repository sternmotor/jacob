Running docker-compose
======================

Versions
--------

Use version 2.4+ for pure docker-compose setups (allowing for clear ressource definition and service dependency on healthchecks) and version 3.6+ for Swarm.

Logging
-------

    logging:
      driver: json-file
      options:  
        max-size: '100m'
        max-file: '7'


Services management
-------------------


Anchors, example: "Exclude some services from running" below

* `&anchor-name` defines the anchor
* `*anchor-name` references the anchor
* `<<: *anchor-name` merges (`<<:`) the keys of `*anchor-name`


Exclude some services from running

    x-disabled-service: &disabled
      image: hello-world
      command: hello
      restart: no

    services:
      elasticsearch:
        <<: *disabled
        
      fluentdb:
        <<: *disabled

Other methods are docker-compose profiles and setting a services `command: /bin/true` (using dynamic environment variables)

Limit capabilities
------------------

See man 7 capabilities for a full list of capabilities or read [here][caps].
Use `cap_add`, `cap_drop` to remove caps for handling files and threads from
root or add caps to user

    services:
      nginx:
        cap_drop:
        - ALL
        cap_add:
        - CHOWN
        - NET_BIND_SERVICE
        - SETGID
        - SETUID

respectively

    sudo docker run --rm -it --cap-drop ALL --cap-add CHOWN alpine sh


[caps]: https://dockerlabs.collabnix.com/advanced/security/capabilities/


## Container control

Force clean shutdown with 1h timeout to allow containers to stop their jobs: edit `/etc/docker/daemon.json`

    "shutdown-timeout": 3600,

Allow restart of docker daemon without restarting containers: edit `/etc/docker/daemon.json`

    "live-restore": true,
    

