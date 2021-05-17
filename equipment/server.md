Server hardware
===============

Remote console (iDRAC, IPMI)
----------------------------

Linux desktop java console setup

* install

    sudo apt -y install firefox icedtea-netx icedtea-plugin default-jdk

* configure access to old console types (DELL R410), edit `/etc/java-11-openjdk/security/java.security`:

    jdk.tls.disabledAlgorithms=

* edit `~/.config/icedtea-web/deployment.properties`, (this file is getting overriden by icedtea config tool), should look like:

    deployment.console.startup.mode=SHOW
    deployment.log.headers=true
    deployment.log=true
    deployment.security.SSLv3=true
    deployment.security.expired.warning=false
    deployment.security.jsse.hostmismatch.warning=false
    deployment.security.level=ALLOW_UNSIGNED
    deployment.security.notinca.warning=false
    deployment.security.sandbox.awtwarningwindow=false

* check settings in IcedTea system control gui


DELL
----



