#!/bin/bash
# USAGE
#   rotate --target-dir TARGETDIR [--schedule SCHEDULE] [--print] [--keep] [--help] 
# 
# DESCRIPTION
#     Script for thinning out backup session directories by examining 
#     timestamps given in names of directories under TARGET_DIR.
#      
#     Run through TARGET_DIR and remove directory entries which fall out of
#     specified SCHEDULE time slots. 
#      
#     This script expects a file structure under TARGET_DIR where each 
#     session dir is named by the timestamp it is created.
#      
#     TARGET_DIR/
#           2014-12-31_23:45/   # last backup of last year
#           2015-01-31_23:20/   # last backup of last month
#           2015-02-01_23:31/   # kept dayly backup
#           2015-03-01_23:34/   # kept dayly backup
#           2015-03-01_13:12/   # latest yearly/monthly/dayly session
#      
#     It is assumed that this script is called at the minimum necessary 
#     interval by e.g. cron. If, for example, backups of the last 5 hours 
#     should be kept when rotating then the backupscript must be called at  
#     least once per hour. 
#      
#     SCHEDULE is specified like minutes.hours.days.weeks.months.years. E.g. 
#     0.0.14.8.6.10 means: keep 0min 0hrs 14days 8weeks 6mon 10yrs.
#      
#     For example 0.0.20.0.6.10 means: throw away every session but 
#       - the latest/newest session for each of the last 20 days, 
#       - the latest/newest session for each of the last 6 months,
#       - the latest/newest session for each of the last 10 years
#      
#     For example 0.0.0.0.0.5 means throw away every session but 
#       - the latest/newest session for each of the last 5 years
#     After running daily backups for 5 years, you have 4 december sessions 
#     and the backup of today representing the newest session of this year.
#      
# OPTIONS
#     --target-dir|-t TARGET_DIR
#         directory where backup sessions are kept, must exist
#         
#     --schedule|-s SCHEDULE
#         schedule for backup sessions to-be-kept, specify like
#         minutes.hours.days.weeks.months.years. Default is 0.0.7.4.6.10.
#  
#     --print|-p
#         print list of directory entries to-be-removed (relative to 
#         TARGET_DIR), newest first. Do not remove any dir
#    
#     --keep|-k
#         print list of directories which are not removed but kept - for
#         debugging; implies --print
#  
#     --help|-h
#         print this help
#  
# EXAMPLE
#     rotate --target-dir /srv/backups -s 0.0.7.4.10.10  
#     rotate -t /mnt/backup/ticket -s 0.0.7.4.6.3 --print

DEFAULT_SCHEDULE="0.0.7.4.6.10" # keep  0min 0hrs 14days 8weeks 6mon 10yrs of sessions
DEFAULT_MODE='remove'       # may be remove or keep
DEFAULT_PRINT='no'


# handle command line options and defaults, start action on TARGET_DIR
main() {

    # load defaults
    local Schedule=$DEFAULT_SCHEDULE
    local Mode=$DEFAULT_MODE
    local Print=$DEFAULT_PRINT

    # collect commandline options
    while [ $# -gt 0 ]; do
        case "${1:-}" in
            --target-dir|--target|--targetdir|-t)
                local TargetDir="${2:-}"
                shift 2
            ;;
            --schedule|-s)
                local Schedule="${2:-}"
                shift 2
            ;;
            --keep|-k)
                local Mode='keep'
                local Print='yes'
                shift 1
            ;;
            --print|-p)
                local Print='yes'
                shift 1
            ;;
            # print help (commented text at top of script file) and exit
            --help|-h)
                sed -e 1d -e '/^$/,$d' -e 's|^\#\ ||' $0
                exit 0
            ;;
            # print help (commented text at top of script file) and error-exit
            *)
                sed -e 1d -e '/^$/,$d' -e 's|^\#\ ||' $0
                echo "Error: unknown option \"${1:-}\"!" 1>&2
                exit 1
            ;;
        esac
    done

    # validate input parameters
    if [ -z "${TargetDir:-}" ]; then
        echo "TARGET_DIR not specified, check --help option!" 1>&2
        exit 1
    fi

    if [ ! -d "${TargetDir:-}" ]; then
        echo "TARGET_DIR directory not found 1>&2"
        exit 1
    fi

    if [ -z "${Schedule:-}" ]; then
        echo "Empty SCHEDULE definition specified, check --help option!" 1>&2
        exit 1
    fi

    # run 
    read_sessions "$TargetDir" \
    | filter_sessions "$Schedule" "$Mode" \
    | while read TimeStamp; do
        DateString=$(date --date="@$TimeStamp")

        # print only
        if [ $Print == 'yes' ]
        then
            echo "${Mode}ing $DateString"
        # print and remove
        else
            echo -n "Removing session \"$DateString\" ... "
            if remove_session "$TargetDir/" "$TimeStamp"
            then
                echo "ok"
            else
                echo "ERROR"
                exit 1
            fi
        fi
    done
}


