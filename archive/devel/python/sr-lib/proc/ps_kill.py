#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""                                                                     
DESCRIPTION    Process killing tools
               * softKill() : try to remove process and childs nicely
               * hardKill() : try to remove process and childs with SigKill
               * softKillSingle, hardKillSingle do this with one process
               only, leaving Childs alone

USAGE          see __doc__ strings or test section for example use
      
TODO
"""
#----------------------------------------------------------------------------
# module handling
#----------------------------------------------------------------------------

__version__ = "$Revision: 0.2.2011-02-09 $"
# $Source$

# module export
__all__ = [
    'softKill',
    'hardKill',
    'softKillSingle',
    'hardKillSingle',
    'ProcessKillError',
]

# standard modules
import time
import os
import signal
import logging
log = logging.getLogger( __name__ )

# extra modules
from pt.data import validate
from pt.proc import ps_list


# delay between kill attempts (seconds)
DELAY = 0.2   # seconds
TIMEOUT  = 2        # seconds

#----------------------------------------------------------------------------
# Error classes                                                          {{{1
#----------------------------------------------------------------------------
class ProcessKillError(BaseException):
    """Error killing process(es)"""

class ProcessKillTimeoutError(ProcessKillError):
    """Timeout killing process(es)"""
#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------

def softKill(ppid, timeout=TIMEOUT, delay=DELAY):
    """Try to remove process and childs via SIGTERM"""
    _kill( ppid, timeout, delay, False) 


def hardKill(ppid, timeout=TIMEOUT, delay=DELAY):
    """Try to remove process and childs via SIGKILL""" 
    _kill( ppid, timeout, delay, True) 

def _kill( ppid, timeout=TIMEOUT, delay=DELAY, hard=False ):

    pids = ps_list.listProcChilds( ppid )
    pids.reverse()
    timeouts = []
    for pid in pids:
        try: 
            _killSingle( pid, timeout, delay, hard )
        except ProcessKillTimeoutError, emsg:
            log.debug( "Timeout killing process '%s'" % proc )
            timeouts.append( proc )

    if len(timeouts) > 0:
        raise ProcessKillError(
            "Timeouts killing process(es) %s"
            % ', '.join( [ "%s" % timeout for timeout in timeouts ])
        )

def softKillSingle( pid, timeout=TIMEOUT, delay=DELAY ):
    _killSingle( pid, timeout, delay, False )
    
    
def hardKillSingle( pid, timeout=TIMEOUT, delay=DELAY ):
    _killSingle( pid, timeout, delay, True  )


def _killSingle( pid, timeout, delay, hard ):
    """Try to remove single process, hard or soft"""

    # check user input
    try: 
        pid = validate.is_integer( pid, 1 )
    except validate.ValidateError:
        raise ProcessKillError(
            "Error: pid must be integer > 1, got '%s'" % pid
        )
    try: 
        pid = validate.is_integer( pid, 1 )
    except validate.ValidateError:
        raise ProcessKillError(
            "Error: pid must be integer > 1, got '%s'" % pid
        )
    try: 
        timeout =  validate.is_float( timeout, 0, 10000)
    except validate.ValidateError:
        raise ProcessKillError(
            "Error: timeout must be number > 0 and < 10000, got '%s'" % timeout
        )
    try: 
        delay   =  validate.is_float( delay, 0, 10000)
    except validate.ValidateError:
        raise ProcessKillError(
            "Error: pid must be number > 0 and < 10000, got '%s'" % delay
        )

    # wording for debug messages an exceptions
    description = hard and "hard" or "soft"
    Description = hard and "Hard" or "Soft"
    my_signal = hard and signal.SIGKILL or signal.SIGTERM

    retries = int( ( timeout / delay ) + 0.5 )

    try:
        for retry in range(1, retries + 1 ):
            log.debug(  
                "%s - killing pid '%d', try %2d/%2d " 
                % (Description, pid, retry, retries )
            )
            os.kill(pid, my_signal)
            time.sleep( delay )
    except OSError, emsg:
        if "No such process" in str(emsg):
            log.debug( "Z's dead, Baby: there is no more '%s' " % pid )
            return True
        else:
            pass

    raise ProcessKillTimeoutError(
        "Maximum tries %s - killing process '%s' reached " 
        " (Tried %s times, delay %s seconds each try)"
        % (description, pid, retries, delay)
    )
    


#----------------------------------------------------------------------------
# tests and example invocation                                           {{{1
#----------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

    # initialize logger
    log = pt.logger.Logger(
#        style = "plain",
        #name         = __name__ , # __name__ or self.__class__.__name__ 
        name         = None , # None = root logger
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )

    pid=6037
    hardKill( pid, timeout ="2", delay = 0.2 )
