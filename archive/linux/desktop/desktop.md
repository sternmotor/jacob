See [Desktop navigation concept](../desktop/navigation.md)

# Xorg in General

monospace fonts:
DejaVu Sans Mono Book - good at size 9pt ,only. Gets badly wide at 10+ pt.


Set screen resolution
```
OUTPUT=$(xrandr | grep -w connected | awk '{print $1}' )
xrandr --output $OUTPUT --mode 1280x1024 --rate 60
```

* [Fluxbox themes](https://www.xfce-look.org/p/1017066/#files-panel)
* LXDE: Linux Mint mit [Squared Theme LMDE](https://www.box-look.org/p/1017066/), see desktop folder
    * WM: Fluxbox, fluxter as pager
    * GTK-Theme: Xfce-dusk
    * Icon Theme: Clarity
    * Font: Neutra Text TF Medium 10.7
    * Config: see [Squared Theme](desktop/146219-Squared-LMDE.tar)
    * File manager: Thunar or rox-filer
    * Thunar Leafpad, Chrome, Consola, xfrun, Audacious, SmPlayer, Conky, TINT2, ginn for apple trackpad
    * lightweight `cairo-compmgr` for window decorations
    * Minetime Calendar, Dark Theme
    * Atom Editor with VIM
    * Mailspring, Phanteon Mail or Geary
    * Browser: Slimjet or Vivaldi
    * [RDS Server](https://wiki.alpinelinux.org/wiki/Remote_Desktop_Server)
* [RXVT Plugins](https://github.com/majutsushi/urxvt-font-size)
* Fluxbox keyboard setup (macrocmd, togglecmd): [here](http://fluxbox-wiki.org/category/howtos/en/Keyboard_shortcuts.html)

* Fluxbox
    * Window groups
    * dmenu, xscreensaver
* dockable apps windowmaker (maybe not at all!)
    * wmbiff mailbox checker
    * minidock /4x application launcher)
    * wmcalc
    * wmnet
    * wmapm, wmthrottle # when on batteries
    * wmappkill
    * wmcalclock
    * wmcalendar


# Alpine Linux

Alpine is designed to run from ram with copying config to persistent storage. Secure, small.

* USB: alpine ram system, store important config on seafile
    * boot into facade desktop, start script for unencrypting real home (to ram) and password dialog, reload fluxbox
    * energy-saving: acpid, cpufreqd, xrandr LCD refresh rate when on battery
* replace busybox tools with [real software](https://wiki.alpinelinux.org/wiki/How_to_get_regular_stuff_working)
* apps: see above
* keyboard and mouse support: imwheel, 

# Antix USB Stick

Alternative: Slax mit Fluxbox Desktop

Ziel:

* super schlanke Admin-Tool und Arbeits/Entwicklungsumgebung auf der Basis von Linux, Fluxbox, ROX filer
* Wichtige Software:
	* Chromium Browser
	* Epiphany
* Software geht immer wieder kaputt, deswegen sollen alle GUI Anwendungen in Docker laufen - austauschbar. Fluxbox selber wirds ja wohl stabil laufen und kommt auf das Root System
* Boot von USB-Stick, ToRam und home Verzeichnis ebenfalls im Ram bis auf Dokumente und Bilder, Möglichkeit Einstellungen persistent zu setzen
* dot-Dateien in GIT
* Software-Auswahl von elementary OS übernehmen - kleine feine Tools



## Installation antix-core

Antix selber ist ganz schön überladen mit allem Krempel, deswegen soll das System vom core aus aufgebaut werden, Anwendungen s.o. und sonst nur SSH, Fluxbox, Docker

### Test: Installation auf Laptop-HD ohne Docker

* Download antix-core von [SourceForge](https://sourceforge.net/projects/antix-linux/files/Final/antiX-17/)
* USB Stick einrichten unter MacOS:
```
sudo su -
hdiutil convert -format UDRW -o image /Volumes/Daten/Users/Gunnar/Downloads/antix-17_x64-core.iso
diskutil list # USB Stick suchen, hier: disk1
diskutil unmountDisk /dev/disk1
dd if=image.dmg  of=/dev/disk1 bs=10m
diskutil unmountDisk /dev/disk1
```


* Boot von USB Stick: F2 Deutsch, F3 Berlin (wichtig - sonst wird System seltsam konfiguriert)
* F4 toram


* WLAN-Einstellung
	* Boot des core systems, Abspeichern von WLAN einstellungen:
	```
	wpa_passphrase Manns xxxx > config
	wpa_supplicant -i wlan 0 -c config -b
	dhclient
	ip a
	ping www.heise.de # voila
	```
* Install antix auf HDD, später wird davon ein live-USB System gebaut

```
cli-installer
cfdisk: 50+250+2GB primare Partitionen
sda1
3=ext4
home eigenständig: y
sda2
3=ext4
antix-net=n
MBR=Y
```

* Einrichtung des Systems
```
apt-get install fluxbox wicd rox-filer system-config-printer add-key-antix add-start-antix advert-block-antix alsamixer-equalizer-antix antix-archive-keyring antix-snapshot-cli automount-antix broadcom-manager-antix cli-installer-antix cli-shell-utils codecs-antix mouse-cc-antix mountbox-antix remaster-antix screenshot-antix system-antix xrdp wdm

apt-get install vim openssh-client nmap qalculate grun chromium geany mirage xmms mplayer gparted nano cifs-utils ntfs-1g
```

# Ubuntu
Create Launcher
```
sudo apt-get install gnome-panel
mkdir -p "$HOME/.local/share/applications"
gnome-desktop-item-edit "$HOME/.local/share/applications"  --create-new

Icon zuweisen, pfad ohne "$HOME"
```

Compiz
* Installation
```
sudo apt-get install compizconfig-settings-manager
ccsm
```
* Fenster plazieren > Fixed Window Placement: hier kann für Fenster
 festgelegt werden auf welchem Viewport die öffnen sollen
* Win-Cursor Settings: ccsm Fenster "Grid"



