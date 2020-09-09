# Linux logging


Rotate logs > 128MB, check daily
edit `/etc/logrotate.d/service`

```
/srv/modoc/modoc_cron/cron.log {
        size 128M
        daily
        rotate 5
        missingok
        notifempty
        compress
        delaycompress
        su modocadmin modocadmin
        create 0644
}
```
