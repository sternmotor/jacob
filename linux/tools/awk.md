# AWK programming

* See  



Run awk with no input and named variables

    awk -v argus=34545 -v beton=2 'BEGIN{print argus + beton}'


Convert input to human readable number (see [stackexchange](https://unix.stackexchange.com/questions/44040/a-standard-tool-to-convert-a-byte-count-into-human-kib-mib-etc-like-du-ls1))

    du --block-size=1 | awk '
        function human(x) {
            if (x<1000) {return x} else {x/=1024}
            s="kMGTEPZY";
            while (x>=1000 && length(s)>1)
                {x/=1024; s=substr(s,2)}
            return int(x+0.5) substr(s,1,1)
        }
        {sub(/^[0-9]+/, human($1)); printf("%-4s %s\n", $1, $2) }
    '

Convert elapsed `$SECONDS` to "days H:M:S" - compatible to macOS 
awk tool, where awk `strftime` is not available. Prints info
right-aligned in terminal

    awk -v elapsed=$SECONDS -v min_elapsed=3  \
    -v termwith=$COLUMNS -v dt="$(date +'%Y-%d-%m %H:%M:%S')" \
    'BEGIN{    
        msg=""
        if(elapsed >= min_elapsed) {
            msg = msg "["
            d = elapsed/60/60/24	
            s = elapsed%60
            m = elapsed/60%60
            h = elapsed/60/60%24
            if (d >= 1) msg = msg int(d) "d "   # add days info
            msg = msg sprintf("%02d:%02d:%02d | %s]", h, m, s, dt)      
        }
        printf("%" termwith "s\n", msg)
    }'


data
----

Check if value is in array - see [this diskussion](https://stackoverflow.com/questions/26746361/check-if-an-awk-array-contains-a-value)

    echo "A:D:C:D:E:F" | tr ':' '\n' | \
    awk 'BEGIN{ 
            split("A D F", valid_values) 
            # now revert k,v in valid_values:
            for (i in valid_values) valid[valid_values[i]]=""
        }  
        $1 in valid
    '



