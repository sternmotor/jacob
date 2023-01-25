# SSH usage

## Authentification

Quickly allow ssh root loging

    sed -i 's|^PermitRootLogin.*|PermitRootLogin without-password|' /etc/ssh/sshd_config
    systemctl restart sshd


Generate ssh key pair:

    [ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -a 256 -N '' -f ~/.ssh/id_ed25519 \
    -C $(whoami)@$(hostname -f)_$(date +%Y-%m-%d)
    cat  ~/.ssh/id_ed25519.pub


Pull remote ssh host key

    TARGET=some-host.example.com
    grep -wq "$TARGET" ~/.ssh/known_hosts || ssh-keyscan $TARGET >> ~/.ssh/known_hosts


Hand over password from variable

    sshpass -p "$PASSWORD" ssh user@host


## sFTP

Run sftp server on port 22222, normal ssh on port 22, allow access for group "sftp" to sftp, only. Deny non-sftp members on sftp port (`/etc/ssh/sshd_config`):

    Port 22222
    Protocol 2
    ...
    SubSystem sftp internal-sftp

    # exclude sftp groups from ssh access
    match group sftp localport 22
        ForceCommand /bin/echo "This account is restricted to sFTP access"

    # exclude ssh logins from sftp
    match group *,!sftp localport 22222
        ForceCommand /bin/echo "This connection is reserved for sFTP access"

    # allow sftp for sftp groups
    match group sftp localport 22222
        AllowTcpForwarding no
        Banner none
        ChrootDirectory /var/lib/sftp/%u
        ForceCommand internal-sftp
        PermitRootLogin no
        X11Forwarding no

Prepare users and chroot dirs

    groupadd sftp
    # add users as members of group sftp 
    install -o root -g root -m 0750 -d /var/lib/sftp
    install -o root -g root -m 0755 -d /var/lib/sftp/user1
    install -o root -g root -m 0755 -d /var/lib/sftp/user2

Prepare bind mounts of local source directories into chroot

    mkdir /var/lib/sftp/user1/dir1
    mkdir /var/lib/sftp/user1/dir2
    mkdir /var/lib/sftp/user2/dir1

Prepare fstab entries

    /srv/dir1 /var/lib/sftp/user1/dir1 none bind 0 0
    /srv/dir1 /var/lib/sftp/user2/dir1 none bind 0 0
    /srv/dir2 /var/lib/sftp/user1/dir2 none bind 0 0

Enbale mountts

    mount -a
    

Now login as user "user1" or "users" via sFTP client on port 22222, this should allow access to "dir1" and "dir2" and nothing else.


## Bastion host
    
Bastion host config

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
        PermitOpen server1:port1, server2:port2
        PermitTTY no    
        PermitTunnel no    
        PermitUserRC no    
        PubkeyAuthentication yes 
        X11Forwarding no

Bastion host usage

    ssh -o ProxyCommand="ssh -W %h:%p -p 22 bastion.example.com" server1 


## Tunneling

Configure transparent jumps over multiple hosts in `~/.ssh/config` where only host "jump" is directly reachable. This works transparently with git and scp. As example, remote (host "target") Port 443 is forwarded to local machine port 4443.

    Host target
      ProxyCommand ssh deepest_jump -W %h:%p
      LocalForward 4443 localhost:443
      User username3

    Host deepest_jump
      User username2
      ProxyCommand ssh deep_jump -W %h:%p

    Host deep_jump
      User username1
      ProxyCommand ssh jump -W %h:%p

    Host jump
      Port 30000

Make remote ssh server accessible on localhost via relay server

    ssh user@relay-server.com -L 2222:remote-server.com:22
    autossh -NnT -M 0 user@relay-server.com -L 2222:remote-server.com:22


Socks proxy (SOCKS4/5 proxy at localhost:3333). Check
whether it's working by surfing e.g. to checkip.dyndns.org)

    ssh -ND 3333 username@external.machine

## Persistent connections

Persistent, fast reusable connections on command line

    mkdir ~/.ssh
    ssh -o ControlMaster=auto -o ControlPersist=10m -o ControlPath=~/.ssh/sockets-%r@%h:%p <COMMAND>


Persistent, fast reusable connections via `~/.ssh/config`:

    Host *
        ControlMaster auto
        ControlPath ~/.ssh/sockets-%r@%h-%p
        ControlPersist 10m
