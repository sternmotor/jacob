# Putty <> OpenSSH

Linux: Convert Putty key to openssh key:

* putty key `example.pem` should look like
```
PuTTY-User-Key-File-2: ssh-rsa
Encryption: none
Comment: examplekey
Public-Lines: 6
AAAAB3NzaC1yc2EAAAABJQAAAQEAskxb4ZArgHn/bANHk3YuwMh/rLqXrXkfuGn3
...
mHmS26MPAUGOOGPGIDg6DM6uaOPuNOolAhkuGrR861ocp5zyCw==
Private-Lines: 14
AAABAG7VhTkwGwqss4hVENFJdwI3cfXAGRjOwLDn7Ln71kYO8Ni7s7jb2Gm42HZ2
...
os2vJBhBIUyfB33CSCh4WRHAaGB9OOsMaWKtMFE=
Private-MAC: 69608f4f75284152c85ab5eb42a8fb9d43xxx
```

* install putty ssh tool under linux
```
sudo yum install -y putty
sudo apt-get install putty-tools
```


* generate openssh public key
```
puttygen example.pem -L > id_rsa.pub
```

* generate openssh private key
```
puttygen example.pem -O private-openssh -o id_rsa
```

* generate ssh2 public key 
```
puttygen example.pem -p > id_rsa.pub.2
```

* extract putty private key (ppk) from `example.pem`
```
puttygen example.pem -O private -o example.ppk
```

* alternative: generate putty ssh key
```
puttygen -t rsa -b 4096 -C "example@host" -o example.pem
```

# run commands over ssh

Copy file, run via sudo. user is "ansible", password is "xxx", gs is list of host adresses
```
while read host; do  
    echo  $host
    sshpass -p 'xxx'  rsync -a setup_ssh.sh ansible@$host: 
    echo 'xxx' | sshpass -p 'xxx' ssh -tt ansible@$host sudo  ./setup_ssh.sh 
done < gs
```



