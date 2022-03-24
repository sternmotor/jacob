# Mac OS Einrichtung - Arbeitsplatz

## Software
Server, Devel
    Python3 python.org
    Homebrew

Remote
    Seafile
    RDP (App Store)

Productivity
    Paste Clipboard Manager
    BetterTouchTool
    Teamviewer
    MacDown für Einzeldateien
    Microsoft Office: Excel, Word, PPT
    Microsoft Remote Desktop


## Homebrew

Installation

    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)
    brew install wget 

## Finder

Preview for all sorts of files in finder, column view:

    brew install qlcolorcode qlstephen qlmarkdown quicklook-json qlimagesize \
    suspicious-package apparency quicklookase qlvideo

To get plugins working in Catalina, you will need to remove the quarantine attribute.

    xattr -d -r com.apple.quarantine ~/Library/QuickLook


## Backup of system and application data

iCloud data does not store system settings but allows for easy access to your data from all devices. For desaster recovery and migrations, do time machine backups from time to time- most settings do not change very often.

* Store all app data in iCloud - easy recovery and migration 
    * enable settings > iCloud > everything except "eMail"

* Run Time Machine backups to an external harddrive stored in a safe place - do this before big updates oder after important system changes (desaster recovery). Multiple macs may run backups to one single backup disk, using the same encryption key.


## Boot options

Safe boot - self repair

Hold shift key while booting (around "bang" sound) for [safeboot](https://support.apple.com/de-de/HT201262)

Recovery mode (disk repair): 
* Hold Command-R while booting (around "bang" sound) 
* Select Disk Repair from the menu. Select and Unmount Macintosh HD (if necessary). Select First Aid and run it. Restart from the Apple Menu.


## RDP Server

NuoRDS = iRAPP von https://www.nuords.com

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
brew update
brew install git nmap git wget python3
brew tap caskroom/cask
```


## RDP
Appstore Windows Remote Desktop 10

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
