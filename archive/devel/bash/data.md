# Bash data handling


## Text operations

Retrieve 3rd word in 1st line:
```
ip r | awk 'NR==1{print $3}'
```

Does a given string match a given glob pattern?
fnmatch() {
    case "$2" in $1) return 0 ;; *) return 1 ;; esac
}
```

## Numbers


Print human readable number 
```
numfmt --to=iec-i --round=nearest $number    # --padding, --suffix,
```

Convert human reable string to number
```
echo 1K | numfmt --from=iec
```

## Dict, CSV

Split out csv variables from in-script-data, see (stackexchange)[https://unix.stackexchange.com/questions/9784/how-can-i-read-line-by-line-from-a-variable-in-bash]

```
FT='
ft-gilching-firewall,jarvis,firewall.ft.local,22,/srv/ansible/private/ssh/remote/ft/id_rsa
systems-firewall,jarvis,firewall.systems.fellowtech.com,20022,/srv/ansible/private/ssh/remote/ft/id_rsa
staging-firewall,jarvis,firewall.systems.fellowtech.com,20022,/srv/ansible/private/ssh/remote/ft/id_rsa
'
while IFS= read -r line
do
    case $line in
        ''|'#'*)
            continue
        ;;
        *)
            # read line csv parts
            OLD_IFS="$IFS"
            IFS=','; read host user addr port key < <(echo "$line")
            IFS="$OLD_IFS"
            echo $addr
        ;;
    esac
# Printf '%s\n' "$var" is necessary because printf '%s' "$var" on a
# variable that doesn't end with a newline then the while loop will
# completely miss the last line of the variable.
done < <(printf '%s\n' "$FW")
```

Generate random numbers including min and max

```
max=2019
min=2016
for i in $(seq 1 10); do
    echo $((($RANDOM % $(($max - $min + 1)) ) + $min ))
done
```


## Array

# handle exclude and include
```bash
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# handle exclude and include options
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
filter_items() {
    # Take all available objects, select includes (by wildcard) and
    # substract excludes (by wildcard)
    # excludes override/narrow include selection.
    #   in case IncludeExprs= "" or *: all objects selected
    #   in case ExcludeExprs= "" : no objects removed (return all included objects )
    # fnmatch provides support for Unix shell-style wildcards

    # expecting names of array variables for: AllItems, IncludeExprs, ExcludeExprs
    # sets "ResultItems" array

    # Read caller array varibles by their names reference
    local Name="$1[@]" && local AllItems=("${!Name}")
    local Name="$2[@]" && local IncludeExprs=("${!Name:-}")
    local Name="$3[@]" && local ExcludeExprs=("${!Name:-}")
    local Item
    local ItemIndex
    local IncludeItems
    local Expr

    # find out what to do part I: collect includes
    if test -z "${IncludeExprs:-}"
    # copy full os component list in case no SRC was specified ...
    then
        IncludeItems=("${AllItems[@]}")
    # ... or compare IncludeExprs expressions against full OS_ COMPONENTS list
    else
        IncludeItems=()  # empty array to start with
        for Item in "${AllItems[@]}"; do
            for Expr in "${IncludeExprs[@]}"; do
                if fnmatch "$Expr" "$Item"; then
                    IncludeItems+=("$Item")
                    break
                fi
            done
        done
    fi

    if test -z "${IncludeItems:-}"; then
        msg_error "\"${IncludeExprs[@]}\" not found in \"${AllItems[@]}\""
    fi

    # find out what to do part II: match includes against excludes:
    # create a copy of array so original can be used for error message
    ExcludeSurvivorItems=("${IncludeItems[@]}")
    for ItemIndex in "${!IncludeItems[@]}"; do # iterate over array index
        for Expr in "${ExcludeExprs[@]:-}"; do
            if fnmatch "$Expr" "${IncludeItems[$ItemIndex]}"; then
                ExcludeSurvivorItems[$ItemIndex]='' # remove element from array
                break
            fi
        done
    done

    # strip empty result items, check if there is anything left
    ResultItems=()
    for Element in "${ExcludeSurvivorItems[@]}"; do
        if [ ! -z "$Element" ]; then   # add  non-emty elements
            ResultItems+=("$Element")
        fi
    done

    if test -z "${ResultItems:-}"; then
        msg_error "Removing \"${ExcludeExprs[@]}\" from \"${IncludeItems[@]}\" left nothing"
    fi
}

