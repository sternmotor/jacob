Window management is configured in touchpad system settings and via [Better Touch Tool BTT](https://folivora.ai), see [here](https://medium.com/@arpitpalod/i-am-so-in-love-with-my-mac-trackpad-c3bbcecef41d) for introduction and some ideas.

All gestures which look too hard to learn easly are left out. All settings below starting with `BTT` are done in Better Touch Tool, mostly in Trackpad and Keyboard settings.

Hint: When adusting trackpad actions, watch grey rectangular mini-display how the gesture is supposed to look like.

General idea:
* 3Finger Swipes and Command-Key-Combinations act on applications, tabs, windows
* 4Finger Swipes and Control-Key-Combinations act on spaces and mission control
* 5Finger Swipes act on mac os system
* left-right movements and arrows switch tabs, windows and spaces
* up/down movements open/close something
* up is fullscreen, down restores size
* 3Finger tap and double tap is reserved for application-specific setup

### Global setup
Settings for all applications

#### Switch, open, close tabs

Switch tabs
* 3Finger swipe left/right (BTT)
* 2Finger TipTap left/right (BTT)
* Control-Tab, Shift-Control-Tab

New tab, close tab
* 3Finger swipe up down (BTT)
* Shift-Command arrow-key up/down (BTT)
* Command-t, Command-w

#### Switch, open, close windows

Switch application windows
* 3Finger click-swipe left/right (BTT)
* 3Finger TipTap left/right (BTT)
* Command-<, Command->

New window, close window
* 3Finger click-swipe up down (BTT)
* Command-n, Shift-Command-w, Command-w (when no tabs are present)

#### Drag-move and drag-resize window

Move single window: Control + Drag
* Advanced moving & resizing > Control-Mouse/Touchpad move (BTT)

Resize single window: Command + Drag
* Advanced moving & resizing > Command-Mouse/Touchpad move (BTT)

#### Maximize and move window

Maximize window left/right/toggle fullscreen/restore
* Command-3Finger swipe left/right/up/down
* Command-Arrow key left/right/up/down (BTT)
* Command-TouchPad-Tap left, right, top edge (in the middle), bottom egde (BTT)

Toggle full screen
* 4Finger double tap (BTT)
* Command-Arrow key up (BTT)

Resize window to quarter size in edge of screen
* Control-Command-3Finger swipe up/down/left/right (BTT)
* Control-Command-Arrow key (BTT)
* Control-Command-TouchPad-Tap in corners (BTT)
* Command-TouchPad-Tap in corners (BTT)

Zoom into window
* 2Finger double tap

#### Spaces, Mission Control

Switch spaces left right
* System Settings > 4Finger swipe left/right
* Control-Arrow key left/right

Mission Control
* System Settings > 4Finger swipe up
* Control-Arrow key up

Show all windows (and tabs for some apps) of current application
* System Settings > 4Finger swipe down
* Control-Arrow key down

#### System Settings
This settings need to be taken in system settings, otherwise the BTT mappings do not work properly

* Touchpad
	* Mission Control > 4Finger swipe up
	* Exposé > 4Finger swipe up
* Dock
    * Auto-hide, learn to use Command-Space

### MacOS System Tools

Take screen shot
* 5Finger swipe up (BTT)

Open Finder
* 5Finger swipe right (BTT)

Open iTerm
* 5Finger swipe left (BTT)

Screen saver, lock desktop
* 5Finger swipe down (BTT)

Computer sleep
* Command-5Finger swipe down (BTT)

### App specific settings

Applications need to be added in the left side bar.  

#### Microsoft Remote Desktop
Disable BTT completely for Microsoft Remote Desktop App


#### iTerm

Terminal setup is the template for window - based work style

New window, close window
* 3Finger swipe up down (BTT)
* Command-n, Command-w (when no tabs are present)

Switch application windows
* 3Finger swipe left/right (BTT)

Maximize window left 3rd, center 3rd, right 3rd
* Option-TouchPad-Tap left, right, top edge (in the middle) (BTT)
* Option-Command-Arrow key left/right/up (BTT)

Restore Window Size
* Option-Command-Arrow key down (BTT)

#### Safari and Chrome

Safari setup is the template for tab - based work style (fullscreen windows in spaces)

Open link in new tab
* 3Finger tap (BTT)

Reload page
* 3Finger double tap (BTT)

#### Atom

Switch tabs
* 3Finger swipe left/right (BTT)

New tab, close tab
* 3Finger swipe up down (BTT)
* Shift-Command arrow-key up/down (BTT)

Show Markdown preview
* 3Finger Click-Swipe right (BTT)

Toggle Project Side bar
* 3Finger Click-Swipe left (BTT)


#### Finder

Folder up/down
* 3Finger swipe up/down (BTT)
* Command-up/down (BTT)
    * Command-Down: "Use Apple Default or do nothing" (Trigger> search "default")
    * Command-Up: "Use Apple Default or do nothing" (Trigger> search "default")

Cycle trough view modes (list/preview)
* 3Finger swipe left/right (BTT)

Maximize Window
* Command-Arrow left/right

New Folder
* 3Finger tap (BTT)

New File
* 3Finger double tap (BTT > System Tools)
