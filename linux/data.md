# Shell data handling

Sum a list of numbers, one int per line (first column)

    awk '{s+=$1} END {print s}' < numbers.txt

