# Timemachine backup


Timemachine backup to samba share
Needs samba 4.8, see [Samba Filesharing](../filesharing/samba.md)


Docker config  for timemachine server:

    version: '3'
    services:
      app:
        image: willtho/samba-timemachine:latest
        build: docker-samba-timemachine
        container_name: timemachine
    #    hostname: timemachine
    #    domainname: sternmotor.net
    #    dns_search: sternmotor.net
        network_mode: host
        environment:
          TM_USER: timemachine
          TM_PW: timemachine
    # size: 512000 = 512 GB
          TM_SIZE: 512000
        volumes:
          - '/media/data/backup/timemachine/:/timemachine'
          - '/etc/localtime:/etc/localtime:ro'
        restart: unless-stopped


    https://github.com/willtho89/docker-samba-timemachine.git

