
Quickly allow ssh root loging

    sed -i 's|^PermitRootLogin.*|PermitRootLogin without-password|' /etc/ssh/sshd_config
    systemctl restart sshd


Generate ssh key pair:

    [ -f ~/.ssh/id_ed25519 ] || ssh-keygen -t ed25519 -N '' -f ~/.ssh/id_ed25519 -C $(whoami)@$(hostname -f)
    cat  ~/.ssh/id_ed25519.pub


Pull remote ssh host key

    TARGET=some-host.example.com
    grep -wq "$TARGET" ~/.ssh/known_hosts || ssh-keyscan $TARGET >> ~/.ssh/known_hosts

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

traffic tunnel, socks proxy (set the SOCKS4/5 proxy to localhost:3333. Check
whether it's working by surfing e.g. to checkip.dyndns.org)

    ssh -ND 3333 username@external.machine

