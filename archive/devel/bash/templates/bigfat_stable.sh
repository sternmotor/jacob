#.SYNOPSIS
#   $0 [-v] [-h][PARAMETERS]
#   Setup routines for bash/sh script scripts and general script template.
#
#   This is no shell script by itself but supports development of other scripts.
#   For using it in your scripts, copy this file as template and write your
#   main() and helper functions. You may also cut off the whole SCRIPT SETUP
#   part and import this file to your script like
#     . "$(dirname "$0")/shellscript-lib.sh"
#
#.DESCRIPTION
#   Initialises robust run of shell resp. bash scripts. Here, "shell" means
#   "sh" or "dash" which lack some features "bash" covers.
#       * sets LANG environment variable to C, so shell commands have english
#         output for parsing and e.g. "grep" expressions
#       * set -e: script exits on every uncatched bad return value of
#         subfunctions or shell commands. Catching means: wrap command
#         with "if-then-else" structure or terminate it like "... || /bin/true"
#       * set -u: script exits if any referenced variable is not set. Very
#         useful when developing scripts. On the downside, extra care must
#         be taken for command line arguments which may not be set. In most
#         cases, it is sufficient to write something like ${1:-} (this means:
#         set to "" if unset) #
#       * set -o pipefail: bash only -  evaluate bad exit code of every command
#         in a pipeline. Without it, only exit of last element in pipe is used.
#
#   Requires setup of cleanup() function which is called at good or bad exit
#   of your shell script. Put whatever code you think makes your script exit
#   nicely, here.
#
#   In-script-logging is not supported by purpose. All error messages from
#   msg_... are written to stddev. Log them to e.g. syslog like
#      my_script 2>&1 | logger -t <script name>
#
#   Verbosity and error handling:
#   Output to console is handled by msg_... functions, supporting verbosity
#   setting and stdout/stderr channel handling. Read PARAMETER -v description
#   first. All msg_... commands print to stderr. This commands mean:
#       msg_debug: * development/ error tracing output, printed with -vv option
#       msg_info: * verbose user info (everything not error or warning)  (-v)
#                  * example: capture/supress shell command output like e.g.
#                    <command> | while read line; do msg_info "$Line"; done
#       msg_start: * store description what is beeing processed for use in
#                    msg_error and msg_fatal messages. In verbose mode, a
#                    starting message is printed. Describe the next action like
#                      "<verb>ing <object(s)>",
#                      e.g. "creating directories in /srv/backup"
#       msg_error: * display error message (re-using msg_start message) and
#                    store this message and error code in $ERROR variable for
#                    display at script end (exit_handler), but continue script.
#       msg_fatal: * like msg_error, but break script here and now.
#       run_debug :  call shell command or function, print command line
#                    in debug mode (-vv)
#       with each msg_... command, some formatting is provided. In case script
#       output is piped to e.g. a log file, no formatting is applied.
#
#   The usage() function prints this help text. Define script PARAMETERS,
#   SYNOPSIS etc. in a comment block at script begin.
#   "NOTES" section is no printed. The format of this help
#   text template is an attempt to bring togehter linux man-page and
#   windows powershell conventions as a platform-independend standard.
#   Call script with -h or --help option
#
#   Command line parameters are analysed for -v|--verbose or -h|--help
#   options which are handled automatically. Do not use this options
#   for your own's script command line definition or rewrite SCRIPT SETUP
#   section. A good practice woul be to handle command line parameters in
#   main() function.
#
#   MISSPKG: specifiy packages which are needed for script to run like:
#      which "sed" > /dev/null 2>&1 || MISSPKG="${MISSPKG:-} sed"
#   and run "check_packages" afterwards. Note that not each command's name is
#   mirrored by debian package name.
#   You can find out about package names for executables like
#     "dpkg -S $( which mtr)"
#   on a system where this executable is installed.
#
#.RISKS
#   * Following command line options are handled by this script automatically,
#     overriding them breaks verbosity handling:
#       -v|--verbose
#       -h|--help
#   * Following function names are occupied, already
#       check_packages()
#       msg_debug()
#       msg_error()
#       msg_fatal()
#       msg_info()
#       msg_start()
#       usage()
#   * Following global variables are occupied:
#       $CNOR $CPUR $CRED
#       $ERROR
#       $MISSPKG
#       $StepMsg
#       $VERBOSITY
#   * -v|--verbose and -h|--help options must be first in command line
#   * Using this template leads to errors in case cleanup() function is not
#     defined
#   * Trapping is set up for pretty much all/following signals:
#       EXIT HUP INT KILL TERM STOP
#     Overriding this trap handling via exit_handler breaks error handling.
#
#.PARAMETER -h or --help
#   Print script usage info, then exit. This parameter is optional.
#   Make sure to have this option specified at beginning of script command line.
#
#.PARAMETER -v or --verbose
#   Set script output verbosity. This parameter is optional.
#   Make sure to have this option specified at beginning of script command line.
#   * by default, no script output is generated except for error or fatal
#     messages
#   * in case one single "-v" resp. "--verbose" option is given, informational
#     user messages are displayed to stderr channel
#   * in case two or more "-v" resp. "--verbose" options are given, developer
#     and error tracing infos are printed to stderr.
#
#.NOTES
#   Company   : fellowtech GmbH
#   Version 1: Gunnar.Mann 16.04.2015
#       New:
#           * finished msg_... tools
#           * added help text, turned tool collection into script template
#       Fixes:
#   TODO
#      * no ideas so far
#
#.LINKS
#   Good sources for bash script development
#   * forget the "Advanced Bash-Scripting Guide"
#   * see Bash FAQ at mywiki.wooledge.org/BashFAQ
#   * http://cheat.errtheblog.com/s/bash
#   * http://www.shell-tips.com

