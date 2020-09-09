# Bash script error handling


Command line option check
```bash
# load defaults for optional parameters
local Schedule=$DEFAULT_SCHEDULE
local Print='no'
local Generate='no'

# collect commandline options
while [ $# -gt 0 ]; do
    case "${1:-}" in
        --schedule|-s)
            local Schedule="${2:-}"
            shift 2
        ;;
        --dry*|-d)
            local Print='yes'
            shift 1
        ;;
        --gen*|-g)
            local Generate='yes'
            shift 1
        ;;
        # print help (commented text at top of script file) and exit
        --help|-h)
            sed -e 1d -e '/^$/,$d' -e 's|^\#\ ||' $0
            exit 0
        ;;
        -*)
            echo "Unkown option \"$1\", try $(basename $0) --help"
            exit 1
        ;;
        # handle single argument
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
```

Script Lock using directories (atomic operation)

```bash
main() { : }

# locking setup
create_lock() {
    # check if lock newer than uptime exists, stop script then with error

    if [ -d "$LOCK" ]
    then
        # check if lock dir is newer than reboot
        local BootTimeSeconds=$( cat /proc/uptime  | cut -d '.' -f1 )
        local BootEpochSeconds=$(( $(date +%s) - $BootTimeSeconds ))
        local FileModEpochSeconds=$(stat -c %Y "$LOCK")
        if [ $FileModEpochSeconds -lt $BootEpochSeconds ]
        then
                echo "Removing outdated lock \"$LOCK\"" 1>&2
                rmdir "$LOCK" && mkdir --parents -- "$LOCK"
        else
                echo "Script is locked, try  'rmdir \"$LOCK\"' if wrong"
                return 12
        fi
    else
        mkdir --parents -- "$LOCK"
    fi
}

cleanup() {
    rm -rf "$LOCK"
}


# check lock, start script
# create ascii string suitable for lock file naming from $0
LOCK_ID=$( echo "$0 ${@:-}" | base64 --wrap 0 --ignore-garbage - | tr -d '=')
LOCK="/var/lock/$(basename $0)/$LOCK_ID" # warlock hihi

if create_lock; then
    trap cleanup EXIT HUP INT KILL TERM STOP
    main "$@"
fi
```


## Status Codes
idea:
```bash
case "$Message" in
    bla) return 2;;
esac

STATUS_CODES="
  0 Backup finished successfully) return                      
  5 Backup error, check eventlog) return
  8 Backup cancelled) return
  9 Backup Volume Shadow copy operation failed) return
 14 Backup finished with or without errors) return) return
 17 Backup engine could not be contacted) return
 18 Backup schedule settings not found) return
 19 Backup start error, check eventlog) return
 20 Another backup or recovery is in progress) return
 21 backup conflict with group policy settings) return
 22 backup recovery planning occupied by other client.) return
 49 No backup target could be found) return
 50 No space available on backup target) return
 52 Backup network target is not writeable) return
100 Backup schedule was cancelled) return
517 Backup error, check eventlog) return
518 Another backup or recovery is in progress) return
521 Backup Volume Shadow copy operation failed) return
527 Backup recovery planning occupied by other client) return
528 Backup conflict with group policy settings) return
544 Backup engine could not be contacted) return
545 Backup schedule settings not found) return
546 Backup start error, check eventlog) return
561 Backup target could be found) return
564 Backup network target is not writeable) return
612 Backup schedule was cancelled) return
"
```
