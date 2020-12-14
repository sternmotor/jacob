Building docker images with alpine
==================================
Entrypoint script
-----------------

check out envsubst

Dockerfile
----------

Split package installation and application config into several `RUN` sections,
allowing for faster image rebiuld in case for example only some config `COPY`
has changed. Each RUN command creates a new layer, do not exxagerate this.


Temporary compiler toolchain  

* install: 

        RUN set -ex \
         && echo "**** install build packages ****" > /dev/null \
         && apk add --update --no-cache --virtual=.build-deps \
            build-base \
            libffi-dev \
            openssl-dev \
            python3-dev 

* clear:

        RUN set -ex \
         && echo "**** removing build packages ****" > /dev/null \
         && apk del --purge .build-deps 

Apk repositories

    ARG ALPINE_VERSION=3.5

    RUN \
     && echo "**** install  build packages ****" >/dev/null \
     && cat << APK_REPO > /etc/apk/repositories
    http://nl.alpinelinux.org/alpine/v${ALPINE_VERSION}/main
    http://nl.alpinelinux.org/alpine/v${ALPINE_VERSION}/community
    APK_REPO 