# ---------------------------------------------------------------------------
# CONFIG DEFAULTS (user options)
# ---------------------------------------------------------------------------
#DEFAULT_SSH_PORT="22"

# ---------------------------------------------------------------------------
# SCRIPT CONSTANTS (internal use)
# ---------------------------------------------------------------------------
#SSH_OPTIONS="-o PasswordAuthentication=no"
#LOCK_BASE_DIR="/var/lock"
# missing packages
# which "wget" > /dev/null 2>&1 || MISSPKG="${MISSPKG:-} wget"

# debug helper: test mode command line options
#set  --  "arg1" "agr 2 " "agrg 3" "-v" "-vvvv"

# ---------------------------------------------------------------------------
# MAIN SCRIPT
# ---------------------------------------------------------------------------
#main() {
#    while [ $# -gt 0 ]; do
#        echo "found command line option '$1'"
#        shift
#    done
#    msg_debug "ssh options: '$SSH_OPTIONS'"
# }

# ---------------------------------------------------------------------------
# SCRIPT FUNCTIONS
# ---------------------------------------------------------------------------
#cleanup(){
#    msg_info "Finished"
#}

# ---------------------------------------------------------------------------
# SCRIPT SETUP                                               
# ---------------------------------------------------------------------------

# HARDEN SCRIPT
    export LANG=C   # avoid errors due to localized command output
    set -o nounset  # avoid using non initialised variables (rm -rf "$dir")
    set -o errexit  # exit the script at non-true return value
    [ -z "${BASH_VERSION:-}" ] || set -o pipefail # bash-only option

# USAGE: filter help text from script header, print and expand variable contents
    usage() {
        local TmpFile=$(mktemp); echo 'cat << EOU' > "$TmpFile"
        sed -e /^\#\.SYNOP/,/^\#\.NOTES/!d -e /^\#\.NOTES/d -e 's|^\#[\.\ ]||' -e 's|^#||' "$0" >> "$TmpFile" || { rm "$TmpFile"; return 1; }
        echo 'EOU' >> "$TmpFile"; . "$TmpFile"; rm "$TmpFile"
    }

