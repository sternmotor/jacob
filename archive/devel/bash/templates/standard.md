
# Standard bash script template

```bash
#!/bin/bash
# USAGE
#   backup-zabbix [--help] [--started] [--problem] [--success] [TARGET]
#
# DESCRIPTION
#     Send backup state messages to zabbix server
#
# ARGUMENTS
#      
#     TARGET
#         local or remote server where backup is running and
#         properly configured zabbix agent ist running
#         [[user@]host[:port] (remote) or nothing (local)
#         
# OPTIONS
#
#     --help|-h
#         print this help
#
#     --problem|-p
#       send information about backup error to zabbix trapper
#
#     --started|-s
#       send information about backup start to zabbix trapper
#
#     --success|-u
#       send information about successful backup run to zabbix trapper
#
#  
# EXAMPLE
#     backup-zabbix --running

set -euo pipefail


# MAIN FUNCTIONS =============================================================

SSH_SESSION_DIR=~/.ssh/sessions # directory for persistent ssh connections
SSH_OPTIONS='-T -o StrictHostKeyChecking=No -o ConnectTimeout=3'
SSH_OPTIONS="$SSH_OPTIONS -o ControlMaster=auto -o ControlPersist=10m"
SSH_OPTIONS_DST="$SSH_OPTIONS -o ControlPath=$SSH_SESSION_DIR/%r@%h:%p.dst"

# zabbix backup notifier
ZABBIX_KEY="backupstate"
ZABBIX_SUCCESS=0
ZABBIX_STARTED=1
ZABBIX_PROBLEM=2
ZABBIX_AGENT_CONFIG='/etc/zabbix/zabbix_agentd.conf'


# handle command line options and defaults, start action on TARGET
main() {

    # collect commandline options
    while [ $# -gt 0 ]; do
        case "${1:-}" in
            --started|-s)
                if [ -z "${ZabbixKey:-}" ]
                then
                    local ZabbixValue=$ZABBIX_STARTED
                    local StateDescription='Started'
                    shift
                else
                    echo "Specify only one of --started, --problem or --success!" 1>&2
                    exit 1
                fi
            ;;
            --problem|-p)
                if [ -z "${ZabbixValue:-}" ]
                then
                    local ZabbixValue=$ZABBIX_PROBLEM
                    local StateDescription='ERROR'
                    shift
                else
                    echo "Specify only one of --started, --problem or --success!" 1>&2
                    exit 1
                fi
            ;;
            --success|-u)
                if [ -z "${ZabbixValue:-}" ]
                then
                    local ZabbixValue=$ZABBIX_SUCCESS
                    local StateDescription='Success'
                    shift
                else
                    echo "Specify only one of --started, --problem or --success!" 1>&2
                    exit 1
                fi
            ;;
            --help|-h)
                sed -e 1d -e '/^$/,$d' -e 's|^# ||' -e 's|^#$||' $0
                exit 0
            ;;
            -*)
                echo "Unkown option \"$1\", try $(basename $0) --help"
                exit 1
            ;;
            *)
                if [ -z "${Target:-}" ]
                then
                    local Target="$1"
                    shift 1
                else
                    echo "TARGET defined as \"$Target\", already - got \"$1\""
                    exit 1
                fi
            ;;
        esac
    done

    # validate input logic
    if [ -z "${ZabbixValue:-}" ]; then
        echo "Specify one of --started, --problem or --success!" 1>&2
        exit 1
    fi


    # generate run_src from SOURCE and run_dst() and $DstDir from TARGET
    set_run_dst "${Target:-}"

    echo "* Notifying zabbix: backup \"$StateDescription\""

    run_dst "
        zabbix_sender --config '$ZABBIX_AGENT_CONFIG' \
            --key $ZABBIX_KEY \
            --value $ZabbixValue \
            > /dev/null 2>&1
    "
}
# ...

main "$@"
```
