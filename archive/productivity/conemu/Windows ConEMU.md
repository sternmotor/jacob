## Conemu 
ConEmu wird als Erstaz für die Powsershell und CMD Consoel konfigurioert und dementsprechend auch direkt über die Standard powershell und cmd Anwendnungen gestartet.
Dazu muss einmalig Conemu gestartet werden und per Rechtscliak auf den oberen Fensterrahmen > Integration > Default Term die obere Option ausgewählt werden:
* Force Conemu as default ...




## Bedienung
### Task Bar
* zusätzliche Konsole öffnen: Shift-Clck auf bestehends Icon eines geöffneten Fensters - geht nur wenn Conemu über die normale Powershell gestartet wurde

### Keyboard and Mouse Actions:
* TODO WIN<ins>Mouserad Fensterhöhe anpassen, Shift-Win</ins>mouserad: Fensterbreite
* Win<ins>Mouse-rad: Schriftgröße
* TODO Fenster nach rechts/unten aufteilen : CTRG-WIN-ALT reight/down
    * TODO Teilfenster schließen: 
    * TODO Teilfenster links/recht/oben/unten aktivieren CTRG-WIN
* TODO Zusätzliche fenster öffnen: Win-N
* TODO Open new tab: CTRL-T
* TODO Close the tab: CTRL-DEL
* !Switch to next tab: CTRL</ins>Alt<ins>Arrow right
* !Switch to previous tab: CTRL</ins>Alt<ins>Arrow left
* Cycle tabs: Ctr</ins>Tab
* Copy text from console to the system clipboard: 
    * TODO Press and hold Shift, use arrows to make a selection and then hit Ctrl<ins>C.
    * Press and hold left mouse button, make a selection and click right mouse button  (like Putty/Powershell)
    * Press CTRL and hul right mopuse button for block select
* TODO Press right mouse button or CTRL-V to paste all the clipboard content.
* TODO CTRL-F find in buffer

## Installation
* Download "stable" Version als 7z Package, entpacken nach C:\Programme\Tools
* In Conemu Ordner gehen, dort den Plugins ornder komplett entfernen
    * im Conemu/conemu Unterordner alle UnterOrdner entfernen bis auf Scripts
    * Alle     {{*.xml}} Dateien entfernen 
* Beim ersten Start: Anpassungen im Schnellkonfig-Fenster: 
    * Settings storage location: `...\ConEmu\ConEmu\ConEmu.xml`
    * Startup Task Shells::Powershell
    * Keyboard hooks: no
    * Inject ConEmuHk: yes
    * Update: Stable

## Konfiguration
ConEmu ist in der Standard-Konfiuration relativ verspielt
* Sehr aufwändig, den ganzen Krempel der gut gemeint ist aber von der Arbeit ablenkt oder nicht benutzt wird oder nervt (Bestätigungsabfragen) abzuschalten
* Sehr aufwändig: Anpassung an Standard-Tastaturkürzel (STRG-T für neuen Tab etc
* Menü ist komplett durcheinandergewürfelt

Zum Glück alles abgespeichert in xml Datei

### SSH/Linux Integration
* Environment
```
set TERM=xterm-256color
set LANG=en_GB.UTF-8
set LC    *ALL=en    *GB.UTF-8
```
* Features > Inject COnEmuHK yes
* Features > Ansi and xterm: yes
* Features > Kill ssh-agent: no
* Features > Colors: TrueMod 24bit yes (for 256 colors)


###System
* Main/Update: Stable
* Startup: named task: Powershell
* Environemnt: Add conemudir to path yes
* Main> Bacground: allow bacground plugins no
* Features > Default term > Force ConEmu as default terminal yes
* Features > Default term : Register on OS Startup no
* Features > Default term Use existing window if avaliable
TODO: vim 256 colors support

### Appearance: Fonts und Windows

* Main: Consoloas 14 einstellen, Antialiasing Clear Type
* Main> Size & Pos: Window Size 85x45
* Main> Size & Pos: size autosave no, show& store no
* Features > Auto register fonts in Conemu Folder off
* Main/Appearance/ Scrollbar Auto-Hide
* Main/Tab-Bar AutoShow yes, Internal CTRLTab ye, Far Windows deaktiveren, Host</ins>key ... deaktiveiren
	*  Main/Tab-Bar: Tab Font Consolas 12
	*  Main/Tab-Bar: Modified suffix: {{"    **"}}
* Main/Task-Bar: Taskbar buttons: show all consoles
* Main/Task-Bar: Show progress indicator
* Features > Text cursor: Block yes, Color yes, Blink no
* Features> Colors > Scheme Monokai oder Solarized 
* Features > Transparnece no
* Status Bar no
* Features> Colors: Fade when inactive abschalten

### User Interface
* Main/Appearance: Show buttons: no show searchfield: yes
* Main/Appearance: Multiple consoles
*  Main/Tab-Bar: double click actions: tab button close, tab bar: open new shell
* Main/Confirm: alles aus
* Main/Appearance: enahance progressbar no ballon help no
* Main/Task Bar: Jump List Add Conemu Task, Add commends fromhistoryyes , Autoupdate yes
* Features > Colors: Adjsut lightness von unslebarem Text: yes!!
* Main> Size & Pos: Long Console 5000
* Features > suppress bells yes
* Features > Monitor Console lang no
* Features >  use clink: no
* Features >  process 'start' no
* Keys & Macro > Keyboard:hier alles deaktiviern bis auf CTRL-Backspace
* Keys <ins> Macro > Keyboard: TODO shortcuts s.u.
* Keys </ins> Macro >Mark & Copy: Intelligent yes, Text-Selection No-Mod, Block = CTRL, copy on leftbutton release = no, show ibeam cursor no
*  Keys <ins> Macro >  Paste: Multi-Lines CTRL-V yes, Confirm deaktivieren
*  Keys </ins> Macro > Highlight deaktiveren
* Startup/tasks: 
    * Shells::Powershell 
    * default task for new console: yes
        * default shell Win+X: yes
        * Taskbar jump list: yes
    * Shells::Powershell /Admin)
        * Taskbar jump list: yes
    * Shells::Cmd
        * Taskbar jump list: no


