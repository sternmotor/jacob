Shell command line usage
========================

# Bash command line

Navigation and editing

* `Ctrl + a`: jump to the start of the line
* `Ctrl + c`: terminate the command
* `Ctrl + d`: delete from under the cursor
* `Ctrl + e`: jump to the end of the line
* `Ctrl + k`: delete to EOL
* `Ctrl + l`: clear the screen
* `Ctrl + r`: search the history backwards
* `Ctrl + u`: delete backward from cursor
* `Ctrl + w`: delete backward a word
* `Ctrl + x` : move between EOL and current cursor position
* `Ctrl + z`: suspend/stop the command

History: edit `/etc/bash.bashrc` respectively `~/.bashrc`

* pre-populate history with commands used offenly (via script)

    history -s ssh host1
    history -s ssh host2
    history -s ssh host3
    history -s ssh host4

* enable history appending instead of overwriting.

    shopt -s histappend   

* make bash autocomplete with up arrow. move arrow left-right and up/down again
  to see the whole story

    bind '"\e[5~":history-search-backward'  
    bind '"\e[6~":history-search-forward'  

* append every command of every session to history instantly
TODO
* add time/date info to history 
TODO
* read history with time and date info
TODO
