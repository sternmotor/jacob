# Docker virtualization


## main route

kubernate < docker containers < atomic (centos)

## Atomic cluster

### Installation

```bash
wget http://cloud.centos.org/centos/7/atomic/images/CentOS-Atomic-Host-7-Installer.iso
```

## Dockerfile


```bash
FROM		fedora
MAINTAINER	Dan Walsh
ENV container docker
RUN yum -y update; yum -y install httpd; yum clean all

LABEL Vendor="Red Hat" License=GPLv2
LABEL Version=1.0
LABEL INSTALL="docker run --rm --privileged -v /:/host -e HOST=/host -e LOGDIR=/var/log/\${NAME} -e CONFDIR=/etc/\${NAME} -e DATADIR=/var/lib/\${NAME} -e IMAGE=\${IMAGE} -e NAME=\${NAME} \${IMAGE} /bin/install.sh"
LABEL UNINSTALL="docker run --rm --privileged -v /:/host -e HOST=/host -e IMAGE=${IMAGE} -e NAME=${NAME} ${IMAGE} /bin/uninstall.sh"
ADD root /
```

### SystemD init script for docker images
```bash
[Unit]
Description=The Apache HTTP Server for TEMPLATE
After=docker.service
BindTo=docker.service

[Service]
ExecStart=/usr/bin/docker start TEMPLATE
ExecStop=/usr/bin/docker stop TEMPLATE
ExecReload=/usr/bin/docker exec -t TEMPLATE /usr/sbin/httpd $OPTIONS -k graceful

[Install]
WantedBy=multi-user.target
```

