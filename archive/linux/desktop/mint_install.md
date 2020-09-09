# Kriterien für neues Client Linux


* LTs, min 3 Jahre
* stabile Codebasis, lieber etwas älter als rolling release
* VPN support
* FreeIPA support 
* OEM installer / ansible rollout möglich?
* BTRFS und Snapshots, boot from BTRFF geht nicht wegen  EFI Partition
* Verschlüsselung über HD/BIOS Hardware, damit kann dann das gesamte System auf BTRSF aufgesetzt werden (ausser /efi) - siehe [Arch auf BTRFS][]
* Swap Datei auf BTRFS: Kernel 5.0+


# Install Mint

* Festplattenpasswort entfernen
* Installer iso booten, Chinnamon LTS Version
* Deutsch
* yes, proprietäre Treiber
* Verschlüsseln + lvm
* user: admin, Admin, Passwort
* reboot

Netzwerk - [VLAN][]

	sudo apt-get install vlan
	sudo su -c 'echo "8021q" >> /etc/modules'
	cat << VLAN_END > /etc/network/interfaces
	auto enp0s25.103
	iface enp0s25.103 inet dhcp
	vlan-raw-device enp0s25
	dns-nameservers 192.168.116.240
	VLAN_END

daraufhin erscheint das LAN Netzwerk nicht mehr in der gnome Netzwerkübersicht - funktioniert aber

Root passwort setzen

	sudo passwd root

Timeshift aktivieren, Methode rsync/btrfs ? geht alles nicht, ToDo
	* Manuelles partitions setup nötig

TLP: power management and increased system usability, prevent from overheating

sudo add-apt-repository ppa:linrunner/tlp
sudo apt update
sudo apt install tlp tlp-rdw
systemctl enable tlp
systemctl start tlp


# Configure Mint

Erste Schritte

* Firewall an, allow inbound tcp 22
* Systemeinstellungen > Bildschirme
* Treiber > propritär o.ä. aktivieren
* Paketquellen auf deutsche umstellen (Taskleiste rechts unten)
* System aktualisieren
	
Einstellungen

* Klang > Klänge > alles deaktivieren
* Themen 
    * Fensterrahmen Mint-Y-Dark
    * Symbole Mint-X-Dark
    * Schreibtisch Mint-Y-Dark
* Bluetooth > oben links deaktivieren
* Fenster > verhalten
	* Verhindern das Fenster den Fokus auf sich ziehen
	* Position neue Fenster: Automatic
* Fenster > Alt-Tab
	* Tab-Umschalter: Bilderfluss 3D
	* Tab-Umschalter: Minimierte Fenster am Ende
	* Fenster aller Arbeitsflächen
	* Verzögerung

* Arbeitsflächen: 3 (damit werden die in der Übersicht sehr groß angezeigt)

Fenster Verwaltung

Skripte nach `~/.bin kopieren`:

* `cycle_window`
* `dude`
* `myip`
* `start-anyapp`
* `start-terminal-ansible`
* `tft`
* `tmux-multiconnect`


Anpassen `PATH` in `~/.profile`

    PATH="$HOME/.bin:$PATH"




# Anwendungen

sudo apt install -y filezilla vlc inkscape gimp kazam thunderbird libreoffice
sudo apt remove -y rhythmbox

Editor

* xed > Bearbeiten>  Einstellungen 
    * Schrift "DejaVu Sans Mono Book" 9 pt
    * Bearbeitung > aktuelle zeiler hervorheben
    * Bearbeitung > Zusammengehörende Klammern
    * Speichern > automatisch Speichern > 0
    * Thema > Solar dunkel

Terminal

* KontextMenü > Deaktivieren Menüleiste
* Einstellungen > Tastenkürzel
	* Neues Fenster WIN+n
* Einstellungen > Profil
	* Text > Schrift "DejaVu Sans Mono Book" 9 pt
	* Farben 
        * Schwarz auf hellgelb
        * Fett NICHT in helleren Fraben darstellen
	* Deaktivieren: Transparenz
	* Bildlauf > Bildlaufleiste anzeigen
	* Befehl > Benutzerdefiniert > ssh ansible
	* Wenn Befehl ändert das Terminal geöffnet halten			
sudo apt install -y xfce4-terminal # seecondary terminal for local operation

Virt manager

    apt install -y spice-client-gtk gir1.2-spiceclientglib-2.0 gir1.2-spiceclientgtk-3.0  virt-manager

Messenger

	apt-get -y install pidgin

Remote desktop client

	sudo apt install -y remmina-plugin-nx remmina-plugin-rdp remmina-plugin-secret remmina-plugin-spice remmina-plugin-vnc remmina-plugin-xdmcp

Firefox

    cp -ra  pkcs11.txt handlers.json user.js  cert*.db extensions.json extension-preferences.json key*.db logins.json prefs.js places.sqlite search.json.mozlz4 persdict.dat  formhistory.sqlite extensions     ~/.mozilla/firefox/g3cg4b7d.default-release/ 



apt-get install -y chromium-browser vim pidgin

# Shortcuts

xfce4-popup-applicationsmenu in 'Settings/Keybaord/Application shortcuts'



iTunes

* Download iTunes 64 Bit
* run in terminal

	sudo apt install -y winehq-stable winetricks
	winecfg # mono, gecko nachinstallieren
	winetricks # DLL Pakete allcodecs 
mdac37 mdac28
	wine ~/Downloads/itunes64...

Reduce startup applications
Gnome Application Drawer >> Search for Startup >>Add/Remove/Edit as you like
* Flatpak
* mintwelcome
* Systemberichte

Add startup applications
* firefox
* chrome + 5s
* thunderbird
* pidgin  + 10 sec


# samba

Mit Server verbinden
	pdc01.vw.infra.gs.xtrav.de
	share: datashare
	domain: vw
	username v.nach

clean up
========

sudo apt autoclean
sudo apt clean
sudo apt autoremove


ToDo
=====
* BTRFS + Snappy
* sudo apt-get install gcompris   # lernen
* sudo apt-get install marble    # globus

[VLAN]: https://wiki.ubuntu.com/vlan
[Arch auf BTRFS]: https://wiki.archlinux.de/title/Arch_auf_BtrFS