# MESSAGES, LOGGING
    ERRORS=""   # container for storing errors during different backups,
                # append "." to this string for each error
    if [ ! -t 1 ]; then CNOR=''; CPUR=''; CRED='' # no colors in pipe
    else # recognize different color codes for bash vs. unix shell
        [ -z "${BASH_VERSION:-}" ] \
        && { CPUR='\033[35;1m'; CRED='\033[31;1m'; CNOR='\033[0;0m'; } \
        || { CPUR=$'\e[35;1m'; CRED=$'\e[31;1m'; CNOR=$'\e[0;0m'; }
    fi
    msg_debug() { [ ${VERBOSITY:-0} -le 1 ] || echo "${CPUR}[DEBUG] ${@:-}$CNOR" 1>&2; }
    msg_info () { [ ${VERBOSITY:-0} -lt 1 ] || echo "${@:-}" 1>&2; }
    msg_start() { [ -z "${BASH_VERSION:-}" ] && StepMsg="$(echo ${@} | tr -s [:space:] )" || StepMsg="$(echo ${@^} | tr -s [:space:] )"; msg_info " * $StepMsg" 1>&2; }
    msg_warn () { local EC=$?; local Msg="${@:-${StepMsg:-Unknown}}"; ERRORS+="."; echo "${CRED}[ERROR] ${Msg}.$CNOR" 1>&2 ; }
    msg_error() { local EC=$?; local Msg="${@:-${StepMsg:-Unknown}}"; [ $EC -gt 0 ] || EC=1; echo "${CRED}[CRITICAL] Error ${Msg}!$CNOR" 1>&2 ; exit $EC; }

# DEFAULT COMMAND LINE OPTIONS: check verbosity and help options -h, -v, -vv
    TmpFile=$(mktemp)
    while [ $# -gt 0 ]; do case "$1" in
        -v|--verbose) VERBOSITY=$(( ${VERBOSITY:-0} + 1 ));; # 0+1 +1 +1
        -vv*|--debug) VERBOSITY=2;;  # DEBUG LEVEL
        -h|--help) trap - EXIT HUP INT KILL TERM STOP; usage; exit 0;;
        -D|--dry|--dry-run) DRY_RUN=true; VERBOSITY=$(( ${VERBOSITY:-0} + 1 )); msg_info "$CPUR***Dry Run***$CNOR" ;;
        *) echo "$1" >> "$TmpFile"
    esac; shift; done
    # copy RemainingArgs to $@
    while read Arg; do set -- "$@" "$Arg"; done < "$TmpFile"; rm "$TmpFile"

# OTHER
    check_packages() { local MISSPKG="$@"; [ -z "$MISSPKG" ] || msg_error "Missing packages, try 'apt-get install -y  $MISSPKG'"; }
    which "sed" > /dev/null 2>&1 || MISSPKG="${MISSPKG:-} sed"
    which "awk" > /dev/null 2>&1 || MISSPKG="${MISSPKG:-} awk"
    check_packages ${MISSPKG:-}

    run_debug() { local Cmd="$@"; msg_debug "$Cmd"; eval "$@" || return $?; } # use $@ and $Cmd must be called exactly like written here, does not run otherwise

# SET ERROR TRAP AND START MAIN LOOP
    exit_handler() { local EC=$?; trap - EXIT HUP INT KILL TERM STOP # disable trap handler
        if [ ! -z "${ERRORS:-}" ]; then echo "${CRED}[CRITICAL] ${#ERRORS} errors occured during script run.$CNOR"; EC=${EC:-1}; fi
        msg_start "Cleaning up"; cleanup && local CL_EC=0 || local CL_EC=$?; [ $CL_EC -gt 0 ] && [ $EC -eq 0 ] && exit $CL_EC || exit $EC
    }
    trap exit_handler EXIT HUP INT KILL TERM STOP
    main "$@"

