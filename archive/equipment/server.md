Server hardware inspection
==========================



MegaCLI Raid
------------




rebuild progress

    watch -d -n 30 'megacli -FwTermLog -Dsply -aALL | tail -n 3'

get rebuild state

    megacli -PDList -aALL  | grep "Firmware state:"


battery charge state

    megacli -AdpBbuCmd  -a0 | egrep "Relative State of Charge|Charging Status"


log to console 

    MegaCli6m -FwTermLog -Dsply -aALL

event log to file

    megacli -AdpEventLog -GetLatest 100 -f events.log -aALL 

state of harddrive 0

    megacli -PDList -a0

get controller writeback / cache policy

    megacli -LDInfo -Lall -Aall | grep "Cache Policy"

