# Mac OS Einrichtung - Arbeitsplatz

## Software
Server, Devel
    GIT github gui: download https://central.github.com/deployments/desktop/desktop/latest/darwin
    Python3 python.org
    Powershell
    Docker
    Homebrew

Remote
    Seafile
    RDP (App Store)
    Swyx Client

Productivity
    Paste Clipboard Manager
    Forklift
    BetterTouchTool
    Teamviewer
    Atom für Projekte + VIM
    MacDown für Einzeldateien
    Microsoft Office: Excel, Word, PPT
    Microsoft Remote Desktop


## Homebrew


Installation

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)
    brew install wget 

# Backup und Datenablage

Aus meiner Sicht fahrt Ihr macOssis am Besten wenn:
* Alle Daten in der iCloud liegen 
    * Einstellungen > iCloud > iCloud Drive 
    * Einstellungen > iCloud> alles ausser "Mail"
Ihr Backups per Time Machine auf einer externen Festplatte habt, welche nach großen Updates oder Änderungen gezogen werden und dann unterm Kopfkissen verschwinden

In iCloud werden keine Systemeinstellungen gesichert. Die ändern sich aber auch nicht ständig, mit sporadischen Sicherungen sollten sich die Aufwände in Grenzen halten. 

Zum Timemachine Backup: Mehrere Macs können auf eine Platte sichern. Dabei wird die gesamte Festplatte verschlüsselt, dieses Passwort muss dann beim Anstecken auf beiden Macs angegeben und evtl im Schlüsselbund gesichert werden. Backup Platte: Lacie Rugged USB-C 2TB (100€)

2.) kannst Du bitte nochmal prüfen unter welcher AppleID Daniela arbeitet - ist das die gleiche wie in der Familienfreigabe?

LG Gunnar
 
    
ZSH
---

Z Shell and oh-my-zsh

    brew install zsh zsh-completions
    sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"


## Teamviewer

* Teamviewer 11 Installieren (alte versionen suchen), Lizenezschlüssel vom Fileserver> Kunden> Doku > Fellowtech > Teamviewer eintragen,

* Teamviewer Account einbinden
    * ID gunnar.mann@fellowtech.de
    * PW $Sm


## Reparatur Icons (default icon in dock)
Das ist ein Problem mit dem Dateisystem, hing wohl mit der Verschlüsselung des Laufwerks zusammen

### Plan A

