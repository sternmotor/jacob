CoreOS Setup via ignition file
==============================


TODO:
* build deployment script out of this
    * simple python subprocess.call  - make comments easier to write
    * define constants for complete config
    * define complete config as yaml text in list of """ """  (with space for comment blocks)
    * get systemd, locksmith and storage files/directories out of yaml 
    * convert rest to python data object
    * run transpiler over systemd, locksmith and storage via tmp file, read into python object
    * export whole circus as ignition.json yml




* see [Systemd and containers](https://container-solutions.com/running-docker-containers-with-systemd)

## Configure CoreOS setup

Features
* configure secure sshd on port 30000, allow only user `core` and `root`
* extend root partition to 50GiB (for docker images) and create compressed btrfs on partition 10 (rest of /dev/sda, mountpoint `/srv`), trigger mounting   of `/srv` at boot
* set user `core` password and ssh key files
* set `/etc/hosts`, `/etc/hostname`, `/etc/zoneinfo` 
* configure bash and vim
* update strategy: reboot thuesday between 4 and 5 pm

CoreOS is built around systemd and Docker.

## Prepare ignition

See 
* [ignition file specification](https://coreos.com/ignition/docs/latest/configuration-v2_3.html)
* [locksmith specification](https://github.com/coreos/locksmith#reboot-windows)
* [proper way to run docker-compose as container](https://stackoverflow.com/questions/29086918/docker-compose-to-coreos)
* [switch from timesyncd to ntpd example](https://coreos.com/os/docs/latest/configuring-date-and-timezone.html)


### Retrieve secure SSHD config:

* find secure set of ciphers by removing insecure ciphers from available bunch (on coreos server)
```
sshd -T | grep ciphers | sed -e "s/\(3des-cbc\|aes128-cbc\|aes192-cbc\|aes256-cbc\|arcfour\|arcfour128\|arcfour256\|blowfish-cbc\|cast128-cbc\|rijndael-cbc@lysator.liu.se\)\,\?//g"
```
* compare default settings as of 
```
sshd -T
```
to settings in ssh config file

### Prepare initial config 
Since "ct" does not support config version "2.3.0" as of now, json config in this section (version 2.3.0) has to be combined manually with the converted next part (version 2.2.0), afterwards. Instert into "storage: files:" 
This is the initial config without config files content

```
cat << 'INITIAL_END' > initial.json
{
    "ignition": {
        "config": {},
        "timeouts": {},
        "version": "2.3.0"
    },
    "networkd": {},
    "passwd": {
        "users": [{
            "name": "core",
            "passwordHash" : "$6$4iEnQPxR$jIJimNWFqUFetH0EH106QAgJmG93CJizBsgEgEQIh/S5NEgREi4VV9ej0x865xdvNnzu6w5esNRFx1YHMRZlK0",
            "sshAuthorizedKeys": [
                "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCWYeIv59k51zweaf/MrBomaBD42e4c283MhX+LtwEc+rrZiu1iEyACKoXicNYpbeeREw8guXsXBxmI6ISQT54zGIwJ8TcctPpvBXRyYVkQdF/qetyHQl/U48TyZQ406gbpA7zbdXhMNz3LYr76Wyw3H9nN0g0RZVMMc23SDgYXdofzrojQhUMqHHnPvic/0yoepyC8q6PuEdvdW5sL0oWjhor62kOJ64Zf8PvFJFUT14iDDpmSuFW5igM/WW//HU2wH4PqBQYPlmz7QCvskjTnV3hqeuvSnaL2vtb7o8Sbl8LQSVJHPkBpnCDqPOD1KlkIuC153yOGmDTAKZ6t7xaXxOrcfbE+9KtwoEn5sx6fMS1mi0E3CQTeADSVinmVpJLKGQBu0smddGkVuabCTC597tiC3+iDz0NUr/HWJtjs4O+3JRwO55gTqF/TlqNp47jcydBWESVFhyUTmD8LDrQym6TYnaXeQGuWxif3Ijdub9633nriZpPYrDWSpdwXy1+DUPo+wY8E8DD2dbN/KS7dRT8RCB6lqTAJW1Akbbf/WcWf0DWpcu/zADLNwb01wAWCP85FzxXFseXD6NEZnVuJMR1Oz4wE8eBjk79EvtdLOZHOdz5oYkUJERfphe4eK3Xzde8wZe4FTy2qOiSGTYsgHf6jbA25jAGP5Fevsx8Khw== gunnar@macbook",
                "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCeWnz1i13zfR+xYGU27bOMmo+Hr5lOdJGVz75B9WHdWsZ9zsSc/Xvpaz2+FMZW8Mq1nOM9zl4uOFkl43erTVR7arBFfyF280oaulxo8hynBdzWfG1zw3OU6L0HnMk5FcgiKMSUpkfDurRs6FjD6rtwDNi+C4pXnwbsGyW8kr55tyqf4qxbhbGAD/jzbt5OXl35BqtwpdpFKenLLOtQgsotgYOIu9Ephf+jUI9zL7ZjWZvYQKBlrIcx5o4Di1N8HPBw1MQhEqZr+TxJdsG/rZFN/gMVrV/4Svhf6b0sGEcE/wVWPTsYbL7uO33BZNbB7hIbFOOoml3j3ALmtzZWxHORpVulbaivxbBLUfhhZxdUlqgBL0oEmSVLESwVvxfykCDd+amjz7w5I/L79eB8IKwO2qVWO1pD9eAqOLXeZvhee4o7sCQ4otm3p+DXsJ0AZiACSp817etSkdrTB6g3q8crRQ9wt/0AKG2XtRVSk5Y0adkL++n7araXx9e/A6aA3taj/Hh8maYCSEHwjhUpcsYKOks4hBm2WJpwbzmiXy43Y8f7yFNIJAA3GtVz1bpSEi6+vDxrL7VADd3/jJc0cSAQ1YwlgN1YcqQUiRXlmC0xGjozt82XrYznZD7Y3MQLbyxf7XMPLdI56MSlJF0T4K2Rdv7nADSo5e6sb/JNaWGBRQ== g.mann@quince",
                "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCrYStE0kH2pN/Ks8it9yW+YwDlOVaXEJ0c9xF9QxE9VVimbDRgoPuDuYmREPGuVLRAwnT4L8jzn3XcJYB0l1u6gt/Sl76BDCmu4IVMM+OPrbAMAYp/zrLPNPxoCJqaUtEOkP8hqG4JRHHaJZ71EHW55rdt4m/uoOPgWPkYkO4p+HHZwfySyhDN8SHAZFwQ8H19ktvW5aYgiO8U0k1skGoL3dh5nvpkR4rHE02ozzm6GRVB3XTK9JMbQZxeuU7VEFwVh64s0742AiWMK3H8WfidmRiuYj/x07phz08R6TAv83KMxP2w4Pb0mav6s1LELO1GLZsKeFdhMmHGzc4MsC/h root@sternmotor2"
            ]
        }]
    },
    "storage": {
        "links": [{
            "filesystem": "root",
            "path": "/etc/localtime",
            "target": "/usr/share/zoneinfo/Europe/Berlin",
            "overwrite": true
        }],
        "disks": [{
            "device": "/dev/sda",
            "partitions": [
                {
                    "label": "ROOT",
                    "number": 9,
                    "sizeMiB": 49152,
                    "startMiB": 0,
                    "typeGuid": "4F68BCE3-E8CD-4DB1-96E7-FBCAF984B709",
                    "wipePartitionEntry": true
                },
                {
                    "label": "DATA",
                    "number": 10,
                    "sizeMiB": 0,
                    "startMiB": 0,
                    "typeGuid": "3B8F8425-20E0-4F3B-907F-1A25A76F98E8"
                }
            ]
        }],
        "filesystems": [
            {
                "mount": {
                    "label": "DATA",
                    "device": "/dev/disk/by-partlabel/DATA",
                    "format": "btrfs",
                    "wipeFilesystem": false
                }
            }
        ]
    }
}
INITIAL_END
```


### Prepare config file json for config files

Download and prepare transpiler (linux rescue system), generate yaml for inserting into ignition file

Generate json for config files - let "ct" executable take care of escaping white space etc. 

This part of ignition handled here in yaml format (to circumvent html-escaping config files) and needs to be "transpiled" to json format afterwards.


```
wget https://github.com/coreos/container-linux-config-transpiler/releases/download/v0.9.0/ct-v0.9.0-x86_64-unknown-linux-gnu -O ct
chmod a+rx ct
./ct -pretty << EOF > files.json
locksmith:
  reboot_strategy: reboot
  window_start: Thu 04:00
  window_length: 1h


storage:
  directories:
  - filesystem: root
    path: "/etc/bash/bashrc.d"
    mode: 438
  files:
  - filesystem: root
    path: "/etc/hostname"
    mode: 420
    contents:
      inline: |-
        elvis

  - filesystem: root
    path: "/etc/hosts"
    mode: 420
    contents:
      inline: |-
        127.0.0.1 localhost.localdomain localhost
        127.0.0.1 elvis.sternmotor.net elvis
        ::1 localhost.localdomain localhost
        ::1 elvis.sternmotor.net elvis

  - filesystem: root
    path: "/etc/ssh/sshd_config"
    mode: 384
    contents:
      inline: |-
        # Network
        Port 30000
        Compression delayed
        X11Forwarding no
        TCPKeepAlive yes
        ClientAliveInterval 60
        ClientAliveCountMax 5
        UseDNS no

        # Authentification
        LoginGraceTime 60
        MaxAuthTries 3
        ChallengeResponseAuthentication no
        DenyUsers All
        AllowUsers core root
        PermitRootLogin without-password
        PasswordAuthentication no

        # System
        Protocol 2
        UsePAM yes
        StrictModes yes
        AcceptEnv TERM COLORFGBG
        Ciphers chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
        PrintMotd yes

  - filesystem: root
    path: "/etc/vim/vimrc.local"
    mode: 420
    contents:
      inline: |-
        " editing
        syntax on 
        set hlsearch
        set nosmartindent
        set nocindent
        set autoindent  
        set expandtab    
        set shiftwidth=4 
        set tabstop=4    
        set smartcase
        set virtualedit=block 

        " file handling
        set encoding=utf-8
        set noautoread 
        set noautowrite
        autocmd BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$") | exe "normal g'\"" | endif
        autocmd BufNewFile,BufRead,InsertEnter,InsertLeave * filetype detect
        set modeline
        set modelines=5

        " user interface
        set laststatus=2
        set statusline=[%n]\ %F\ %M%R%H\ \ %y\ \ %p%%%=Line:%l/%L\ \ Column:%c
        set mouse=	

        " backup, history
        set directory=~/.vim
        if !isdirectory(&directory)
            call mkdir(&directory, "p")
        endif
        set undodir=~/.vim
        set backupdir=~/.vim
        set viewdir=~/.vim
        let mapleader=','  
        let g:mapleader=','
        set undofile   
        set undolevels=500 
        set history=500   
        set undoreload=10000    
        set backup



  - filesystem: root
    path: "/etc/bash/bashrc"
    mode: 420
    append: true
    contents:
      inline: |-
        bind '"\e[5~":history-search-backward'   
        bind '"\e[6~":history-search-forward'  
        set +H 
        set show-all-if-ambiguous on    
        shopt -s checkhash
        shopt -s checkwinsize
        shopt -s histappend   
        alias ..='cd ..'
        alias less='less -QR'
        alias ll='ls -l --human-readable'

systemd:
  units:
    - name: srv.mount
      enable: true
      contents: |-
        [Unit]
        Before=local-fs.target
        [Mount]
        What=/dev/disk/by-label/DATA
        Where=/srv
        Type=btrfs
        Options=defaults,noatime,compress=zstd
        [Install]
        WantedBy=local-fs.target
FILES_END
```

### Combine json files

python - << PYTHON_END > config.ign
import json
data={}
with open('initial.json') as initial_file:
    data.update(json.load(initial_file))
with open('files.json') as files_file:
    new_data = json.load(files_file)
    data.update({
        'storage': new_data['storage'],
        'systemd': new_data['systemd'],
    })  
    
print(json.dumps(data, indent=4, sort_keys=True))
PYTHON_END

## Download and run coreos installer
```
wget https://raw.githubusercontent.com/coreos/init/master/bin/coreos-install
bash coreos-install -C stable -d /dev/sda -i config.ign
```

* bei der installation wird die config.ign nach /dev/sda6 kopiert. Beim boot von CoreOS wird diese Datei dann als `/usr/lib/ignition/user.ign` eingesetzt und verarbeitet und landet dann letzendlich unter
```
/usr/share/oem/config.ign
```

# Option: maintenance 

reset state partition `/dev/sda9` and trigger ignition run:
```
sudo umount /srv 
sudo rm -rf --one-file-system --no-preserve-root /
sudo touch /boot/coreos/first_boot
sudo reboot
```

# vim: set shiftwidth=4 tabstop=4 expandtab :
