# Ubuntu server setup

Zur Installation von Ubuntu Servern als HyperV Gastsystem oder auf x64-kompatibler Hardware wird eine ISO Datei verwendet, welche direkt in HyperV Gastsystemen eingebunden oder auf einen USB Stick kopiert werden kann.

Diese ISO Datei wird im folgenden als "Installer LiveCD" bezeichnet. Für das Ubuntu System, auf welchem die Installer LiveCD erstellt wird, wird der Name "LiveCD Builder" verwendet.



## Erstellung der Installer LiveCD

Die Installer LiveCD wird auf dem LiveCD Builder erstellt.

### Einrichtung des LiveCD Builder Systems

Beim "LiveCD Builder" handelt es sich um ein fest installiertes Standard Ubuntu Desktop System, auf welchem Skripte zur Erstellung einer Installer LiveCD liegen. Diese werden in einem GIT Repository verwaltet - das LiveCD Builder System ist also austauschbar.

Fertiggestellte ISO Dateien werden über ein Samba-Share bereitgestellt.



### Erstellung der Installer LiveCD

Zur Erstellung der Installer LiveCD muss das LiveCD Builder System unbedingt im UEFI Modus starten (HyperV Guest Options > Security > Secure Boot > "Microsoft UEFI").



wichtig: unattended upgrades, secure sysctl, swappiness, kernel options, fstab, network, localepurge

preseed file
https://sfxpt.wordpress.com/2013/06/09/get-the-debianubuntu-ready-and-customized-the-way-you-like-in-10-minutes/

Preseed UEFI System
https://debianforum.de/forum/viewtopic.php?f=12&t=162007
You'll need as a prerequisite a preseed file. Use debconf-get-selections to generate this. Start with the output of that command and edit as necessary.

Unattanedet updates:
https://info.gwdg.de/docs/doku.php?id=de:services:server_services:preseeding:start

RAM-Komprimierung mit zram5)
kein Swap auf physischen Blockdevices
IO-Scheduler per Kernel-Parameter auf noop gestellt 6)

HyperV VM: automatisch erkannt, erfordert sda und sdb Laufwerke
x64: automatisch erkannt, erfordert sda Laufwerk (/srv wir hier mit drauf gepackt)