filter_sessions() {
    # expects session time stamps (epoch seconds) to be piped in, pipes out
    # all bad sessions which are not important for keeping rotation schedule
    # strategy: keep newest session for each interval, return all other sessions

    local Rotation="$1"    # something like 5.10.14.8.6.10
    local RotationMode="$2"
    local Session="" # counter variable
    local AllSessions=""
    local GoodSessions=""

    # read input sessions from stdin into variable, validate values
    while read Session; do
        # validate input
        local Now=$(date +%s)
        if [ $Session -gt 0 ] && [ $Session -le $Now ]
        then
            AllSessions="$AllSessions $Session"
        else
            echo "Error: session '$Session' is invalid, expecting epoch seonds like 1-$Now" 1>&2
        fi
    done
    local AllSessionsSorted=$(echo $AllSessions | tr ' ' '\n' | sort -r | uniq )

    # populate $GoodSessions by finding sessions which are in some
    # rotation schedule interval

    while read IntervalOldest IntervalNewest IntervalName IntervalNumber; do
        for Session in $AllSessionsSorted; do
            if [ $Session -ge $IntervalOldest ] && [ $Session -le $IntervalNewest ]
            then
                GoodSessions="$GoodSessions $Session"
                break
            fi
        done
    done < <(get_schedule_intervals "$Rotation")

    # filter out all sessions from $AllSessionsSorted which shall get removed
    local GoodSessionsSorted=$(echo $GoodSessions | tr ' ' '\n' | sort | uniq)

    # keep mode: printgood session
    if [ $RotationMode == 'keep' ]
    then
        for Session in $AllSessionsSorted; do
            if echo $GoodSessionsSorted | grep -qw $Session; then
                # $session is not a good session
                echo $Session
            fi
        done

    # remove or print mode: print bad session
    else
        for Session in $AllSessionsSorted; do
            if ! echo $GoodSessionsSorted | grep -qw $Session; then
                # $session is not a good session
                echo $Session
            fi
        done
    fi
}


get_schedule_intervals() {
    local Schedule="$1"
    local Counter=""
    local Oldest=""
    local Newest=""

    # analyse rotation string, store single values Keep - Variables
    read KeepMin KeepHou KeepDay KeepWee KeepMon KeepYea < <(
        echo $Schedule | tr '.' ' '
    )
                         # MaxCounter      # Oldest          # Newest
    get_date_interval  "$KeepMin" "minute" $(date +%H:%M:00) $(date +%H:%M:59)
    get_date_interval  "$KeepHou" "hour"   $(date +%H:00:00) $(date +%H:59:59)
    get_date_interval  "$KeepDay" "day"    "00:00:00"       "23:59:59"
    get_date_interval  "$KeepWee" "week"   "last monday 00:00:00" "sunday 23:59:59"
    # monthes need special procedure handling different month lengths
    get_month_interval "$KeepMon"
    get_date_interval  "$KeepYea" "year"   $(date "+%Y-01-01T00:00:00") $(date "+%Y-12-31T23:59:59                        ")
}

get_date_interval() {
    # call date manipulation loop for minutes, days, hours, weeks ...
    local MaxCounter="$1"  #14,6, 365
    local Counter=
    local IntervalName="$2" # week, minute
    local IntervalOldest="$3"
    local IntervalNewest="$4"

    for Counter in $(seq 1 $MaxCounter ); do
        local Oldest=$(date --date="$IntervalOldest $(( $Counter - 1 )) ${IntervalName}s ago" +%s)
        local Newest=$(date --date="$IntervalNewest $(( $Counter - 1 )) ${IntervalName}s ago" +%s)
        echo $Oldest $Newest $IntervalName $Counter
    done
}

get_month_interval() {
    # call date manipulation loop for months. Month calculatio is special
    # since each month has different length and there is no thing like e.g.
    # "sunday" to mark a week's end

    local MaxCounter="$1"  #14,6, 365
    local Month=

    # prepare table with last month's days, occupy array 1...12
    local Month=""
    for Month in $(seq 1 $MaxCounter); do
        local OldestDate=$(date --date="$(( $Month -1 )) months ago" "+%Y-%m-01 00:00:00" )
        local Oldest=$(date --date="$OldestDate" +%s)
        local NextMonthBegin=$(date --date="$(( $Month - 1 )) months ago + 1 month " "+%Y-%m-01 00:00:00" )
        local Newest=$(date --date="$NextMonthBegin 1 second ago" +%s)
        echo $Oldest $Newest month $Month
    done
}

read_sessions() {
    # return epoch seconds time stamp for each existing backup session
    # expects session dirs to be named like YY-mm-dd_HH-MM-SS
    local DIR="$1"

    ls -- "$DIR" | convert_dir2timestamps
}

convert_dir2timestamps() {
    # run / ssh command relies on proper IFS setting, so
    # dir name splitting is taken out of read_session to here

    local IFS='_'   # separate YY-mm-dd_HH-MM-SS into YY-mm-dd_ and HH-MM-SS
    while read EntryDate EntryTime WeekDay; do
        local FormattedEntryTime=$(echo $EntryTime | tr '-' ':')
        # return entry only if date can be read
        if date --date="$EntryDate $FormattedEntryTime" >/dev/null 2>&1; then
            date --date="$EntryDate $FormattedEntryTime" +%s
        fi
    done

}

remove_session() {
    # removes backup sessions handed over via pipeline
    # pipe input: epoch seconds
    # expects session dirs to be named like YY-mm-dd_HH-MM-SS
    local BACKUP_DIR="$1"
    local TimeStamp="$2"

    local DirName=$( date --date="@$TimeStamp" +%Y-%m-%d_%H-%M-%S_%a )

    rm -rf "$BACKUP_DIR/$DirName"
}


LANG=C          # avoid errors due to localized command output
set -o pipefail
set -o nounset  # avoid using non initialised variables (rm -rf /$dir)
set -o errexit  # exit the script at non-true return value
main "$@"
