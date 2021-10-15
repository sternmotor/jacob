Bash data handling
==================

Calculations
------------

Calculate float (no input)

    awk 'BEGIN {printf "%8.3f\n", 3/22.7 }'

Sum up all numbers in a text file

    awk '{ sum += $1 } END { print sum }' "$temp_dir/all_sizes_mb"


Arrays
------


Dictionaries, Hash
------------------

Create and read assoziative array:

    declare -A MYMAP
    MYMAP[foo]=bar 
    echo ${MYMAP[foo]}

