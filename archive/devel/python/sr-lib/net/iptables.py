#!/usr/bin/env python
# -*- coding: utf-8 -*-
#vim:fdm=marker
# unlock vim folding via zR, zo and lock folding via zM, zc
#----------------------------------------------------------------------------
"""                                                                     
DESCRIPTION    iptables python wrapper                        {{{1

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
    'IptablesError',
    'Error',
    'iptables'
]

# standard
import logging
log = logging.getLogger( __name__ )


# extra modules
from pt.run import Run, RunError, InitError

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class Error(BaseException):
    """Base class for module errors"""
class IptablesError(Error):
    """Error executing iptables command"""

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------

IPTABLES_EXE = "/sbin/iptables"

def iptables( args ):
    """args: array or string containing arguments """

    if type( args ) == type( [] ):
        args = ' '.join(args)

#    log.debug( "Running '%s %s'" % ( IPTABLES_EXE, args) )

    last_line = ""
    try: 
        for line in Run( IPTABLES_EXE + ' ' + args ):
            if "Permission denied (you must be root)" \
            or 'Operation not permitted' in line:
                raise IptablesError(
                    "Permission denied (you must be root)[3]"
                )
            yield line
    except RunError, emsg:
        try:
            raise IptablesError(
                "Error running iptables:\n%s\n%s" % (line ,emsg)
            )
        except UnboundLocalError:
            raise IptablesError(
                "Error running iptables:\n%s" % emsg
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
        name         = None , # __name__ or self.__class__.__name__ 
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )
    for line in iptables( "-L"):
        print line
