# Linux network



## SSH
### Alternate port
See [Diskussion](https://adayinthelifeof.nl/2012/03/12/why-putting-ssh-on-another-port-than-22-is-bad-idea/):

When we start SSH on port 22, we know for a fact that this is done by root or a root-process since no other user could possibly open that port. But what happens when we move SSH to port 2222? This port can be opened without a privileged account, which means I can write a simple script that listens to port 2222 and mimics SSH in order to capture your passwords. And this can easily be done with simple tools commonly available on every linux system/server. So running SSH on a non-privileged port makes it potentially LESS secure, not MORE. You have no way of knowing if you are talking to the real SSH server or not.

### Port-Knocking

There are 3rd party tools, which are implemented in userland so don’t use them. Instead, you can do this with simply using iptables, which has got a very nifty module called “recent”, which allows you to create simple - yet effective - port knocking sequences.

```
${IPTABLES} -A INPUT -p tcp --dport 3456 -m recent --set --name portknock
${IPTABLES} -A INPUT -p tcp --syn --dport 22 -m recent --rcheck --seconds 60 --name portknock -j ACCEPT
${IPTABLES} -A INPUT -p tcp --syn --dport 22 -j DENY
```

As soon as something tries to connect to port 3456 (yes, a non-privileged port, but no problem as nothing is running on it), it will set a flag called “portknock”. Now, when we try to setup a connection to the SSH port, it will check to see if your IP has set a “portknock” flag during the last 60 seconds. If not, it will not accept the connection. And the third line will by default deny any access to SSH together as a failsafe.

### Expect
Run dialog via ssh
```
expect <<- EOF
    spawn ssh -o StrictHostKeyChecking=No -o ConnectTimeout=3 USER@HOST
    set timeout 3
    send "execute shutdown\n"
    expect "(y/n)"
    send "y\n"
EOF
```
Ubuntu: install expect like below, skip X11 recommendations
```
sudo apt-get install --yes --no-install-recommends expect
```



## nmap port scanner

Check open ports on local host
```bash
nmap -sV localhost
```

## Latency, QOS

Introduce network latency og 50ms:
```bash
tc qdisc add dev eth0 root netem delay 50ms
```
