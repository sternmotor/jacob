# Linux user and permission handling

## Sudo

Create a user for installation to be used in Ansible and also grant root privileges to him
```
useradd ansible
passwd ansible
echo -e 'Defaults:ansible !requiretty\nansible ALL = (root) NOPASSWD:ALL' | tee /etc/sudoers.d/ansible
chmod 440 /etc/sudoers.d/ansible
```

## Passwords
Generate SHA512 password hash for `/etc/shadow`, install `mkpasswd` like `apt-get install whois`
```
Password="xxxxx"
Salt=$(pwgen 8 1)
mkpasswd -m sha-512 -S "$Salt" -s "$Password"
```



## Switch user, chroot operation

Run commands on other users behalf
```
for user in root admin; do
    echo "Re-creating key for \"$user\""
    sudo su --login $user --command "{
            cd ~/.ssh
            pwd
            echo $HOME
            echo "-----"
    } < /dev/null
    "
done
```

Pipe somethig to other user and operate on file as this user
```
echo $SSHD_KEY | chroot /mnt su --login $user --command "tee  ~/.ssh/authorized_keys >/dev/null"
```
