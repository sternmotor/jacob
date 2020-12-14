Allgemein
=========

* Alle öffentlichen Texte zweisprachig (Abwesenheitsmail)
* Admin-Anleitungen deutsch
* Willkommens Leitfaden ist nur deutsch, muß zweisprachig werden => eh alles neu schreiben


Arbeitsplatz einrichten
=======================

Netzwerk
---------

* Tagging Linux/Windows, WS, VW, WN Netzwerk
* Tagging Brocade/ DLink smart switch

Hardware 
--------

* Links Laptop/ PC, 2 Bildschirme zwischen denen Maus- 
  und Tastatur-Kabel verläuft, rechts oder Mitte Telefon
* USB direkt an PC/Docking Station
* Verkabelung USB, Lautsprecher
* einwandfreie Netzwerkkabel verwenden
* Netzwerkkabel Telefon > Rechner oder Telefon + Rechner oder Switch?
* Telefon vorbereiten auch wenn keins verwendet wird (Kabel verlegen)
* keine Kabelbinder
* PC/Notebook beschriften: 
    * Rechnername
    * Kürzel Hauptbenutzer

Konfiguration Systeme (Benutzer anlegen)
----------------------------------------


IPA 
* IPA Gruppen
    * Beispiel xRes Team:
        * dokuwiki
        * developers_xres
        * jira-developers
        * gitlab_users
        * grafana_viewers
        * jira-users
        * jabber_users


Crowd  für Confluence
* Benutzer einrichten

Mail
* Welche Mail Kalender und Verteiler?      Hotfix, Team, Spam und Entwicklung
    * Standard Kalender
        * Team
        * Urlaub
    * Dev/Admin Verteiler
        * Hotfix
        * Bereitschaft
        * Nagios
        * CheckMK
        * Jira
        * Notfall
    * Entwicklung Verteiler
        * Support
        * Hotfix
    * Admin Verteiler
        * adminteam
    * Support Verteiler
        * supportteam

* Kolab  https://mail.traso.de/kolab-webadmin/?
* Passwort vorname nachmae initialen

DataShare Berechtigungen, VW Domain Member + Password

Zugänge xmid, wiki, gustav, jira, redmine, otrs

Windowsuser (wn Domäne)


Rechner Installation
------------------

Rechnernamen ausdenken: englische Frucht    
Linux:       .ws.infra.gs.xtrav.de                             
Windows:    .wn.infra.gs.xtrav.de

Seriennummer und Model ablesen, notieren   
    * Eintragen in Inventar-Excel
    * Host, linux_notebook_fujitsu, Kommentar "Employee: ISH, Fujitsu S936"
Laptop: Festplatten Verschlüsselungspasswort 
    * festlegen  
    * in Passport ablegen


Rechner Aufbau: Namen ausdrucken, auf Laptop/ PC aufkleben

Laptop/ PC Verschlüsselung (BIOS)



### Linux OS Installation

Download CentOS Image: http://mirror.infonline.de/centos/7.7.1908/isos/x86_64/CentOS-7-x86_64-DVD-1908.iso
Image auf USB Stick packen

    sudo dd if=Downloads/CentOS-7-x86_64-DVD-1908.iso of=/dev/sdb bs=1M && sync

Laptop BIOS Einstellungen: Festplatten Verschlüsselung
* Das BIOS Menü wird durch wiederholtes Drücken von F2, BS, DEL und Enter erreicht
   
* Festplatten Passwort läßt isch nicht nach einem Reboot festlegen, nur nach komplettem Shutdown
    * Security → „Password at unattended boot“ und „Password at restart“ deaktivieren. 
    * Security > ... > Passwort setzen

Neustart mit USB Stick: Boot Menü mit F12 einschalten
Centos Install
* language entsprechend Benutzer-Sprache
* Software Selection: 
    * GNOME Desktop + Applications:
        * GNOME 
        * Internet 
        * Office Suite

    * Disk > select (white-on-black label) , reclaim Space from windows installation, Done, Remove All
    * Start installation
        * set root password
        * keinen Benutzer anlegen
    * Reboot
        * Accept License
        * Network > hostname FQDN s.o.
        * No User Creation
        * Location Service Off
        * Timezone City Berlin
        * User setup: test test , Password
        
    * Desktop
        * Wired LAN ON
        * IP feststellen
            * Terminal > ip a > 192.168.107 ... 


Rechner anlegen (IPA)
* Identität > Host > Hinzufügen   , Zone ws.infra.gs.xtrav.de.
* Netzwerkdienste > DNS > DNS-Zonen ws.infra.gs.xtrav.de.
    

Ansible Basis ausrollen:

* Schlüssel vom Benutzer auf ansible Server manuell auf root authorized keys des neuen Rechners übertragen

    ssh root@grape.ws.infra.gs.xtrav.de
    ssh-keygen -N '' -f ~/.ssh/id_rsa.pub -b 4096   
    cat - > ~/.ssh/authorized_keys
    # copy-paste authorized_keys von anderem Server, CTRL-D to exit
    chmod 0600 ~/.ssh/authorized_keys

* Ansible Basis ausrollen

    ansible-playbook playbooks/workstations.yml -l grape.ws.infra.gs.xtrav.de 
    docker, ssh, nscd, ipajoin, tuning 


### Windows

