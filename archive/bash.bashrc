# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
    [ -z "$PS1" ] && return

#------------------------------------------------------------------------------
# bash console settings
#------------------------------------------------------------------------------

# enable history appending instead of overwriting.
    shopt -s histappend   
# disable shell ! events
    set   +H 
# enable checkwinsize so that bash will check the terminal size 
    shopt -s checkwinsize
# check hashed commands before searching all path
    shopt -s checkhash
# allow less to view *.gz etc. files
    [ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"
# enable single-tab completions
    set show-all-if-ambiguous on    

# make bash autocomplete with up arrow. move arrow left-right 
# and up/down again to see the whole story.
    bind '"\e[5~":history-search-backward'  
    bind '"\e[6~":history-search-forward'  

# make tab cycle through commands instead of listing  
    # bind '"\t":menu-complete'

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "${debian_chroot:-}" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color|*-256color) _COLORS=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
_FORCE_COLORS=yes

if [ -n "$_FORCE_COLORS" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	_COLORS=yes
    else
	_COLORS=
    fi
fi

# PROMPT DEFINITION


if [ "$_COLORS" = yes ]; then
    NORMAL="\[\033[0;0m\]"
    BOLD="\[\033[1m\]"
    REVERSE="\[\033[7;3m\]"
    FG="\[\033[0;0m\]"
    ON_BLACK="\[\033[40m\]"
    CYAN="\[\033[34;1m\]"
    GREEN="\[\033[32;1m\]" 
    GREY="\[\033[37m\]"
    PURPLE="\[\033[35m\]"
    RED="\[\033[31m\]"
fi
PROMPT_COMMAND=__prompt_command # Func to gen PS1 after CMDs

__prompt_command() {
    local EXIT="$?"             # This needs to be first

    if [ $EXIT != 0 ]; then
        PS1="${RED}${debian_chroot:+($debian_chroot)}\u@\h${NORMAL}:\w ${RED}[$EXIT]${NORMAL} \$ "
    else
        PS1="${GREEN}${debian_chroot:+($debian_chroot)}${GREEN}\u@\h${NORMAL}:\w \$ "    #${CYAN}\w${NORMAL} \$ "
    fi
    # \a : an ASCII bell character (07)
    # \d : the date in "Weekday Month Date" format (e.g., "Tue May 26")
    # \e : an ASCII escape character (033)
    # \h : the hostname up to the first '.'
    # \H : the hostname
    # \j : the number of jobs currently managed by the shell
    # \l : the basename of the shell’s terminal device name
    # \n : newline
    # \r : carriage return
    # \s : the name of the shell, the basename of $0 (the portion following
    #      the final slash)
    # \t : the current time in 24-hour HH:MM:SS format
    # \T : the current time in 12-hour HH:MM:SS format
    # \@ : the current time in 12-hour am/pm format
    # \A : the current time in 24-hour HH:MM format
    # \u : the username of the current user
    # \v : the version of bash (e.g., 2.00)
    # \V : the release of bash, version + patch level (e.g., 2.00.0)
    # \w : the current working directory, with $HOME abbreviated with a tilde
    # \W : the basename of the current working directory, with $HOME
    #      abbreviated with a tilde
    # \! : the history number of this command
    # \# : the command number of this command
    # \$ : if the effective UID is 0, a #, otherwise a $
    # \nnn : the character corresponding to the octal number nnn
    # \\ : a backslash
    # \[ : begin a sequence of non-printing characters, which could be
    #      used to embed a terminal control sequence into the prompt
    # \] : end a sequence of non-printing characters

}

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    alias minicom='minicom -c on'
    alias less='less -QR'
else
    alias ls='ls --classify'
fi

# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# some more ls aliases
alias ll='ls -l --human-readable'
alias la='ls -l --human-readable --almost-all'
alias ..='cd ..'
alias ...='..;..'
alias ....='..;..;..'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# cleanup
