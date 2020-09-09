#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""                                                                     
DESCRIPTION    Process listing tools
               * listProcChilds)() list all child processes 
                 for given process
               * listProcs()  list all processes currently running

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
    'listProcChilds',
    'listProcs',
    'ProcessListError',
]

# standard
import os
import logging
log = logging.getLogger( __name__ )

from pt.data import validate

#----------------------------------------------------------------------------
# error classes                                                          {{{1
#----------------------------------------------------------------------------
class ProcessListError(BaseException):
    """Error listing processes"""

#----------------------------------------------------------------------------
# main class                                                             {{{1
#----------------------------------------------------------------------------

def listProcChilds( ppid ):
    """
    Return a list if all children processes for a given process
    """
    ppid = validate.is_integer( ppid )

    # collect all processes and it's childs
    pids_ppids = []
    pid_exists = False
    for entry in listProcs():
        pids_ppids.append( [ entry['ppid'], entry['pid'] ]  )
        if entry['pid'] == ppid:
            pid_exists = True

    if not pid_exists:
        raise ProcessListError( "Process pid '%d' not found!" % ppid)

    # iterate over all childs, yield process numbers
    res = []
    for pid in _recurse( ppid, pids_ppids ):
        res.append( pid )
    return res


def _recurse( ppid, pids_ppids ):
    """ Iterate over all processes and it's childs """
    yield ppid
    pids = _filterChilds( ppid, pids_ppids )
    for pid in pids:
        for pid in _recurse( pid, pids_ppids):
            yield pid


def _filterChilds( ppid, pids_ppids ):
    """ Filter all childs for given process """
    for ( parent, child ) in pids_ppids:
        if parent == ppid:
            yield child


def listProcs():
    """     
    Read all processes currently running from /proc/<process>/stat like
    'ps' does, store some parameters for lter use.
            
    EXAMPLE:
    >>> for entry in listProcs():
    >>>    print entry['pid'], entry['ppid'] 
    """

    PROC_DIR = "/proc"

    for entry in os.listdir( PROC_DIR ):
        try:
            validate.is_integer(entry,0)
        except validate.VdtTypeError:
            continue

        fh = open( PROC_DIR + os.sep + entry + os.sep + 'stat', 'r') 
        stat = fh.readline().split()
        fh.close()
        yield {
            'pid'       : validate.is_integer( stat[0 ], 0 ),
            'ppid'      : validate.is_integer( stat[3 ], 0 ), 
            'pgrp'      : validate.is_integer( stat[4 ] ,0 ), 
            'threads'   : validate.is_integer( stat[19], 1 ),
            'nice'      : validate.is_integer( stat[18], -19, 20) ,
            'exe'       : stat[1 ].strip('(').strip(')'),
        } 



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

    pid="3247"
#    for entry in listProcs():
#        print entry
    print listProcChilds( pid )
