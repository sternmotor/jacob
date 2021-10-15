Server hardware
===============

Remote console (iDRAC, IPMI)
----------------------------

Linux desktop java console setup

* install

        sudo apt -y install firefox icedtea-netx icedtea-plugin openjdk-8-jdk

* activate java 8

        sudo update-alternatives --config java

* configure access to old console types (DELL R410), edit `/etc/java-8-openjdk/security/java.security`:

        jdk.tls.disabledAlgorithms= # remove everything

* edit `~/.config/icedtea-web/deployment.properties`, (this file is getting overriden by icedtea config tool), should look like:

        deployment.jre.dir=/usr
        deployment.log.headers=true
        deployment.log=true
        deployment.security.SSLv3=true
        deployment.security.expired.warning=false
        deployment.security.jsse.hostmismatch.warning=false
        deployment.security.level=ALLOW_UNSIGNED
        deployment.security.notinca.warning=false
        deployment.security.sandbox.awtwarningwindow=false

* check settings in IcedTea system control GUI, run firefox to start the whole thing


DELL
----



