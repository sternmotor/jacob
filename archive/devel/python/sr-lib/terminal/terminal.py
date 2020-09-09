#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 DESCRIPTION  contains class Output with methods for terminal output
 
 USAGE        
              see class docstring
 CHANGELOG    
    10-01-27    * only getsize and isfance functions left, no class
    09-09-23    * split out simple print functions from terminal.py
    09-06-26    * creation

 TODO
 
 THANKS TO

"""
 
__version__ = "$Revision: 0.1.2010-08-03 $"
# $Source$



__all__ = [
    'isTerminal',
    'terminalSize',
    'TerminalError',
    'colorsOn', 
    'colorsOff',
    'NORMAL', 'BOLD', 'REVERSE', 'ALARM',
    'ONBLACK', 'ONGREY', 'ONRED', 'ONGREEN', 
    'ONYELLOW', 'ONBLUE', 'ONPURPLE', 'ONCYAN',
    'RED', 'GREEN', 'YELLOW', 'BLUE', 'PURPLE', 'CYAN',     
    'fail_msg',
    'warn_msg',
    'pass_msg',
    'info_msg',
]

# libs for calculating terminal size
import sys
import os


#------------------------------------------------------------------------------
# error class
#------------------------------------------------------------------------------
class TerminalError(Exception):
    pass

#------------------------------------------------------------------------------
# terminal functions
#------------------------------------------------------------------------------
def isTerminal():
    """return True, True if there's a tty for stdout, stderr"""
    # If the stream isn't a tty, then assume it has no capabilities.

    return ( sys.stdout.isatty(), sys.stderr.isatty() )

def terminalSize():
    from fcntl   import ioctl
    from termios import TIOCGWINSZ
    from struct  import unpack

    def ioctl_GWINSZ(fd):
        try:
            cr = unpack('hh', ioctl(fd, TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (env['LINES'], env['COLUMNS'])
        except:
            cr = (25, 79)
    cols = int(cr[1])
    rows = int(cr[0])
    return( cols, rows )


#----------------------------------------------------------------------------
def colorsOn():
#----------------------------------------------------------------------------
    # define colors (must not be placed before "if colors ..."
    global NORMAL   
    global BOLD     
    global REVERSE  
    global ALARM
    global ONBLACK  
    global BLACK
    global ONGREY   
    global RED      
    global GREEN    
    global YELLOW   
    global BLUE     
    global PURPLE   
    global CYAN     
    global ONRED    
    global ONGREEN  
    global ONYELLOW 
    global ONBLUE   
    global ONPURPLE 
    global ONCYAN   

    NORMAL   = '\033[0m'
    BOLD     = '\033[1m'
    REVERSE  = '\033[7;3m'
    ALARM    = '\033[41m\033[1;37m'
    ONBLACK  = '\033[40m'
    ONGREY   = '\033[47m'
    RED      = '\033[31m'
    BLACK    = '\033[30m'
    GREEN    = '\033[32m'
    YELLOW   = '\033[1;33m'
    BLUE     = '\033[34m'
    PURPLE   = '\033[35m'
    CYAN     = '\033[36m'
    ONRED    = '\033[41m'
    ONGREEN  = '\033[42m'
    ONYELLOW = '\033[43m'
    ONBLUE   = '\033[44m'
    ONPURPLE = '\033[45m'
    ONCYAN   = '\033[46m'


#----------------------------------------------------------------------------
def colorsOff():
#----------------------------------------------------------------------------
    global NORMAL   
    global BOLD     
    global REVERSE  
    global ALARM
    global ONBLACK  
    global ONGREY   
    global BLACK
    global RED      
    global GREEN    
    global YELLOW   
    global BLUE     
    global PURPLE   
    global CYAN     
    global ONRED    
    global ONGREEN  
    global ONYELLOW 
    global ONBLUE   
    global ONPURPLE 
    global ONCYAN   

    NORMAL   = ''
    BOLD     = ''
    REVERSE  = ''
    ALARM    = ''
    ONBLACK  = ''
    BLACK    = ''
    ONGREY   = ''
    RED      = ''
    GREEN    = ''
    YELLOW   = ''
    BLUE     = ''
    PURPLE   = ''
    CYAN     = ''
    ONRED    = ''
    ONGREEN  = ''
    ONYELLOW = ''
    ONBLUE   = ''
    ONPURPLE = ''
    ONCYAN   = ''


#------------------------------------------------------------------------------
# flush buffers, colors on off
#------------------------------------------------------------------------------

# aquire info about console capabilities
std_fancy, err_fancy = isTerminal()

# set colors
if std_fancy or err_fancy :
    colorsOn()
else:
    colorsOff()


def _write_message(left, text, right, color, channel):
    """
    Print formatted message, helper for fail_msg|warn|ok
    """
    if not text:
        string = ''

    else:
        term_size = terminalSize()[0]
        text_size = len(left) + len(text) + len(right) + 3  
        # the trick here is int() to get number of full lines
        # looks dumb but i got bad results using modulo operator
        fill_size = term_size - ( text_size - int( text_size / term_size ) * term_size )
        if term_size == text_size:
            fill_size = 0
        
        if fill_size > 3:
            fill_string = "."
        else:
            fill_string = ' '

        string = "%s %s %s %s" % (
            color + left + NORMAL,
            text,
            color + fill_string * fill_size + NORMAL,
            color + right + NORMAL,
        )
    channel.write( "%s\n" % string)
    
        
def info_msg(text):
    _write_message( "INFO", text, "INFO", NORMAL, sys.stdout )
def pass_msg(text):
    _write_message( "[OK]", text, "[OK]", GREEN, sys.stdout )
    sys.stdout.write('\n')
def warn_msg(text):
    _write_message( "[WW]", text, "[WW]", YELLOW, sys.stderr )
    sys.stderr.write('\n')
def fail_msg(text):
    _write_message( "[EE]", text, "[EE]", RED, sys.stderr )
    sys.stderr.write('\n')
    


# flush output buffers
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

if __name__ == '__main__':
    fail_msg( "error" )
    warn_msg( "error" )
    info_msg( "error" )
    pass_msg( "error" )

    text="""Bad exit code [23] running '/usr/bin/rsync --acls --archive --checksum --delete-during --delete-excluded --devices --hard-links --human-readable --itemize-changes --links --modify-window=20 --numeric-ids --omit-dir-times --partial --progress --protect-args --recursive --sparse --specials --stats --verbose --verbose --xattrs -e "/usr/bin/ssh  -p 22 -o 'Compression no' -q -c arcfour,blowfish-cbc,aes192-cbc" 'backup1.bb:/etc/ssl' '/tmp''"""

    pass_msg( text )
