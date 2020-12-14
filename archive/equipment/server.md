Server hardware inspection
==========================



MegaCLI Raid
------------




rebuild progress

    watch -d -n 30 'megacli -FwTermLog -Dsply -aALL | tail -n 3'

get rebuild state

    megacli -PDList -aALL  | grep "Firmware state:"

raid volume state

    megacli -AdpAllInfo -aALL | grep -A 8 "Device Present"


battery charge state

    megacli -AdpBbuCmd  -a0 | egrep "Relative State of Charge|Charging Status"


log to console 

    MegaCli6m -FwTermLog -Dsply -aALL

event log to file

    megacli -AdpEventLog -GetLatest 100 -f events.log -aALL 

state of harddrives in raid

    megacli -PDList -a0

get controller writeback / cache policy

    megacli -LDInfo -Lall -Aall | grep "Cache Policy"

