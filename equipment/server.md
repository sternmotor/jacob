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


## DELL

### StoreCLI/LSI management


* download https://docs.broadcom.com/docs/007.0709.0000.0000_Unified_StorCLI.zip
* install

    rpm -i storcli-007.0709.0000.0000-1.noarch.rpm
    ln -s /opt/MegaRAID/storcli/storcli64 /usr/local/bin/storcli

    storcli /c0 /eall /sall show
    storcli /c0 /vall show

    # show rebuild
    storcli /c0 /eall /sall show rebuild


### MegaRaid/LSI management

volume config overview (raid level)

	megacli -LDInfo -Lall -aALL

volume/disk state overview

	megacli -AdpAllInfo -aALL | grep -A 8 "Device Present"


locate bad hdds - overview:

	megacli -LDInfo -Lall -aALL | grep "^Name"
	megacli -PDList -aALL | grep "Enclosure Device" | sort | uniq
	megacli -PDList -aALL  | grep -E "Slot|Firmware state:|S.M.A.R.T"

locate bad hdds - details

	megacli -PDList -aAll| sed 's/^\(Enclosure Device ID.*\)/--- &1/' \
	| grep --color=no -E \
	"Enclo|Slot|Count:|Raw Size:|S.M.A.R.T|Firmware state|Spare|Inquiry Data|---"


locate bad hdds physically - blink:

	megacli -PdLocate -start -physdrv[252:2] -a0

observe rebuild

	watch -d -n 20 'megacli -FwTermLog -Dsply -aALL | tail -n 5'

retrieve controller log

    megacli -FwTermLog -Dsply -aALL

bbu charge state

    megacli -AdpBbuCmd  -a0 | egrep "Relative State of Charge|Charging Status"

get controller writeback / cache policy

    megacli -LDInfo -Lall -Aall | grep "Cache Policy"
