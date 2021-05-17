Linux logging
==============

Logrotate
---------

Not checked yet: avoid log files alltogether and run "journalctl" only - properly configured and integrated into log collectors like [filebeat][] or [fluentd][]. 

Classic approach: use "logrotate" daemon:

* `su`: in case log files are written by e.g. the Apache user www-data, the ownership may need changing for access via e.g. [filebeat][] or [fluentd][].
* `delaycompress`: do not compress first rotation, so that contents can still be written here 
* `create`: create new log file to avoid problem with log analysis tools

Config file

* edit `/etc/logrotate.d/example.conf`:

        /var/log/example/example.log {
            size 128M
            daily
            rotate 5
            missingok
            notifempty
            compress
            delaycompress
            su apache apache
            create 0644
            postrotate
                /bin/systemctl reload httpd.service 2>&1 | logger -t EXAMPLE_LOGROTATE
            endscript
        }

Syntax test

    logrotate -d /etc/logrotate.d/example.conf

Run once

    logrotate -vf /etc/logrotate.d/example.conf


[filebeat]: https://www.elastic.co/de/beats/filebeat
[fluentd]: https://www.fluentd.org/
