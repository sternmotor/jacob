
Generate ssh key pair:

    ssh-keygen -a 100 -f ~/.ssh/id_ed25519 -N '' -t ed25519 -C $(whoami)@$(hostname -f)
