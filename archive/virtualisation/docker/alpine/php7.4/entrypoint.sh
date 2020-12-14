#!/bin/sh
set -e


# run other entrypoint scripts - if present
find '/docker-entrypoint.d' -type f -executable 2>/dev/null || /bin/true \
| sort | while read entrypoint_script; do 
    echo "*** launching $entrypoint_script ***"
    "$entrypoint_script"
done


# make container process user run with external PUID and GUID matching 
# calling user, modify home permissions
if [ ! -z "$PGID" ]; then 
    groupmod --gid $PGID                  'www-data'
    usermod  --uid $PUID --gid $PGID      'www-data'
    chown -R $PUID:$PGID "$(getent passwd 'www-data' | cut -d ':' -f6)"
fi


# in case container is executed with options or non-executable string as
# first parameter, start container process CMD
if which "${1:-}" >/dev/null 2>&1
then
    exec "$@"
else    
    exec 'php-fpm' "$@"
fi
