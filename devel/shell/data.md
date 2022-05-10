Bash data handling
==================




Calculations
------------

Calculate float (no input)

    awk 'BEGIN {printf "%8.3f\n", 3/22.7 }'

Sum up all numbers in a text file

    awk '{ sum += $1 } END { print sum }' "$temp_dir/all_sizes_mb"


Check if string is a integer - dows not work with floats

    test [ ! -z "$number" ] && [ -z "${number//[0-9]/} ]

Arrays
------


Dictionaries, Hash
------------------

Create and read assoziative array:

    declare -A MYMAP
    MYMAP[foo]=bar 
    echo ${MYMAP[foo]}


Read from variable line by line

    SSH_PUBKEYS='
        xxx 1
        yyy 2
        zzz 3
    '

    echo  "$SSH_PUBKEYS" | awk NF | while read -r line; do
        echo "line: $line"
    done 
