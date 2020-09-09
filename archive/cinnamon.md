# Cinnamon desktop setup


## centos

switch gnome to centos

```
yum install epel-release -y
yum groupinstall "Server with GUI" -y
yum install cinnamon -y
```


## system
* ssh config

## favorites

* plank: `sudo yum install -y plank` 
    * Wird auf Hauptbildschirm angezeigt
    * left click icons => keep, arrange
    * Einstellung: Click auf Plank Symbol


## task bar

* Calendar: enable displaying week numbers
* Calendar display format string: `%a, %e. %B %H:%M KW %V`
* Leisten verschieben/löschen: RM auf Leiste (freie Stelle) > Leiste verändern > lesen und machen



* Menu > RM > configure > user defined symbol > `/usr/share/cinnamon/theme/menu-symbolic.svg`


## keyboard shortcuts

* CTRL + ESC terminal on jump host: `gnome-terminal --window-with-profile=Ansible`
* SHIFT + ESC terminal on local host: Starter > Start Terminal
* STRG + WIN + ALT + UP: lock screen
* STRG + WIN + ALT + DOWN: shut down

### window switching

switch to or start firefox
* edit `~/.bin/start-anyapp`
```
#!/bin/sh
set -eu
CMD="${@:-}"
if [ -z "$CMD" ]
then
    echo "Usage: $(basename $0) <executable in path>" 1>&2
    echo "Example: $(basename $0) firefox" 1>&2
    exit 2
else
    if ! wmctrl -x -a $CMD; then
        exec $CMD
    fi
fi
```
* create shortcut command `/home/g.mann/.bin/start-anyapp firefox`

switch to or start jump host terminal (by profile)
* edit `~/.bin/start-ansible-terminal`
```
#!/bin/sh

PROFILE="Ansible"
LOCAL_TERM="g.mann@quince"

ansible_window_title=$(
    wmctrl -lx \
        | grep -vi "$LOCAL_TERM" \
        | grep "gnome-terminal" \
        | head -n 1 \
        | cut -d ' ' -f 7-
)

if [ -z "$ansible_window_title" ] 
then
        exec gnome-terminal --window-with-profile=$PROFILE
else
        wmctrl -F -a "$ansible_window_title"
fi
```

switch to next window of same class
```
#!/bin/bash
# call like cycle_window back to enable reverse switch


set -euo pipefail

# get id of current window
active_win_id="$(
    xprop -root \
    | grep '^_NET_ACTIVE_W' \
    | awk -F'# 0x' '{print $2}'
)"
if [ "$active_win_id" == "0" ]; then
    active_win_id=""
fi

# get window class of current window
current_win_class=$( wmctrl -lx | grep $active_win_id | awk '{print $3}')

# get list of all windows matching with the class
win_list=$(wmctrl -x -l | grep -i $current_win_class | awk '{print $1}' )

# reverse window list if wanted
if [ "${1:-}" = "back" ]; then
   win_list=$( echo $win_list | tr ' ' '\n'|tac|tr '\n' ' ')
fi

# get next window to focus on, removing id active
switch_to=$(echo $win_list | sed s/.*$active_win_id// | awk '{print $1}')

# if the current window is the last in the list ... take the first one
if [ -z "$switch_to" ];then
    switch_to=$(echo $win_list | awk '{print $1}')
fi

# switch to window
wmctrl -i -a $switch_to
```


## mouse support
http://xahlee.info/linux/linux_xbindkeys_tutorial.html


## applications
* terminal: WIN + C, WIN + V, WIN + X copy paste cut

