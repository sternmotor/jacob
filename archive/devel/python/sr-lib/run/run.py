#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    shell self.cmd handler using pexpect for timeout and
               unbuffered output handling {{{1

USAGE          see __doc__ strings or test section for example use
      
CHANGELOG    
   10-02-12    * creation, copied from fstools.py

TODO

THANKS TO

"""

__version__ = "$Revision: 0.1.2010-02-12 $"
# $Source$


#----------------------------------------------------------------------------
# modules import, constants                                              {{{1
#----------------------------------------------------------------------------

# module export
__all__ = [
    'Run',
    'Error',
    'InitError',
    'RunError',
]

# standard
import os
import logging
log = logging.getLogger( __name__ )

# extra modules
import pexpect
from pt.data import validate


#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """Base class for module errors"""
class InitError(Error):
    """Error during initialisation of self.cmd"""
class RunError(Error):
    """Error during execution of self.cmd"""
class LockError(Error):
    """Error creating or reading lock file (where pid is stored)"""


class Run():
    """
    START self.cmd
    (1) Start self.cmd in a one-liner, do not return output handler
         error_code = Run("ls /etc")
    (2) Start command, store pid file (allow stop of command
        rh = Run( lockfile="/var/run/cmd.lock", timeout = None )
        for line in rh.start( "ls /etc" ):
            print line
        error_code = rh.error_code
        pid        = rh.pid
    
    STOP self.cmd
    run.stop()
    Run.stop(lockfile="/var/run/cmd.lock")
    """
    def __init__(self, cmd = None, timeout=None, lock_file=None, iterator=None):
        """Set up run environment"""

        # check parameters
        self.timeout    = timeout   and validate.is_integer(timeout, 0) or None
        self.lock_file  = lock_file and validate.is_string( lock_file ) or None
        self.pid        = os.getpid() 
    
        if cmd is not None:
            # Start command immediately
            self.cmd = self.fix_cmd_string( cmd )

            # yield and return are not alloewd here
            for line in self._pexpect():
                log.debug( line )

    def debug(self, cmd):
        for line in self.start(cmd):
            log.debug(line)

    def start(self, cmd):
        """Start command, return iterator, create lockfile"""

        self.cmd = self.fix_cmd_string( cmd )

#        if self.lock_file is None:
#            log.debug(
#                "Lockfile is not defined, stop function will not work"
#            )

        # initate command
        out = self._pexpect()

        # store pid to pidfile, setup up removal at script exit

        # run command
        for line in out:
            if line is not None: 
                yield line

        # make sure pid file is gone after successful finish

#    def stop( self, pidfile = None ):
#        pf = 
#        if pidfile is None and self

    def fix_cmd_string( self, cmd ):
        """ Turn cmd array to string, check type """

        # check input
        if cmd is None or cmd == '':
            raise InitError(
                "Command handed over to start() is not defined or empty string"
            )

        # turn self.cmd array to string
        if type(cmd) is type([]):
            exe = cmd[0]
            args = []
            for arg in cmd[1:]:
                if arg.startswith('-') or arg == '*':
                    args.append( arg )
                else:
                    args.append(  '"%s"' % arg )
                    
            cmd = ' '.join( [exe] + args )
        # check parameters
        return cmd and validate.is_string( cmd ) or None


    def _pexpect(self):
        """Call executable via pexcept, store process pid chain"""

        self.exitcode = False

        log.debug( "Initialising system shell command string '%s'" % self.cmd )

        try:
            session = pexpect.spawn( self.cmd, timeout=self.timeout)
        except KeyboardInterrupt:
            raise InitError( "User break, exiting" )
        except pexpect.ExceptionPexpect, emsg:
            raise InitError( emsg )
    
        try:
            while True:
                out = session.readline()
                if out == '':
                    break
                else:
                    yield out.rstrip()
            session.close()
        except KeyboardInterrupt:
            raise RunError( "User break, exiting" )


        if session.exitstatus:
            self.exitcode = session.exitstatus
            raise RunError(
                "Bad exit code [%s] running '%s'" 
                % ( session.exitstatus, self.cmd )
            )
        else:
            self.exitcode = 0

        if session.signalstatus:
            self.signal = session.signalstatus
            raise RunError(
                "Received signal code [%s] running '%s'"
                % ( session.signalstatus, self.cmd )
            )
        else:
            self.signal = None
        log.debug( "Success running system self.cmd '%s'" % self.cmd )

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
        name         = __name__ , # __name__ or self.__class__.__name__ 
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )

#    Run( "ls /etc" )
#    run = Run("ls /etc")
#    run.call( "ls /etc")
    run=Run()
    lines = run.start( "ls")
    print run.pid
    for line in lines:
        print line
