Abstract coding patterns
========================

Patterns focussed on server system operation


Run concurrent tasks on at a time (locking mechanism)


    LOCK_FILE="<scope>.lock"
    while /bin/true:

        if lockfile-check "$LOCK_FILE"; then
            echo "running already"
            sleep 5
            continue
        else
            echo "starting action"
            lockfile-create "$LOCK_FILE"
            trap "lockfile-remove "$LOCK_FILE"" EXIT INT TERM
            <do something>
            break
        fi

    lockfile-remove "$LOCK_FILE"
