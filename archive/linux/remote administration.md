# Linux Remote Administration

## AutoSSH
Poor-man's VPN in case you need only some ports forwarded. SystemD sevice may look like:

* edit `/etc/systemd/system/autossh-zabbix.service`:

```
[Unit]
Description=AutoSSH Port Forwarder
After=network.target
After=syslog.service

[Service]
# daemon options
Type=forking
Restart=always
RestartSec=5
PIDFile=/var/run/autossh/connection1.pid

# autossh options
EnvironmentFile=/etc/default/autossh-connection1.conf
Environment=AUTOSSH_PIDFILE="$PIDFile"
Environment=AUTOSSH_POLL=60
Environment=AUTOSSH_FIRST_POLL=10
Environment=AUTOSSH_GATETIME=0
Environment=AUTOSSH_LOGLEVEL=3
# -p [PORT]
# -l [user]
# -M 0 --> no monitoring port (would require echo server to be set up)
# -N Just open the connection and do nothing (not interactive)
# -F used to skip reading ssh config where controlmaster settings 
#    (not working) may hide
ExecStartPre=/usr/bin/install --owner root --group root --mode 0750 --directory /var/run/autossh
ExecStart=/usr/bin/autossh -M 0 -N -q -f \
          -o ExitOnForwardFailure=yes \
          -o StrictHostKeyChecking=no \
          -o ServerAliveCountMax=5 \
          -o ServerAliveInterval=45 \
          -o TCPKeepAlive=yes \
          -p ${RELAY_PORT} -l ${RELAY_USER} ${RELAY_ADDR} \
          -L ${LOCAL_ADDR}:${LOCAL_PORT}:${REMOTE_ADDR}:${REMOTE_PORT}
[Install]
WantedBy=multi-user.target
```

* configure connection and port forwarding in `/etc/default/autossh-connection1.conf`

```
# Settings for AutoSSH Port Forwarder

# CONNECTION
# Relay server is the ssh server to connect to for establishing port forwardings
RELAY_ADDR=ssh_gate.example.com
RELAY_PORT=22222
RELAY_USER=sshproxy

# PORT FORWARDING
# Forwarding remote server (making it available here at proxy host) is done by
# connecting ssh to relay server and establishing port forwarding of REMOTE 
# to LOCAL
REMOTE_ADDR=172.31.252.11
REMOTE_PORT=10051
LOCAL_ADDR=127.0.0.1
LOCAL_PORT=10052
```

* enable service

```
systemctl daemon-reload
systemctl enable autossh-connection1
systemctl start autossh-connection1
```
 

## SSH Server

* Access restrictions: see [here](https://www.linuxquestions.org/questions/linux-security-4/securing-ssh-allow-denying-and-match-statements-4175530596/):

```
PasswordAuthentication no
X11Forwarding no

Match Group gui Address 192.168.1.*
    X11Forwarding yes
Match Address 192.168.1.*
    PasswordAuthentication yes
```

## SSH Client

* config file

```
cat << 'SSH_CONFIG_END' > ~/.ssh/config
# SSH client configuration
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%h_%p_%r
    ControlPersist 4h
    ServerAliveInterval 60
    ServerAliveCountMax 5
    User root
    Compression yes
    # https://stribika.github.io/2015/01/04/secure-secure-shell.html
    UseRoaming no
    KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
    Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
    MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,umac-128@openssh.com
# Options: LocalForward LocalAdress:Port RemoteAdress:Port
Host st sternmotor
    hostname sternmotor.net
    port 30001
SSH_CONFIG_END    
mkdir -p ~/.ssh/sockets
chmod 0700 ~/.ssh/sockets
``` 

Run command on multiple servers - important is to redirect stdin

```
for i in server1 server2 server3 servern; do
    echo $i; {
        ssh $i.systems.fellowtech.com "service zabbix-agent start"
    } < /dev/null
done
```

Run SSH command with password in variable

```
cat << SSH_CMD | sshpass -p "$AdminPassword" ssh $SSH_OPTIONS user@server.tld
    ls /etc
SSH_CMD
```

## SSH Jump host, bastion host, SSH Relay

### Collection

Jump host architecture: see [Diskussion](https://serverfault.com/questions/903253/ssh-access-gateway-for-many-servers)

* "Use the gateway server as jump host that accepts every valid key (but can easily remove access for a specific key which removes access to all servers in turn) and then add only the allowed keys to each respective server. After that, make sure you can reach the SSH port of every server only via the jump host."
* 2 Factor Auth on the jump host
* Consider [Gentoo Wiki Comments](https://wiki.gentoo.org/wiki/SSH_jump_host)
* Jump host for wan connections: [MOSH](http://mosh.org)

### Bastion/jump host realization

* SSH Proxy user and group:

```
groupadd sshproxy
useradd -s /bin/bash -m zabbix -G sshproxy
su sshproxy --shell /bin/bash --command '
      [ -f '~/.ssh/id_rsa' ] || ssh-keygen \
      -f ~/.ssh/id_rsa -N "" -b 4096 \
      -C "ssh proxy port forwarding user" 
    touch  ~/.ssh/authorized_keys
	mkdir ~/.ssh/sockets
    chmod 0600 ~/.ssh/authorized_keys
'
```

* on jumphost server, adapt `/etc/ssh/sshd_config`:

```
...
DenyGroups All
AllowGroups ssh sftp sshproxy
...

Match group sshproxy
    AllowAgentForwarding no             # prohibited, use ProxyCommand instead of bastion's ssh client 
    AllowTcpForwarding local            # use for normal tcp tunnels to backend servers
    AllowStreamLocalForwarding no       # use for forwarding network sockets from backend servers
    ForceCommand echo 'This account can be used for forwarding, only'
    GatewayPorts no                     # or clientspecified
    PasswordAuthentication no           # keys only
    PermitOpen backend.example.net:22, 172.17.19.18:22
    PermitTTY no
    PermitTunnel no
    PermitUserRC no
    PubkeyAuthentication yes            # keys only
    X11Forwarding no
```

* TODO:
    * restrict public access to user/group sshproxy
    * restrict access for ssh and sftp to local networks
    * bastion host in dmz
    * allow public login to management server behind bastion host. Allow login to bastion host from this management server (only) 
    * Emergency access: Knock daemon, login via password then

### Client connections

Login to backend servers:

```
ssh -o ProxyCommand="ssh -W %h:%p -p 22222 sshproxy@gate.example.net" backend_user@backend.example.net
```


AutoSSH connections (ignoring `~/.ssh/config` settings, e.g. "controlmaster"):

```
autossh -NnT -M 0 -F /dev/null \
-o ExitOnForwardFailure=yes \
-o ServerAliveInterval=60 \
-o ServerAliveCountMax=3 \
-o ProxyCommand='ssh -W %h:%p -p 22222 backend_user@backend.example.net' \
sshproxy@gate.example.net
```


For easy connecting via jump host in SSH connections for e.g. git access: edit `~/.ssh/config`:

```
Host backend.example.net
    Hostname backend.example.net
    User backend_user
    ProxyCommand ssh -W %h:%p -p 22222 sshproxy@gate.example.net
```

 