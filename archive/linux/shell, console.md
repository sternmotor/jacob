# Tools

Screen: Connect to eventually running session - close it and adapt screen size
    ```bash
    screen -ADR
    ```

Tmux: see section below

# Bash command line

Navigation and editing

* `Ctrl + a`: jump to the start of the line
* `Ctrl + c`: terminate the command
* `Ctrl + d`: delete from under the cursor
* `Ctrl + e`: jump to the end of the line
* `Ctrl + k`: delete to EOL
* `Ctrl + l`: clear the screen
* `Ctrl + r`: search the history backwards
* `Ctrl + R`: search the history backwards with multi-occurrence
* `Ctrl + u`: delete backward from cursor
* `Ctrl + w`: delete backward a word
* `Ctrl + x` : move between EOL and current cursor position
* `Ctrl + z`: suspend/stop the command

History: edit `/etc/bash.bashrc` respectively `~/.bashrc`
```
# enable history appending instead of overwriting.
    shopt -s histappend   
# make bash autocomplete with up arrow. move arrow left-right
# and up/down again to see the whole story.
    bind '"\e[5~":history-search-backward'  
    bind '"\e[6~":history-search-forward'  
```

## User interaction

Query admin password for firewall interactively
```bash
echo -n 'Enter firewall "admin" user password: '
Prompt=''
while IFS= read -p "$Prompt" -r -s -n 1 char
do
    # Enter - accept password
    if [[ $char == $'\0' ]] ; then
        break
    fi
    # Backspace
    if [[ $char == $'\177' ]] ; then
        Prompt=$'\b \b'
        AdminPassword="${AdminPassword%?}"
    else
        Prompt='*'
        AdminPassword+="$char"
    fi
done
echo
```

# TMUX

## Organisation and Workflow

* In short:
	* sessions = projects
	* windows = server logins (like tabs) and pair programmer's window sharing
	* panes = tasks at servers


* Tmux basically has three levels of abstraction. The session. This level occurs automatically when you spawn tmux. Each session can have multiple windows. In turn, each window can have multiple panes. These panes can be moved within and between windows, and the windows can be moved within and between sessions.

other view:

* Tmux has three levels of hierarchy when it comes to organizing views: Sessions, windows, and panes. Sessions are groups of windows, and a window is a layout of panes. Windows and panes are to a certain degree interchangeable as we will see, but sessions are fairly immutable. I use sessions to separate workspaces, almost like the spaces in osx. Windows and panes I use as is convenient.

* Because I tend to isolate projects to a single session, allowing me to have a complete context switch when needed, I tend to name them the project I am working on

* Windows in tmux have a name, and a sort number. They live in the bar at the bottom of the screen, ordered by their sort number

* If you invoke the tmux console, type in link-window, and you can share a window between two sessions, using the same target/source syntax as move. That means I can have the same shell, or the same program shared between multiple sessions. No more juggling the irc window, I can simply have it everywhere

* DevOp window names: `dev`, `op`, `test`


## Usage

### Speeding up tmux 
Tmux is rather slow with vertical split windows ... SSH compression helps:

* edit `~/.ssh/config`, add
```
Compression yes
```

### Keyboard Shortcuts

Prepend each listed key with `CTRL-b`.

General
* `d`: detach all sessions
* `D`: detach selected session
* `t`: clock, time
* `?`: help
* `tmux new -s bob -t alice`: colaboration: bob creates own session connecting to alice's windows

Sessions
* `tmux new -s <session name>`: create session
* `tmux a -t <session name>`: reattach to existing session
* `:new<CR>`:  new session
* `s`:  list/switch sessions
* `$`:  rename session
* `:link-window -s <othersession_name>:1 -t 4` stick other session's window 1 to window 4
* `:unlink-window`: unlink sticky window (run in linked window)

Windows
* `<N>`: switch to window number N
* `c`: new window
* `w`: list windows
* `l,n,p`: last, next, previous window
* `&`: kill window
* `,`: rename window
* `: move-window -t <session name>` Move window to other session

Panes
* `Cursor`: select pane
* `"`, `%`: split upper/lower, left/right
* `z`: Toggle zoom for mouse copy/paste
* `x`: kill pane
* `q`: show pane numbers (enter number to go to that pane)
* `!`: break pane to new window
* `{}`: swap panes
* `space`: rotate pane layout
* `t`: hide pane content - display clock

Copy/ Search/ Scroll Mode
* `PageUp`: Enter copy/search/scroll mode
* `q`: Exit copy/search/scroll mode
* `CTRL + s`: (in Copy mode) Search, CTRL +n,p for next previous
* `z`: Toggle zoom for mouse copy/paste

### Collaboration

One cursor approach (simple)

    tmux new -s shared  # A
    tmux a -t shared    # B


Independent window switch: mutiple sessions in window group

    tmux new -s session-A # A
    tmux new -s session-B -t session A

Alternatively, use wemux (more features, more complexity)


### Broadcast Input

* broadcast keyboard input to multiple panes. I use it extensively when I want to type the same bunch of commands into multiple console sessions. When multiple panes are open : map to  `C-a C-x`

    bind -n C-x setw synchronize-panes

Start multiple sessions with broadcast input

    tmux kill-session -t $SESSION 2> /dev/null || :
    tmux new-session -d -s $SESSION 2>/dev/null

    # add tiles and ssh sessions
    zbx-get-proxies | while read host; do
                echo -n "Connecting to host $host :"
        tmux split-window -v -t $SESSION "ssh -p 22  ${host/monitoring\./} || sleep 30000"
        tmux select-layout tiled
    done

    tmux set-window-option synchronize-panes on
    # kill first pane (shell where startet from)
    tmux kill-pane -t 0
    tmux attach -t $SESSION

### Plugins
* see [Status Messages in screen](http://www.linuxjournal.com/article/10950): new Mail
* see [https://github.com/tmux-plugins]
* continuum status in tmux status line
* tmux-resurrect
* tmux-copycat - a plugin for regex searches in tmux and fast match selection
* tmux-yank - enables copying highlighted text to system clipboard
* tmux-open - a plugin for quickly opening highlighted file or a url
