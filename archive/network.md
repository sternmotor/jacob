# Network tools


## firewall

Close port for maintenance (example external requests to port 28017)
```
iptables -I INPUT -p tcp ! -s 127.0.0.1/8 --dport 27017 -j DROP
# do stuff here
iptables -F
```

## tcpdump

Log ascii traffic
```
tcpdump dst <host> -qA 
```
