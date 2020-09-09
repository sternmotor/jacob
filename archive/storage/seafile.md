# Seafile Client
## Linux

Init seafile client, see [Github Haiwen](https://github.com/haiwen/seafile/blob/master/app/seaf-cli)
```
mkdir /var/log/seafile /media/data/seafile
rm -rf /etc/seafile
mkdir /media/data/seafile
seaf-cli init --confdir /etc/seafile --dir /media/data/seafile
seaf-cli start -c /etc/seafile/
seaf-cli download -l da92fa7c-8b35-4530-8e8e-33bd6b37213b -s https://Sternmotor.net/seafile -d /media/data/seafile -u gunnar@manns-online.net -p xxx -c /etc/seafile/
#ccnet-init -n Alfred -c /etc/seafile
#ccnet -f /var/log/seafile/ccnet.log -c /etc/seafile/
````