Safe boot: Mac starten, während des Startes Umschalt-Taste gedrückt halten. Einmal starten lassen (eventuell File Fault entschlüsseln), danach Neustart. Was macht der Safe boot? [Viel](https://support.apple.com/de-de/HT201262)

### Plan B
Running Disk Repair out of Recovery Mode resolved this issue for me. Reboot while holding Command-R. Select Disk Repair from the menu. Select and Unmount Macintosh HD (if necessary). Select First Aid and run it. Restart from the Apple Menu.


## RDP Server

NuoRDS = iRAPP von https://www.nuords.com

## Teamviewer
Download, set up account

## MacDown
* Markdown >Intelligente Anführungszeichen
* Editor > Menlo 12pt, Mou Paper
* Vorschau > CSS Github 2
* Yes Syntax Highlight für Code Blöcke

## iTerm
Auch nicht besser als Terminal, nur zur Info:
* Markieren per Maus klappt besser, VIM: press ALT + Mouseclick to mark in Terminal mode
* Suche im Fenster, Mouseless copy
* Tmux Integration: see [Linux Shell and Console tips](../linux/shell,console.md)
    * run `tmux -CC a || tmux -CC` in remote linux session
* Clipboard History
* ToDo: [Shell Integration ](https://www.iterm2.com/documentation-shell-integration.html)    
    * copy files finder > remote
    * set marks in history
* Settings:
    * General
        * Yes Quit when all windows
        * No Confirm (both)
        * Yes Save history
        * No Copy on selection
        * Yes Applications may access Clipboard
        * No adjust window size
        * Open tmux windows as nactive windows
        * Open dashboard if there are more than 1 tmux windows
        * Yes bury tmux client window   (hide initial shell window after calling `tmux -CC`)
    * Profile `tmux`
        * Colors: Import Relaxed, Belafonte Dark, Novel von [diesem Repo](https://github.com/mbadolato/iTerm2-Color-Schemes)
        * Text: Menlo 11pt.

## Windows, Spaces, Better Touch Tool
Window management is configured in touchpad system settings and via [Better Touch Tool BTT](https://folivora.ai), see [here](https://medium.com/@arpitpalod/i-am-so-in-love-with-my-mac-trackpad-c3bbcecef41d) for introduction and some ideas.

See Jacob:Desktop files

## SSH
ssh config erstellt

```bash
mkdir -p ~/.cache/ssh/%h_%p_%r
```

```
Host *
    user root

    # re-use connections
	ControlMaster auto
	ControlPath ~/.cache/ssh/%h_%p_%r
	ControlPersist 4h

    # stay connected
    ServerAliveInterval 60
    ServerAliveCountMax 5

    # secure this client
    # https://stribika.github.io/2015/01/04/secure-secure-shell.html
    KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256

Host ft fellowtech
 	hostname zbxrelay.ft.local
	user root
	port 22
```

Schlüssel erstellt
```bash
ssh-keygen -b 4096 -C gunnar.mann@imac
```


## Safari

* Shortcuts: [See Shortcut world]( https://shortcutworld.com/Safari/mac/Best-of-Safari-Browser-Keyboard-Shortcuts)
* Command+1|2|3 = Tabs (auch fixierte)
* Ctrl-Tab: next tab
* Shift-Ctrl-Tab: previous tab
* Two-Finger Swipe left: reload page (F5)


## HomeBrew
Brew files are installed to `/usr/local/`:

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

* wait 1h

```bash
brew install git
brew install nmap
brew install git
brew install wget
brew install python3
brew install pigeon
brew tap caskroom/cask
brew cask install powershell
```
* update:
```bash
brew update
brew cask reinstall powershell
```


## RDP
Appstore Windows Remote Desktop 10

## Seafile
* Download von seafile.com
* Config f�r Benutzer FT:
	ID:
	PW:

##  Dash Doku Viewer, Atom Plugin
* Download von Webseite

## Transit App

* Your order ID: 1523527782970960
* Serial Number: T8EA-NAGA-6THL-X675-RKAK-A

## Terminal
Novel Theme is fine

### key codes for bash ssh sessions

Fixing the escape sequences sent by the Terminal. Open Preferences (for example, by hitting Cmd+,), and navigate to Settings tab, then for the profile you want to adjust, navigate to Keyboard tab. To get `\033` in the dialog box, just press the Escape key
```
home: \033[1~
end: \033[4~
page up: \033[5~
page down: \033[6~
```

### asc-compressor
siehe Vorlagen - angepasste Version unter `/usr/local/bin` einkopieren via `base64 -D | tar -xz`


### commands
```
open xxx.app
```

```
pbcopy, pbpaste
```

grab the link of the latest Google doodle and copy it to your clipboard
```
curl http://www.google.com/doodles#oodles/archive | grep -A5 'latest-doodle on' | grep 'img src' | sed s/.*'<img src="\/\/'/''/ | sed s/'" alt=".*'/''/ | pbcopy
```
spotlight search
```
mdfind -onlyin ~/Documents essay
```

spotlight rebuild cache
```
mdutil -E
```

spotlight disable indexing
```
mdutil -i off
```

### screen shots
Select a window using your mouse, then capture its contents without the window's drop shadow and copy the image to the clipboard
```
screencapture -c -W
```

Capture the screen after a delay of 10 seconds and then open the new image in Preview
```
screencapture -T 10 -P image.png
```

Select a portion of the screen with your mouse, capture its contents, and save the image as a pdf:
```
screencapture -s -t pdf image.pdf
```

## services

see here [Apple Developer page](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html)  and [some blog](http://paul.annesley.cc/2012/09/mac-os-x-launchd-is-cool/) for launchtl overview
show what launch scripts are currently loaded
launchctl list

start Apache web server automatically
```
sudo launchctl load -w /System/Library/LaunchDaemons/org.apache.httpd.plist
```

Partitionen, Disks

* Intel Macs can only boot from GUID partitions
* Apple requires 128MiB (262144 sectors) free space following a partition
```
diskutil cs list
diskutil list
diskutil listFilesystems


# erasing a volume requires specifying the filesystem and name
diskutil eraseVolume JHFS+ New /Volumes/SecondVolume
# erase volume, leave name and type as is
diskutil reformat /Volumes/SecondVolume
rename a volume
diskutil rename "{current name of volume}" "{new name}"
```

Partition a while disk, create a new volume with whole disk size (`0b`)

`g` is Gigabytes
```
diskutil partitionDisk /dev/disk2 GPT JHFS+ New 0b

split and merge partitions
diskutil splitPartition /dev/disk2s6 JHFS+ Test 10GB JHFS+ Test2 0b
diskutil mergePartitions JHFS+ NewName disk2s4 disk2s6
```

release free space
```
sudo diskutil eraseVolume "Free Space" %noformat% /dev/disk0s3
```

resize apfs container to use up all free space
```
diskutil apfs resizeContainer disk0s2 0
```

list gpt partitions
```
gpt -r show disk2
```

Unmount all the volumes on the disk
```
diskutil unmountDisk disk2
```

create an HFS+ partition in the free space (partition only, no file system)
if the new disk hasn't appeared, you'll need to reboot before formatting
```
sudo gpt add -b 409640 -s 195313624 -t hfs disk2
```

format via `diskutil erase` command above

Work on partition table without boot from disk: Restart into Internet Recovery Mode by pressing Command-R (oder alt-cmd-r (??)) , gedrückt haltem bis apple logo erscheint

```
diskutil cs list
sudo diskutil cs resizeVolume <lvUUID> %100
```

# apfs resize
```
sudo diskutil apfs resizeContainer disk0s2 ...
```

## Atom MacOS


### Installation

* download atom, copy to Programs
* Productivity plugins:
    * Settings
        * Install
    		* language-markdown
        	* markdown-preview-extended
            * image-view
            * markdown-image-paste
            * pdf-view
            * teletype
* my plugins:
    * Settings
        * Install
            * ex-mode
            * hydrogen
            ```
            pip3 install ipykernel
            python3 -m ipykernel install --user    
            ```
                * options: output in dock
            * atom-keyboard-macros-vim
            * atom-clock
            * convert-to-utf8
            * ex-mode-sort
            * remote-edit
            * sync-settings
            * vim-mode-plus
            * vim-mode-zz
            * vim-surround

* Markdown Preview PDF export:
    * via npm:
        ```bash
        sudo npm install -g phantomjs-prebuilt
        ```
    * manually:
        * [download PhantomJS](http://phantomjs.org/download.html) and
        * copy to `/usr/local/bin/`:
            ```bash
            sudo cp ~/Downloads/phantomjs-*-macosx/bin/phantomjs /usr/local/bin
            ```
    * test: `phantomjs` must be executable
    * configure
        * edit `~/.mume/style.less`
            ```
            .markdown-preview.markdown-preview {
                @media print {
                    font-size: 8pt;
                }
            }
            ```

### Latex PDF export
Edit markdown files, export to pdflatex via `markdown-preview-enhanced`:
* install pandoc adn pdflatex in macos
```bash
brew install pandoc
brew cask install basictex
ln -s /Library/TeX/texbin/pdflatex /usr/local/bin/
```

See https://kofler.info/atom-als-markdownpandoc-editor/
Usage: Start md document like


check out: pandoc-convert - works good with standard markdown ... todo: format
code blocks and hyperlinks better,

```
---
title: "Habits"
author: John Doe
date: March 22, 2005
output: pdf_document
---
```

### Configuration
sync- settings plugin:
* see [Instructions](https://atom.io/packages/sync-settings)
* Github Token: `64db9efd0ac6d52dd68a4677ce05a2aa8098e01b`
* Gist ID: `695b86c22458b37f221e2e01057faa8f`
* Usage: Shift-Command-P sync-settings backup|restore

Settings
* Core
    * Enable "open empty editor on start"
* Editor
    * Enable Softwrap
* Packages
  * spell-check > Use Locales > de-DE
   * spell-check > Activate Add Known Words
    * Autocomplete Plus
        * Keymap for confirming a Suggestion "Tab always, enter when ..."
* My Settings
    * VIM Escape mode via `jk` (`ESC` is a little far from home position): edit `~/.atom/keymap.cson`:
        ```yaml
        'atom-text-editor.vim-mode-plus.insert-mode':
          'j k': 'vim-mode-plus:activate-normal-mode'
        ```
    * Editor
        * Font family "menlo"
    * Packages
        * atom-clock
            * Time format `dd. DD. MMM HH:mm (W)` (with calendar week)
            * Locale `de`
* At first start, change to `welcome.md` pane and uncheck "Show Welcome Guide ..."
* Enable "autosave" plugin in settings - stores "untitled" tabs etc.
* Switch language for spell checker
* Fix Tab switching to work with Control-Tab and Shift-Control Ta
    * Go the Atom menu > Open Your Keymap and add:
    ```yaml
    'body':
      'ctrl-tab': 'pane:show-next-item'
      'ctrl-shift-tab': 'pane:show-previous-item'
    ```

### Usage
See [Sitepoint blog]( https://www.sitepoint.com/12-favorite-atom-tips-and-shortcuts-to-improve-your-workflow/)

* Command palette: Shift-Command-P - run every command available in atom
* Work on current document, hide everything else Command-ENTER
* Multiple cursors: Command+Click
* Preview Toogle: Shift-Control-M
* Open Project folder: Control-Shift-A
* edit from command line: atom FILE1 FILE2 DIR1 DIR2
* markdown preview:
    * activate like Shift-Control-M for files ending like `*.md`
    * in preview pane:
		* Table of contents: ESC
        * PDF export:
    		* Right click
    			* PhantomJS
    				* PDF
* sort text: visual mode, mark, Control-s, type "sort"
* disable core packages (mostly redundant to vim functions):
    * about
    * autocomplete-atom-api
    * autocomplete-css
    * autocomplete-html
    * autoflow
    * background-tips
    * bookmarks
    * bracket-matcher
    * command-palette
    * deprecation-cop
    * dev-live-reload
    * encoding-selector
    * execution-reporting
    * git-diff
    * github
    * go-to-line
    * grammar-selector
    * language- c coffee-script css csharp git go java java-script less mustache objective-c ruby ruby-on-rails sass toml typescript
    * markdown-preview
    * metrics
    * open-on-github
    * package-generator
    * styleguide
    * welcome
