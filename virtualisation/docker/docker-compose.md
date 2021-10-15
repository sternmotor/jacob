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

Other methods are docker-compose profiles and setting a services `command: /bin/true` (using dynmic environment variables)

