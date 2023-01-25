Docker and docker-compose operation
===================================

General settings: logging, buildkit, selinux - edit `/etc/docker/daemon.json`

    {
        "data-root": "/srv/docker",
        "ip": "0.0.0.0",
        "log-driver": "json-file",
        "log-level": "warn",
        "log-opts": {
            "max-file": "3",
            "max-size": "2M",
            "mode": "non-blocking"
        },
        "selinux-enabled": false,
        "features": { 
            "buildkit": true }
        }
    }


Execute commands in container
-----------------------------

NOT tested: e.g. if the container doesn't have ip commands in it

    nsenter -n -t $(docker inspect --format {{.State.Pid}} $dockername) ip route add something.


Reload container
----------------

Retrieve container name, send SIGHUP there

    #!/bin/bash
    set -euo pipefail
    LANG=C

    SERVICE='haproxy'   # docker-compose.yml service name
    SCRIPT_DIR="$(dirname "$0")"

    container=$(
        docker inspect -f '{{.Name}}' $(
            docker-compose --project-directory="$SCRIPT_DIR" ps -q $SERVICE
        ) | cut -c2-
    )

    docker exec $container haproxy -c -V -f /etc/haproxy/haproxy.cfg \
    && docker kill -s HUP $container


Ressources
----------

Check if and to which limit memory is restricted (within container, for example entrypoint script):

1. obtain amount of total memory on host (within container)

        host_mem_mb=$(free -m | awk 'NR==2{print$2}')

2. obtain total memory in container - huge number in case there is no cgroup limit

        container_mem_mb=$(awk '{printf "%d", $1/1024/1024 }' \
          < /sys/fs/cgroup/memory/memory.limit_in_bytes)

3. find out if limit is set

        if [ $container_mem_mb -lt $host_mem_mb  ] 
        then
            echo "limit is $container_mem_mb MB"
        else
            echo "there is no memory limit, host mem is $host_mem_mb MB"
        fi
    
Read [docker ressource constraints][contraints]

Increase shared memory (shm) in running container

    container_id=$(docker inspect --format='{{.Id}}' <CONTAINER_NAME>)
    mount -o remount,size=<NEW_SIZE_GB>g -t tmpfs /srv/docker/containers/$container_id/mounts/shm/
    # docker exec <CONTAINER_NAME> df -h /dev/shm


Get current RAM/CPU/IOPS/Network usage


    docker stats 

Container management
--------------------

Remove zombie containers

    docker rm $(docker ps --filter "status=exited" -q)


Monitoring
----------

Container ressource usage: `docker stats`

* `CPU %`: reports the host capacity CPU utilization.For example, if you have two containers, each allocated the same CPU shares by Docker, and each using max CPU, the docker stats command for each container would report 50% CPU utilization. Though from the container's perspective, their CPU resources would be fully utilized.
* `MEM USAGE / LIMIT MEM %`:  memory used by the container, along with the container memory limit, and the corresponding container utilization percentage. If there is no explicit memory limit set for the container, the memory usage limit will be the memory limit of the host machine. Note that like the CPU % column, these columns report on host utilization.
* `NET I/O`: total bytes received and transmitted 
* `BLOCK I/O`:  total bytes written and read to the container file systems
* `PIDS`: number of kernel process IDs running inside container


[scale_id]: https://tarunlalwani.com/post/docker-compose-scale-with-dynamic-configuration-part-1/
[constraints]: https://docs.docker.com/config/containers/resource_constraints/
