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
