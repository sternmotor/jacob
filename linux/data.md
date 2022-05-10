# Shell data handling

Sum a list of numbers, one int per line

    awk '{s+=$1} END {printf "%.0f", s}' < numbers.txt

