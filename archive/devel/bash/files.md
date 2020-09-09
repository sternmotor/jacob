# Bash scripting - file handling


* remove comments, delete empty lines, combine spaces etc.
```
sed -e '/^$/d;s/^[ \t]*//;s/[ \t]*$//;/^$/d;s/[ \t]\#.*//' \
-e 's/^#$//;s/^\#[^!].*//;/^$/d' -e 's/[ \t]\+/ /g' -e 's/[ \t]*=[ \t]*/=/' $CONFIG_PATH
```

