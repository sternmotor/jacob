# Bash time and unit handling


Convert number to human readable representation
```bash

bytestohuman() {
    # converts a NUMBER to a human readable format in IEC binary notation
    # (base-1024), rounded to DIGITS decimal places for anything larger than a
    # byte. switchable to PADDED format and BASE-1000 if desired.
    local NUMBER=${1:-0}     # input number
    local PADDED=${2:-yes}      # padding on (yes) or off (no)
    local BASE=${3:-1024}    # 2^x base: put 1024 or 1000 here
    local DIGITS=${4:-2}     # number of digits to put after "."

    awk -v bytes=$NUMBER -v pad=$PADDED -v base=$BASE -v digits=$DIGITS '
        function human(x, pad, base, digits) {
            if(base!=1024)base=1000
            basesuf=(base==1024)?"iB":"B"
            s="BKMGTEPYZ"
            while (x>=base && length(s)>1) {
                x/=base
                s=substr(s,2)
            }
            s=substr(s,1,1)
            xf=(pad=="yes") ? ("%"5+digits"."digits"f") : ("%."digits"f")
            s=(s!="B") ? (s basesuf) : ((pad=="no") ? s : ((basesuf=="iB")?(s "  "):(s " ")))
            return sprintf( (xf " %s"), x, s)
        }
        BEGIN{
            print human(bytes, pad, base, digits)
        }
    '
}
```


Convert epoch seconds to timestamp
```
date --date="@$SomeSeconds" +%Y-%m-%d_%H-%M-%S_%a
```

Generate random timestamps - need double random for modulo operation with long int
```
NowSeconds=$(date +%s)
DeltaSeconds=$(( 3600*24*365*5 ))   # 2 years

for i in $(seq 1 10); do
    SomeSeconds=$(( $NowSeconds - ( $RANDOM$RANDOM % $DeltaSeconds ) ))
    echo $( date --date="@$SomeSeconds" +%Y-%m-%d_%H-%M-%S_%a)
done
```