# ---------------------
Die Erstellung der InstallCD erfolgt mit dem Tool [Cubic](https://askubuntu.com/questions/741753/how-to-use-cubic-to-create-a-custom-ubuntu-live-cd-image). Für die Benutzung dieses Tools wird ein
Ubuntu Desktop System (ISOCreator) eingerichtet, welches für die permanente Benutzung eingerichtet wird.

Die Skripte für das tatsächliche Rollout des Ubuntu Systems werden auf dem ISOCreator System per GIT Versionskontrolle gepflegt.

Jedes Update der Rollout-Skripte erfordert die Erstellung einer neuen InstallCD. Die Benutzung von GIT auf der InstallCD hat sich als unnötig komplex in der Anwendung erwiesen.


### Einrichtung des ISO Systems



### Update und Erstellung des "Ubuntu Installer CD"


### Benutzung der InstallCD



### Update

1. Download Ubuntu LTS Desktop von der [Ubuntu Seite](http://releases.ubuntu.com/18.04/ubuntu-18.04-desktop-amd64.iso)
2. Create HyperV VM, 50GB HD, 4GB Ram, Generation 2, Secure Boot = UEFI
3. Boot from ISO above, when finished:
    * Open Terminal
    * Check internet connection: `ping www.heise.de`
    * Enable multiverse repository (Software & Updates), install software:
    ```sh
    sudo apt-add-repository ppa:cubic-wizard/release
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 6494C6D6997C215E
    sudo apt update
    sudo apt-get dist-upgrade
    sudo apt install cubic isolinux --yes
    ```
    * Create Disk: "Disk Manager", 54Gb Hard Disk, Format Name "ISO", NTFS, mount via "play" button
    * Start "Cubic", Project directory `/media/ubuntu/ISO`


1. Download Ubuntu LTS Desktop von der [Ubuntu Seite](http://releases.ubuntu.com/18.04/ubuntu-18.04-desktop-amd64.iso)
2. Create HyperV VM, 50GB HD, 4GB Ram, Generation 2, Secure Boot = UEFI
3. Boot from ISO above, when finished:
    * Start "Install Ubuntu"
    * English Language, German Keyboard
    * Minimal Installation, Yes, download Updates
    * Erase Disk and Install Ubuntu, TimeZone Berlin
    * Machine Name: "iso-creator"
    * "Your Name: "administrator", passwd Yaq, Login automatically
    * "Restart Now" + Enter
4. Freshly booted system:
    * install ssh server
    ```sh
    sudo su -  # yaq
    apt install --yes openssh-server
    ssh-keygen -C root@iso-creator -b 4096 -N ''
    touch ~/.ssh/authorized_keys
    chmod 0600 ~/.ssh/authorized_keys
    cat ~/.ssh/id_rsa.pub
    ip a # note IP
    ```
    * connect to `root@<server-ip>`
    * continue with file sharing and tool setup
    ```sh
    apt install --yes net-tools samba vim-nox git haveged
    install --mode 0777 -d /srv/samba
    echo '[shared]' >> /etc/samba/smb.conf
    ech'  guest ok = yes' >> /etc/samba/smb.conf
    echo '  path=/srv/samba' >> /etc/samba/smb.conf
    echo '  public=yes' >> /etc/samba/smb.conf
    echo '  writeable=yes' >> /etc/samba/smb.conf
    service smbd restart
    ```
    * Download and install the [ubuntu server network installer image](http://cdimage.ubuntu.com/netboot/18.04)
    ```sh
    cd /srv/samba
    wget http://releases.ubuntu.com/18.04/ubuntu-18.04-live-server-amd64.iso
    ```


    * Download and install systemback software from sourceforge repository]()
    ```sh
    tar -xf System*
    cd System*
    sudo install.sh # Option 4, retry 2x
    ```






    * install `systemback` iso creator and cubic fresh-iso-creator
    ```sh
    sudo apt-add-repository ppa:cubic-wizard/release
    #sudo apt-add-repository ppa:nemh/systemback
    sudo apt update
    sudo apt install --yes cubic isolinux # systemback
    ```

    * HyperV: Ubuntu ISO image nach `\\<server-ip>\shared` kopieren
    * Start cubic, Projekt Directory `/srv/samba`




    * from hyperv, the exported iso is accessible from `\\<server-ip>\shared`




## Inbetriebnahme

### Bau der Maschine auf testv22 hyperv1

```
Import-Module D:\Install\vm-setup
New-LinuxVM -vswitch Ethernet -Layout Standard -Name mailrelay.systems.fellowtech.com
```

VM starten, dann

```
cd /srv/bootstrap
./start-bash
git remote set-url origin ssh://git.fellowtech.de:22222/os-ubuntu16/bootstrap
git pull
./start-bash
vim bootstrap.conf # Anpassung NETWORK section
bootstrap --vm -v
```

Auf dem HyperV die VM herunterfahren und exportieren

### Import und Start der Maschine auf dem Ziel-HyperV
* den VM-Export von der `\\10.10.4.11\d$` Freigabe des hyperv1.testv22 auf `\\hyperv2.secure.fellowtech.com\d$` Freigabe verschieben
* die VM auf dem hyperv2.secure als "Copy" importieren (neue UUID)
* Anpassen: Netzwerkkarte und VLAN
* VM starten - beim ersten Boot läuft in der Konsole kein Text durch und die Maschine ist dann plötzlich "da"
* SSH Login vom RDS auf die Server Adresse funktioniert
    * wenn nicht:
        * auf der hyper-V Konsole als admin/yaq anmelden, {{sudo su -}} und debuggen, Beispiel für `/etc/network/interfaces`:
```
auto  eth0
iface eth0 inet static
    address   172.17.16.18
    netmask   255.255.255.248
    gateway   172.17.16.17
    dns-nameservers 172.17.16.2
    dns-search systems.fellowtech.com
    dns-domain systems.fellowtech.com
```
* passwd admin # BFG
* edit /etc/systemd/timesyncd.conf 172.17.16.2
* echo 'Acquire::http { Proxy "http://172.17.16.10:3142"; };' > /etc/apt/apt.conf.d/02proxy

### Basis-Konfiguration der Maschine
Nach dem SSH Login: das Passwort für den `admin`Benutzer setzen:
```
passwd admin # BFG
```
Aptitude für Betrieb im Systems-Netzwerk konfigurieren
```
echo 'Acquire::http { Proxy "http://172.17.16.10:3142"; };' > /etc/apt/apt.conf.d/02proxy
```
Den Ansible ft Schlüssel auf dem ansible Server ausgeben
```
cat /srv/ansible/private/ssh/remote/ft/id_rsa.pub
```

 bzw. so im neuen "mailrelay" Server einfügen:
```
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDRHZf0u6mlc1VpF0ddZjTtobG7n77rHvNPtz2B6BMhBjRTHaUT/ZFFcrgBE8SlyDqFPEnH6mZ+57LUdNQ7GTIgZU3BkVHMFd/xyjgb7mOMlQG6gLBumUqzbSGX5R3LQS95kIelKv1T+ZqFMCvg6XouGibbYA/jDxvixuA5xjw8tXF2Ufuuo1SRgqKpxPfZs5zxdpXSgsu6AwzZHwMVhbq5En0e2Yx6ZSpHZ3uqdpFHluusKHQZ9KviH7ITEEdmffQxp/OQtYTP++YSrroICwbDhaf4y2vYZ07ii4OOMBkn+zltcFMASr+hsazl9ArsAczjuRaL41QIFUJp/dDHLIOFsh53M5JpvR0EN9yk9/a2hvENPXOhmD19w389Ya65SL0PTbjhQsBX8AYtcn7Y7G2h6VEylx7+LPNopi/6vpQHzXyMK7PwFa3Q5a7MyUB5TwhUVjzx5r5jPCB51XOGqGqOGOdQVP5zTiuQ+owRXnkO4fSwfpmVkwR81JwnML0BNFmDOiD7GDPciLnjvau/R45a0PlZ6TaBO1mujo6ZdQB6LbgNFz6JFCKSnRHRWSid/WxieFFLgl+ekYdrFx3Jv6BzIIkuVQ5PMwzQ+rQ4CE3B9PRU6gbtgIY9QnRJa4GVyBo8LbpG4hmRaWfsNf7t77gUrCnD0FVeBaLXt0QWV3RxCQ== Ansible Automation fellowtech GmbH for ft' >> /root/.ssh/authorized_keys
```

Damit kann sich der Ansible Server auf den Server verbinden ... alles weitere von diesem Server:

* Laden des host keys:
```
ssh mailrelay.systems.fellowtech.com -i /srv/ansible/private/ssh/remote/ft/id_rsa
# yes
exit
```
* Server `systems-mailrelay` im inventory `/srv/ansible/inventory/inventory.yml` eintragen:
    * Gruppen:
        * `backup-nas` auskommentiert weil kein SSH -Zugriff auf den backup1.secure möglich ist und das Backup-Skript für den pull der Datensicherung noch nicht fertig ist
        * `linux-virtual`
        * `ft-rz`
    * Host config:
```
"systems-mailrelay":
  ansible_host : mailrelay.systems.fellowtech.com
  BackupTargetDir: '/srv/serverbackup/linux/mailrelay'
  BackupStartHour: 21
  BackupStartMinute: 5
```
* Server per ansible einrichten
```
ansible-playbook /srv/ansible/inventory/linux
ansible-playbook /srv/ansible/inventory/monitoring
ansible-playbook /srv/ansible/inventory/backup
```



# Installation eines Ubuntu-Systems

## Einleitung
Dies ist die Anleitung für die Installation von Ubuntu 16.04 LTS Systemen als VM auf einem HyperV oder auf x64 Hardware.

## Vorbereitung

### Konfiguration
Für die Installation sollte der Server mit einem "Internet-fähigen" DHCP-Netzwerk verbunden werden. Das muss nicht das Ziel-Netzwerk (zum Beispiel Kundennetzwerk im Rollout-Prozess) sein.

Die Netzwerk-Verbindung wird während der Einrichtung konfiguriert und ist erst nach einem Neustart aktiv.

Benötigt werden:
* IP, Gateway, Netzmaske (lang)
* DNS Domain, Hostname
* NTP Server IP, DNS Server IP
* Virtual Switch, an welchen die VM angebunden werden soll

### HyperV VM
Der erste Schritt ist, aus den verfügbaren Profilen für das Server-Layout:

* **standard**: 2 CPU Cores, RAM 1GB, 5G /root, 15G /srv, 512MB swap
* **tiny**: 1 CPU Core, 512MB RAM, 3G /root, 1G /srv, 256M swap
* **worker**: 4 CPU Cores, RAM 4G, 5G /root, 35G /srv, 2G swap
* **beast**: 8 CPU Cores, Ram 8G, 5G /root, 35+ G /srv, 4G swap

eine Variante aussuchen. Alternativ können beim Aufruf des `New-LinuxVM` CMDlets (s.u.) einzelne Parameter angegeben werden, siehe `help New-LinuxVM`

Das aktuelle Installations-Image aus `\\jarvis\repository\server-os-ubuntu16\iso` muß auf dem HyperV unter `D:\Install` verfügbar sein.

Dann wird die virtuelle Maschine mit folgendem Befehl angelegt:
```
Import-Module \\jarvis\repository\server-hyperv\vm-setup
$Parameters = @{
    Layout = 'worker'
    vSwitch = 'Slot6 Port1'     # Virtual Switch, an welchen die VM angebunden werden soll
    Name = 'backup1'        # Name der VM
    Description = 'backup control server on hyperv1'
    Data_Size = 5GB
}
New-LinuxVM @Parameters -verbose
```

### x64 Hardware
Da nach derzeitigem Stand die Live-CD auf x64 Hardware nicht startet (Grub Fehler) und eine Entscheidung, ob wir weiterhin diese Hardware-Server verwenden nicht gefallen ist wird die Option "x64 Hardware" nicht weiter verfolgt.


## Installation
Während der Konfiguration der VM wird eine DVD in der VM "eingelegt", welche nach dem Start bootet.
Nach dem Boot der rescue-live-CD (Option "Ubuntu Installer ..." auswählen) wird direkt eine Shell gestartet. Auf die angezeigte IP kann eine Putty/SSH Verbindung gestartet werden, mit der sich im Folgenden bequemer arbeiten läßt.

Die Einrichtung des Betriebssystems wird über die Konfigurationsdatei `/srv/bootstrap/bootstrap.conf` gesteuert, dort folgende Parameter anpassen:
```
MACHINE_NAME="backup1"
DOMAIN_NAME="tmrelo.local"
IP="10.1.0.151"
NM="255.255.252.0"
GW="10.1.0.1"
DNS="10.1.0.21"
NTP="10.1.0.21"
```

### HyperV VM

* Installation starten:
```
bootstrap --vm -v
reboot
```

* Derzeit kann es vorkommen, das die HyperV-Konsole ("RDS"-Verbindung zur VM) schwarz bleibt. Hier hat bis jetzt immer geholfen, die VM herunterzufahren und anschließend neu zu starten.
* Ansible über das installierte System laufen lassen
auf dem Ansible Server den public SSH key für den Kunden ausgeben:
```
cat /srv/ansible/private/ssh/remote/<kunde>/id_rsa.pub
```
Nach dem Neustart in das gestartete System einloggen (admin/Ya) und den Ansible SSH key eintragen:
edit `/root/.ssh/authorized_keys`

Nun muss einmalig die Verbindung von Ansible zum neuen Linux-Server gestartet werden, um die "known_hosts" List auf dem Ansible Server zu aktualisieren:
```
ssh <Server-Adresse> -i /srv/ansible/private/ssh/remote/<kunde>/id_rsa
```
Die Server-Adresse ist die welche in der `inventory.yml` als `ansible_host` Parameter hinterlegt worden ist.

Dann auf dem Ansible Server folgende Befehle laufen lassen:
```
ansible-playbook /srv/ansible/inventory/linux.yml
ansible-playbook /srv/ansible/inventory/monitoring.yml
ansible-playbook /srv/ansible/inventory/domain.yml
```

Für weitere Dienste die entsprechenden yml Dateien unter `/srv/ansible/inventory` anziehen.

### x64 Hardware
```
bootstrap --x64 -v
reboot
```

# Hintergründe

## Offen
* OS Installation per KVP


## Warum keine Installation per Ubuntu Live-CD?
Ubuntu läßt sich vornehmlich aus einem offiziellen LiveCD-Image erstellen, das erstellte System hat aber folgende Nachteile:
* langsamer Start (Suche nach BTRFS Partitionen)
* elende Installiererei mit Rückfragen im 10 Minuten Takt
* admin Benutzer darf nicht verwendet werden obwohl es den im fertig installierten System überhaupt nicht gibt (WTF)
* doofes Partitionsschema erlaubt keine einfache Vergrößerung der Datenpartition im Nachheinein

## Manuelle Installationsschritte
Folgender Ablauf entspricht im Wesentlichen der automatischen Einrichtung per [Skript](\\jarvis)
