# Config file handling in bash scripts

Set parameter in config file

```
function setcfg() {
    # set parameter in config file
    # usage: setcfg <config file> <parameter> <value> or
    #        setcfg <config file> <parameter=value>"

    local ConfigFile="$1"
    # check wether variable setting is of type 'Variable=Value'  or 'Variable Value'
    # this is determined by the way the arguments are handed over to this function

    if [ `echo $2 | sed '/=/!d' | wc -l` = 0 ]
    then
        # assume <parameter> <value>
        local Variable="$2"
        local Value="$3"
        local Delimiter=" "
    else
        # assume  <parameter=value>
        local Variable=`echo $2 | cut -d= -f1`
        local Value="\"`echo $2 | cut -d= -f2-`\""
        local Delimiter="="
    fi

    # check if config file and directory exist, already (create if necessary)
    checkfile $ConfigFile

    # check if variable is set, at all
    if [ "`sed "/^$Variable$Delimiter/!d" $ConfigFile | wc -l`" = 0 ]
    then
        # variable is unset, add variable and value to end of file
        echo "$Variable$Delimiter$Value" >> $ConfigFile
    else
        # variable is set already, replace value
        sed -i -e "s|^\(${Variable}\)${Delimiter}.*|\1${Delimiter}${Value}|"  $ConfigFile
    fi
}
```

Read parameter from config file
```
function getcfg() {
   # opposite to setcfg: extract parameter from config file
   # usage: getcfg <config file> <parameter>
   # expects format ^parameter=value
   local ConfigFile="$1"
   local Variable="$2"

   sed "/^${Variable}=/!d;s/\"//g" $ConfigFile | cut -d= -f2-
}
```