* lokalen Admin anlegen (wsb)
* Startkonfiguration alle Fragen mit "Nein" markieren. Kein GPS! Keine Cortana! nichts davon auswählen!
* Computernamen vergeben und Domäne setzen

    VerwaltungsNetz = vw.infra.gs.xtrav.de
    WindowsNetz = wn.infra.gs.xtrav.de

* WindowsAntiSpy-Script ausführen (https://git.app.infra.gs.xtrav.de/infra/skripte/tree/master/Windows/Windows-Antispy)
* Drucker einrichten
     printer01.per.infra.gs.xtrav.de
     printer02.per.infra.gs.xtrav.de
* Laptop/ PC Verschlüsselung


Programme deinstallieren

* Wunderlist
* Dolby Digital Plus
* WLAN und Mobilfunkguthaben
* Tap Windows
* Pics Art
* Network Speed Test
* FreshPaint
* Feedback-Hub
* Erste-Schritte
* Duolingo
* 3DBuilder
* Xbox

Programme installieren

* chocolatey script (https://git.app.infra.gs.xtrav.de/infra/skripte/tree/master/Windows/chocolatey)
* urbackup Client


Abschließende Installation und Konfiguration
--------------------------------------------

* VPN
* Drucker
* Thunderbird 
    * Mail imap, smtp
    * Signatur und Abwesenheitsnachricht ??
    * Verteiler, Sieve
    * Kalender
    * Addressbuch Import
    * Enigmail + Cert
* Windows Support:
* Windows Verwaltung:
     * Sage client
* Dev Team:       Entwickler-Rechner für PHP, also PHP-Storm, MySQL-Workbench oder Heidi, Docker ... usw. 
    * PHPStorm, php 7  5.6, 7.0, 7.3 remi repository
    * PHP 7.3
    * Docker CE
    * Git
    * DBeaver
* Admin Team:
    * Virtual Machine Manager
    * X2Go Client x2goclient-4.0.1.4
    * Jira Login
    * Yubikey 2Faktor Auth

### Linux

### Windows

* MS Office - Word, Excel & Co. (ACHTUNG: Makros und die Makro-Verarbeitung sollten bei allen standardmäßig deaktiviert sein und am besten bleiben)
* Office & Windows aktivieren
* Greenshot - Imgur Plugin deaktivieren in Conf ! greenshot.xlsx
* urbackup Client


Details
-------

### Mail TB

    Start thunderbird
    Mail, Email, Password
    Manual config
    siehe Willkommensleitfaden
    Username: lastname for imap and smtp


    Omit Masterpassword?
    check all folder s for new mail
    Hamburger > preferences > preferences > Advanced > Config Editor
    
    Signature
        Account Setup > Signature > Use HTML
        Copy Paste from wiki
            Adapt: 
                Firstmann, Lastame
                Department
            Extension or 0 Phone extesnions 0 or real number
            Fax Extension 21
            Mail Address
        Kolab > Settings > Idenitities > Signature, paste

    Support Postfach
        dasselbe
    
    Out of Office Replay
        Roundcube > Settings out of office 
        betreff: offen
            
    Developers: no sieve mail only managers 

    Enigmail:
        * install plugin via thunderbird plugin manager
        * Hamburger > Enigmail > Setup Wizard
        * Keys alreadys installed > apply keys     # from thunderburd enigmail keys?
        * Key Manager > set password on key
                    * Upload keys to key server hkps://hkps.pool.sks-keyservers.net
                    * Confirm Confirmation mail, wait
                    * Generate and store revocation certificate
                    
    send revocation cert to admin@traso.de "Revocation i.shumeiko@traso.de"

    Lightning
    Kolab:
        Settings > Folder > Sahred > Kalender, mark < your team> , team, urlaub, krank
        siehe willkommensleitfaden
        
        TB Lightning: userName = email v.nachname@traso.de, password is kolab password
        Automatisierung: 
            * https://mail.traso.de/iRony/calendars/gunnar.mann%40traso.de/57e29af3-79b8-4f73-b959-a5af1a3c31fe
            * ID is gleich, benutzername anders

### phpstorm
* download from jetbrains.com
* install
* give root password one time
* insert license server url: http://jetbrains.app.infra.gs.xtrav.de/
    

GitLab
* Gruppe enstprechend team ... alle repositories mappen



### Drucker

    Beide Etagen-Drucker werden installiert, um bei Ausfällen einen Ersatzdrucker zur Verfügung zu haben.

    Drucker Addressen
        * printer01.per.infra.gs.xtrav.de
        * printer02.per.infra.gs.xtrav.de

    Windows 10:

        * Logo > Einstellungen > Geräte und Drucker > Nicht in Liste enthalten > Drucker Adresse eingeben
        * Adresse eingeben
        * Admin-PW
        * Namen anpassen: "Drucker OG 1" bzw. "Drucker EG"
        * Teststeite drucken



### Datashare
        rover.app   Benutzer anlege
        finder > + other location > smb://pdc01.vw.infra.gs.xtrav.de/datashare
    

Abschluss
=========

Übergabe Zettel ausdrucken

    Konkreten Namen einsetzen statt v.nachname

IPA change password 

    IPA > User > Actions > Reset password, ENTER old, leave OTP empty, new password
    Store bookmark

MAIL change Password

    mail.traso.de (siehe Willkommenszettel)
    Settings > Password > 
    Store bookmark

