# BackupPC


Restore latest backup from dockerized backuppc, here a docker volume

TARGET=/srv/restore-$(date +%Y-%m-%d)
HOST=host.example.com
SHARE=/srv/docker/volumes
DIR=db_data
mkdir -p $TARGET

docker exec -tu backuppc backuppc \
    /usr/local/BackupPC/bin/BackupPC_tarCreate \
    -h jira2020.app.infra.gs.xtrav.de \
    -n -1 \
    -s "$SHARE" "$DIR" \
    | zstd -1 > "$TARGET/${SHARE}_${DIR}.tar.gz"
