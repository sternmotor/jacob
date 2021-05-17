Linux process management
========================

Lower priority of current process (script)

    renice +19 -p $$ >/dev/null 2>&1
    ionice -c3 -p $$ >/dev/null 2>&1
